import sys
from pathlib import Path

from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


def compile_file(input_path):
    input_path = Path(input_path)
    output_path = input_path.with_suffix(".vm")

    source = input_path.read_text(encoding="utf-8")
    tokenizer = JackTokenizer(source)
    symbol_table = SymbolTable()

    with output_path.open("w", encoding="utf-8") as output_file:
        vm_writer = VMWriter(output_file)
        engine = CompilationEngine(tokenizer, symbol_table, vm_writer)
        engine.compile_class()

    return output_path


def compile_path(input_path):
    input_path = Path(input_path)
    if input_path.is_dir():
        return [compile_file(path) for path in sorted(input_path.glob("*.jack"))]
    return [compile_file(input_path)]


if __name__ == "__main__":
    for output_path in compile_path(sys.argv[1]):
        print(output_path)
