# VM変換器: メインプログラム
# .vm を読んで .asm (Hackアセンブリ) を書き出す

import os
import sys
import parser as p
import code_writer as cw


COMPARISON_COMMANDS = {"eq", "gt", "lt"}


def translate(input_path, output_path):
    """
    input_path(.vm)を読んで、1行ずつアセンブリに変換し、output_path(.asm)に書き出す。
    第2段階での追加点:
      - "C_ARITHMETIC" のとき、command(= p.arg1(line))が
        COMPARISON_COMMANDS(eq/gt/lt)に入っていたら cw.write_comparison(command, label_id) を使う。
        それ以外(add/sub/neg/and/or/not)は今まで通り cw.write_arithmetic(command)。
      - label_id は「eq/gt/ltが何回目の呼び出しか」を表すカウンタ。
        ループに入る前に label_id = 0 のように用意し、
        write_comparison を呼ぶたびに 1 増やす（呼んだ後に += 1 でよい）。
    """
    filename = os.path.splitext(os.path.basename(input_path))[0]
    lines = p.clean_lines(input_path)
    asm_blocks = []
    label_id = 0
    for line in lines:
        itype = p.command_type(line)
        if itype == "C_ARITHMETIC":
            command = p.arg1(line)
            # ここを埋める: commandがCOMPARISON_COMMANDSに入っているかで
            # write_comparison と write_arithmetic を使い分ける
            if command in COMPARISON_COMMANDS:
                asm_blocks.append(cw.write_comparison(command, label_id))
                label_id += 1
            else:
                asm_blocks.append(cw.write_arithmetic(command))
            pass
        elif itype == "C_PUSH":
            asm_blocks.append(cw.write_push(p.arg1(line), p.arg2(line), filename))
        elif itype == "C_POP":
            asm_blocks.append(cw.write_pop(p.arg1(line), p.arg2(line), filename))
        else:
            raise ValueError(f"Unknown command type: {itype}")
    with open(output_path, "w") as f:
        f.write("\n".join(asm_blocks))
    pass


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = input_path.replace(".vm", ".asm")
    translate(input_path, output_path)
