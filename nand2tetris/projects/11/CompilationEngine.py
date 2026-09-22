class IndentedWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.indent_level = 0

    def write(self, text):
        for line in text.splitlines(keepends=True):
            stripped = line.lstrip()
            if stripped.startswith("</"):
                self.indent_level -= 1

            self.output_file.write("  " * self.indent_level + stripped)

            if stripped.startswith("<") and not stripped.startswith("</"):
                if "</" not in stripped:
                    self.indent_level += 1


class CompilationEngine:
    OPERATOR_COMMANDS = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq",
    }

    SEGMENTS = {
        "static": "static",
        "field": "this",
        "arg": "argument",
        "var": "local",
    }

    def __init__(self, tokenizer, symbol_table, vm_writer):
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
        self.label_counter = 0
        self.class_name = None

    def new_label(self, prefix):
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def escape_xml(self, token):
        return token.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def write_current_token(self):
        token_type = self.tokenizer.token_type()
        token = self.tokenizer.current_token()

        if token_type == "stringConstant":
            token = self.tokenizer.string_val()
        elif token_type == "integerConstant":
            token = str(self.tokenizer.int_val())

        token = self.escape_xml(token)
        self.output_file.write(f"<{token_type}> {token} </{token_type}>\n")

    def advance_and_write(self):
        self.tokenizer.advance()
        self.write_current_token()

    def current_token(self):
        return self.tokenizer.current_token()

    def peek_token(self):
        next_index = self.tokenizer.current_index + 1
        if next_index < len(self.tokenizer.tokens):
            return self.tokenizer.tokens[next_index]
        return None
    
    def compile_class(self):
        self.symbol_table.reset()
        self.tokenizer.advance()  # class
        self.tokenizer.advance()  # class name
        self.class_name = self.current_token()
        self.tokenizer.advance()  # {
        self.tokenizer.advance()

        while self.current_token() in {"static", "field"}:
            self.compile_class_var_dec()
            self.tokenizer.advance()

        while self.current_token() in {"constructor", "function", "method"}:
            self.compile_subroutine()
            self.tokenizer.advance()

    def compile_class_var_dec(self):
        kind = self.current_token()
        self.tokenizer.advance()
        type_name = self.current_token()
        self.tokenizer.advance()

        while self.current_token() != ";":
            name = self.current_token()
            self.symbol_table.define(name, type_name, kind)
            self.tokenizer.advance()
            if self.current_token() == ",":
                self.tokenizer.advance()

    def compile_subroutine(self):
        subroutine_kind = self.current_token()
        self.symbol_table.start_subroutine()
        if subroutine_kind == "method":
            self.symbol_table.define("this", self.class_name, "arg")
        self.tokenizer.advance()  # return type
        self.tokenizer.advance()  # subroutine name
        subroutine_name = self.current_token()
        self.tokenizer.advance()  # (
        self.tokenizer.advance()
        self.compile_parameter_list()
        self.tokenizer.advance()  # {
        self.tokenizer.advance()

        while self.current_token() == "var":
            self.compile_var_dec()
            self.tokenizer.advance()

        function_name = f"{self.class_name}.{subroutine_name}"
        local_count = self.symbol_table.var_count("var")
        self.vm_writer.write_function(function_name, local_count)

        if subroutine_kind == "constructor":
            field_count = self.symbol_table.var_count("field")
            self.vm_writer.write_push("constant", field_count)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        elif subroutine_kind == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements()

    def compile_parameter_list(self):
        while self.current_token() != ")":
            type_name = self.current_token()
            self.tokenizer.advance()
            name = self.current_token()
            self.symbol_table.define(name, type_name, "arg")
            self.tokenizer.advance()
            if self.current_token() == ",":
                self.tokenizer.advance()


    def compile_var_dec(self):
        self.tokenizer.advance()  # type
        type_name = self.current_token()
        self.tokenizer.advance()

        while self.current_token() != ";":
            name = self.current_token()
            self.symbol_table.define(name, type_name, "var")
            self.tokenizer.advance()
            if self.current_token() == ",":
                self.tokenizer.advance()
            

    def compile_statements(self):
        while self.current_token() in {
            "let", "if", "while", "do", "return"
        }:
            if self.current_token() == "let":
                self.compile_let()
            elif self.current_token() == "if":
                self.compile_if()
            elif self.current_token() == "while":
                self.compile_while()
            elif self.current_token() == "do":
                self.compile_do()
            elif self.current_token() == "return":
                self.compile_return()

            self.tokenizer.advance()

    def compile_do(self):
        self.tokenizer.advance()
        self.compile_subroutine_call()
        self.vm_writer.write_pop("temp", 0)

    def compile_subroutine_call(self):
        receiver = self.current_token()
        name = receiver
        implicit_argument_count = 0

        if self.peek_token() == ".":
            self.tokenizer.advance()
            self.tokenizer.advance()
            subroutine_name = self.current_token()
            receiver_kind = self.symbol_table.kind_of(receiver)
            if receiver_kind is not None:
                segment = self.SEGMENTS[receiver_kind]
                index = self.symbol_table.index_of(receiver)
                class_name = self.symbol_table.type_of(receiver)
                self.vm_writer.write_push(segment, index)
                name = f"{class_name}.{subroutine_name}"
                implicit_argument_count = 1
            else:
                name = f"{receiver}.{subroutine_name}"
        else:
            self.vm_writer.write_push("pointer", 0)
            name = f"{self.class_name}.{receiver}"
            implicit_argument_count = 1

        self.tokenizer.advance()
        self.tokenizer.advance()
        argument_count = self.compile_expression_list()
        self.vm_writer.write_call(
            name,
            argument_count + implicit_argument_count,
        )
        self.tokenizer.advance()

    def compile_let(self):
        # let varName = expression ;
        self.tokenizer.advance()
        name = self.current_token()
        kind = self.symbol_table.kind_of(name)
        segment = self.SEGMENTS[kind]
        index = self.symbol_table.index_of(name)

        self.tokenizer.advance()
        if self.current_token() == "[":
            self.vm_writer.write_push(segment, index)
            self.tokenizer.advance()
            self.compile_expression()
            self.vm_writer.write_arithmetic("add")
            self.vm_writer.write_pop("temp", 0)

            self.tokenizer.advance()
            self.tokenizer.advance()
            self.compile_expression()
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_pop("that", 0)
            return

        self.tokenizer.advance()
        self.compile_expression()
        self.vm_writer.write_pop(segment, index)

    def compile_while(self):
        expression_label = self.new_label("WHILE_EXP")
        end_label = self.new_label("WHILE_END")
        self.vm_writer.write_label(expression_label)

        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(end_label)
        
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_statements()
        self.vm_writer.write_goto(expression_label)
        self.vm_writer.write_label(end_label)

    def compile_return(self):
        self.tokenizer.advance()

        if self.current_token() != ";":
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)

        self.vm_writer.write_return()
        

    def compile_if(self):
        true_label = self.new_label("IF_TRUE")
        false_label = self.new_label("IF_FALSE")
        end_label = self.new_label("IF_END")

        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_expression()
        self.vm_writer.write_if(true_label)
        self.vm_writer.write_goto(false_label)
        self.vm_writer.write_label(true_label)
        
        self.tokenizer.advance()
        self.tokenizer.advance()
        self.compile_statements()

        next_index = self.tokenizer.current_index + 1
        has_else = (
            next_index < len(self.tokenizer.tokens)
            and self.tokenizer.tokens[next_index] == "else"
        )
        if has_else:
            self.vm_writer.write_goto(end_label)
            self.vm_writer.write_label(false_label)
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.compile_statements()
            self.vm_writer.write_label(end_label)
        else:
            self.vm_writer.write_label(false_label)


    def compile_expression(self):
        self.compile_term()

        while self.current_token() in {
            "+", "-", "*", "/", "&", "|", "<", ">", "="
        }:
            operator = self.current_token()
            self.tokenizer.advance()
            self.compile_term()
            if operator in {"*", "/"}:
                subroutine = "Math.multiply" if operator == "*" else "Math.divide"
                self.vm_writer.write_call(subroutine, 2)
            else:
                self.vm_writer.write_arithmetic(self.OPERATOR_COMMANDS[operator])

    def compile_expression_list(self):
        argument_count = 0

        if self.current_token() != ")":
            self.compile_expression()
            argument_count = 1

            while self.current_token() == ",":
                self.tokenizer.advance()
                self.compile_expression()
                argument_count += 1

        return argument_count

    def compile_term(self):
        token = self.current_token()

        if token in {"-", "~"}:
            self.tokenizer.advance()
            self.compile_term()
            command = "neg" if token == "-" else "not"
            self.vm_writer.write_arithmetic(command)
        elif token == "(":
            self.tokenizer.advance()
            self.compile_expression()
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "integerConstant":
            self.vm_writer.write_push("constant", self.tokenizer.int_val())
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "stringConstant":
            value = self.tokenizer.string_val()
            self.vm_writer.write_push("constant", len(value))
            self.vm_writer.write_call("String.new", 1)
            for character in value:
                self.vm_writer.write_push("constant", ord(character))
                self.vm_writer.write_call("String.appendChar", 2)
            self.tokenizer.advance()
        elif token in {"false", "null"}:
            self.vm_writer.write_push("constant", 0)
            self.tokenizer.advance()
        elif token == "true":
            self.vm_writer.write_push("constant", 0)
            self.vm_writer.write_arithmetic("not")
            self.tokenizer.advance()
        elif token == "this":
            self.vm_writer.write_push("pointer", 0)
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "identifier":
            name = self.current_token()
            if self.peek_token() in {".", "("}:
                self.compile_subroutine_call()
            elif self.peek_token() == "[":
                kind = self.symbol_table.kind_of(name)
                segment = self.SEGMENTS[kind]
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(segment, index)
                self.tokenizer.advance()
                self.tokenizer.advance()
                self.compile_expression()
                self.tokenizer.advance()
                self.vm_writer.write_arithmetic("add")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)
            else:
                kind = self.symbol_table.kind_of(name)
                segment = self.SEGMENTS[kind]
                index = self.symbol_table.index_of(name)
                self.vm_writer.write_push(segment, index)
                self.tokenizer.advance()
        else:
            raise NotImplementedError(f"term is not implemented: {token}")
