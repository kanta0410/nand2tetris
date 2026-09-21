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
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = IndentedWriter(output_file)

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
        self.output_file.write("<class>\n")

        self.advance_and_write()
        self.advance_and_write()
        self.advance_and_write()
        self.tokenizer.advance()

        while self.current_token() in {"static", "field"}:
            self.compile_class_var_dec()
            self.tokenizer.advance()

        while self.current_token() in {"constructor", "function", "method"}:
            self.compile_subroutine()
            self.tokenizer.advance()

        self.write_current_token()

        self.output_file.write("</class>\n")

    def compile_class_var_dec(self):
        self.output_file.write("<classVarDec>\n")

        while self.current_token() != ";":
            self.write_current_token()
            self.tokenizer.advance()

        self.write_current_token()
        self.output_file.write("</classVarDec>\n")

    def compile_subroutine(self):
        self.output_file.write("<subroutineDec>\n")

        self.write_current_token()  # constructor/function/method
        self.advance_and_write()  # return type
        self.advance_and_write()  # subroutine name
        self.advance_and_write()  # (

        self.tokenizer.advance()
        self.compile_parameter_list()
        self.write_current_token()  # )

        self.output_file.write("<subroutineBody>\n")
        self.advance_and_write()  # {
        self.tokenizer.advance()

        while self.current_token() == "var":
            self.compile_var_dec()
            self.tokenizer.advance()

        self.compile_statements()

        self.write_current_token()  # }
        self.output_file.write("</subroutineBody>\n")
        self.output_file.write("</subroutineDec>\n")

    def compile_parameter_list(self):
        self.output_file.write("<parameterList>\n")

        while self.current_token() != ")":
            self.write_current_token()
            self.tokenizer.advance()

        self.output_file.write("</parameterList>\n")

    def compile_var_dec(self):
        self.output_file.write("<varDec>\n")
        
        while self.current_token() !=";":
            self.write_current_token()
            self.tokenizer.advance()
        
        self.write_current_token()
        self.output_file.write("</varDec>\n")
            

    def compile_statements(self):
        self.output_file.write("<statements>\n")

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

        self.output_file.write("</statements>\n")

    def compile_do(self):
        self.output_file.write("<doStatement>\n")

        self.write_current_token()  # do
        self.tokenizer.advance()
        self.compile_subroutine_call()
        self.write_current_token()  # ;

        self.output_file.write("</doStatement>\n")

    def compile_subroutine_call(self):
        self.write_current_token()  # subroutine or class/object name

        if self.peek_token() == ".":
            self.advance_and_write()  # .
            self.advance_and_write()  # subroutine name

        self.advance_and_write()  # (
        self.tokenizer.advance()
        self.compile_expression_list()
        self.write_current_token()  # )
        self.tokenizer.advance()

    def compile_let(self):
        self.output_file.write("<letStatement>\n")

        self.write_current_token()  # let
        self.tokenizer.advance()
        self.write_current_token()  # variable name

        self.tokenizer.advance()
        
        if self.current_token() == "[":
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_expression()
            self.write_current_token()  # ]
            self.tokenizer.advance()

        self.write_current_token()  # =
        self.tokenizer.advance()
        self.compile_expression()
        self.write_current_token()  # ;

        self.output_file.write("</letStatement>\n")

    def compile_while(self):
        self.output_file.write("<whileStatement>\n")

        self.write_current_token()  # while
        self.advance_and_write()  # (
        self.tokenizer.advance()
        self.compile_expression()
        self.write_current_token()  # )
        
        self.advance_and_write()  # {
        self.tokenizer.advance()
        self.compile_statements()
        self.write_current_token()  # }

        self.output_file.write("</whileStatement>\n")

    def compile_return(self):
        self.output_file.write("<returnStatement>\n")

        self.write_current_token()  # return
        self.tokenizer.advance()

        if self.current_token() != ";":
            self.compile_expression()

        self.write_current_token()  # ;

        self.output_file.write("</returnStatement>\n")
        

    def compile_if(self):
        self.output_file.write("<ifStatement>\n")

        self.write_current_token()  # if
        
        self.advance_and_write()  # (
        self.tokenizer.advance()
        self.compile_expression()
        self.write_current_token()  # )
        
        self.advance_and_write()  # {
        self.tokenizer.advance()
        self.compile_statements()
        self.write_current_token()  # }

        next_index = self.tokenizer.current_index + 1
        has_else = (
            next_index < len(self.tokenizer.tokens)
            and self.tokenizer.tokens[next_index] == "else"
        ) #トークン長が収まっていてelseきてたら↓
        if has_else:
            self.tokenizer.advance()
            self.write_current_token()
            
            self.advance_and_write()  # {
            self.tokenizer.advance()
            self.compile_statements()
            self.write_current_token()  # }

        self.output_file.write("</ifStatement>\n")

    def compile_expression(self):
        self.output_file.write("<expression>\n")

        self.compile_term()

        while self.current_token() in {
            "+", "-", "*", "/", "&", "|", "<", ">", "="
        }:
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_term()

        self.output_file.write("</expression>\n")

    def compile_expression_list(self):
        self.output_file.write("<expressionList>\n")

        if self.current_token() != ")":
            self.compile_expression()

            while self.current_token() == ",":
                self.write_current_token()
                self.tokenizer.advance()
                self.compile_expression()

        self.output_file.write("</expressionList>\n")

    def compile_term(self):
        self.output_file.write("<term>\n")

        token = self.current_token()

        if token in {"-", "~"}:
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_term()
        elif token == "(":
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_expression()
            self.write_current_token()  # )
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "identifier":
            if self.peek_token() == "[":
                self.write_current_token()
                self.advance_and_write()  # [
                self.tokenizer.advance()
                self.compile_expression()
                self.write_current_token()  # ]
                self.tokenizer.advance()
            elif self.peek_token() in {".", "("}:
                self.compile_subroutine_call()
            else:
                self.write_current_token()
                self.tokenizer.advance()
        else:
            self.write_current_token()
            self.tokenizer.advance()

        self.output_file.write("</term>\n")
