import sys

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def analyze(input_path, output_path):
    with open(input_path, encoding="utf-8") as input_file:
        source = input_file.read()

    tokenizer = JackTokenizer(source)

    with open(output_path, "w", encoding="utf-8") as output_file:
        engine = CompilationEngine(tokenizer, output_file)
        engine.compile_class()


if __name__ == "__main__":
    analyze(sys.argv[1], sys.argv[2])