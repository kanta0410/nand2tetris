class SymbolTable:
    KINDS = {"static", "field", "arg", "var"}

    def __init__(self):
        self.reset()

    def reset(self):
        self.symbols = {}
        self.counts = {kind: 0 for kind in self.KINDS}

    def start_subroutine(self):
        self.symbols = {
            name: symbol
            for name, symbol in self.symbols.items()
            if symbol["kind"] in {"static", "field"}
        }
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, type_name, kind):
        if kind not in self.KINDS:
            raise ValueError(f"unknown kind: {kind}")

        self.symbols[name] = {
            "type": type_name,
            "kind": kind,
            "index": self.counts[kind],
        }
        self.counts[kind] += 1

    def var_count(self, kind):
        return self.counts[kind]
    
    

    def kind_of(self, name):
        symbol = self.symbols.get(name)
        return symbol["kind"] if symbol else None

    def type_of(self, name):
        symbol = self.symbols.get(name)
        return symbol["type"] if symbol else None

    def index_of(self, name):
        symbol = self.symbols.get(name)
        return symbol["index"] if symbol else None
