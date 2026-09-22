class JackTokenizer:
    KEYWORDS = {
        "class", "constructor", "function", "method",
        "field", "static", "var",
        "int", "char", "boolean", "void",
        "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return",
    }

    SYMBOLS = "{}()[].,;+-*/&|<>=~"

    def __init__(self, source):
        self.source = source
        self.tokens = self.tokenize(source)
        self.current_index = -1

    def tokenize(self, source):
        tokens = []
        index = 0

        while index < len(source):
            char = source[index]

            if source[index:index + 2] == "//":
                index += 2

                while index < len(source) and source[index] != "\n":
                    index += 1

                continue

            if source[index:index + 2] == "/*":
                index += 2

                while (
                    index < len(source)
                    and source[index:index + 2] != "*/"
                ):
                    index += 1

                index += 2
                continue

            if char.isspace():
                index += 1
                continue

            if char in self.SYMBOLS:
                tokens.append(char)
                index += 1
                continue

            if char == '"':
                start = index
                index += 1

                while source[index] != '"':
                    index += 1

                index += 1
                tokens.append(source[start:index])
                continue

            start = index

            while (
                index < len(source)
                and not source[index].isspace()
                and source[index] not in self.SYMBOLS
                and source[index] != '"'
            ):
                index += 1

            tokens.append(source[start:index])

        return tokens

    def has_more_tokens(self):
        return self.current_index + 1 < len(self.tokens)

    def advance(self):
        if self.has_more_tokens():
            self.current_index += 1

    def current_token(self):
        return self.tokens[self.current_index]

    def token_type(self):
        token = self.current_token()    

        if token in self.KEYWORDS:
            return "keyword"
        elif token in self.SYMBOLS:
            return "symbol"
        elif token.isdigit():
            return "integerConstant"
        elif token.startswith('"') and token.endswith('"'):
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self):
        return self.current_token()

    def symbol(self):
        return self.current_token()

    def identifier(self):
        return self.current_token()

    def int_val(self):
        return int(self.current_token())

    def string_val(self):
        return self.current_token()[1:-1]

