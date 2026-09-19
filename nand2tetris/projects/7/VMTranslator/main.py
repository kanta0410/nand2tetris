# VM変換器: メインプログラム
# .vm を読んで .asm (Hackアセンブリ) を書き出す

import os
import sys
import parser as p
import code_writer as cw


COMPARISON_COMMANDS = {"eq", "gt", "lt"}


def collect_vm_files(input_path):
    """入力がVMファイルでもフォルダでも、変換するVMファイル一覧にする。"""
    if os.path.isdir(input_path):
        
        vm_files = [
        os.path.join(input_path, filename)
        for filename in os.listdir(input_path)
        if filename.endswith(".vm")
        ]
        return vm_files   
        
        
    return [input_path]


def translate(input_path, output_path, bootstrap=False):
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
    vm_files = collect_vm_files(input_path)
    asm_blocks = []
    if bootstrap:
        asm_blocks.append(cw.write_init())
    label_id = 0
    call_id = 0
    for vm_file in vm_files:
        # ここを埋める: vm_fileからファイル名だけ取り出す
        filename = os.path.splitext(os.path.basename(vm_file))[0]
        # ここを埋める: 現在のVMファイルをParserへ渡す
        lines = p.clean_lines(vm_file)
        for line in lines:
            itype = p.command_type(line)
            if itype == "C_ARITHMETIC":
                command = p.arg1(line)
                if command == "return":
                    pass
                # write_comparison と write_arithmetic を使い分ける
                if command in COMPARISON_COMMANDS:
                    asm_blocks.append(cw.write_comparison(command, label_id))
                    label_id += 1
                else:
                    asm_blocks.append(cw.write_arithmetic(command))
            elif itype == "C_PUSH":
                asm_blocks.append(cw.write_push(p.arg1(line), p.arg2(line), filename))
            elif itype == "C_POP":
                asm_blocks.append(cw.write_pop(p.arg1(line), p.arg2(line), filename))
            elif itype == "C_LABEL":
                # ここを埋める: ラベル名をCodeWriterへ渡して、生成したASMを追加する
                asm_blocks.append(cw.write_label(p.arg1(line)))
            elif itype == "C_GOTO":
                # ここを埋める: ジャンプ先のラベル名をCodeWriterへ渡して、生成したASMを追加する
                asm_blocks.append(cw.write_goto(p.arg1(line)))
            elif itype == "C_IF":
                # ここを埋める: ジャンプ先のラベル名をCodeWriterへ渡して、生成したASMを追加する
                asm_blocks.append(cw.write_if(p.arg1(line)))
            elif itype == "C_FUNCTION":
                # ここを埋める: 関数名とローカル変数の数をCodeWriterへ渡して、生成したASMを追加する
                asm_blocks.append(cw.write_function(p.arg1(line), p.arg2(line)))
            elif itype == "C_RETURN":
                # ここを埋める: return用のアセンブリをCodeWriterへ渡して追加する
                asm_blocks.append(cw.write_return())
            elif itype == "C_CALL":
                # ここを埋める: 関数名と引数個数をCodeWriterへ渡して追加する
                asm_blocks.append(cw.write_call(p.arg1(line), p.arg2(line), call_id))
                # ここを埋める: 次のcallで別の戻り先ラベルになるよう番号を進める
                call_id += 1
            else:
                raise ValueError(f"Unknown command type: {itype}")
    with open(output_path, "w") as f:
        f.write("\n".join(asm_blocks))


if __name__ == "__main__":
    input_path = sys.argv[1]
    if os.path.isdir(input_path):
        output_path = os.path.join(
            input_path,
            os.path.basename(os.path.normpath(input_path)) + ".asm",
        )
    else:
        output_path = input_path.replace(".vm", ".asm")
    bootstrap = "--bootstrap" in sys.argv[2:]
    translate(input_path, output_path, bootstrap)
