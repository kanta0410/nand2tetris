# Hack アセンブラ 基本版: メインプログラム
# .asm を読んで .hack (バイナリ)を書き出す

import sys
import parser as p
import code as c
import symbol_table as st


def first_pass(lines):
    """
    ラベルのアドレスを確定させる（1パス目）。
    PREDEFINED_SYMBOLSをコピーしたものをベースに、ラベルを追加して返す。
    ヒント:
      - table = dict(st.PREDEFINED_SYMBOLS) からコピーして始める
        （dict()でコピーしないと元のPREDEFINED_SYMBOLSまで書き換えてしまう）
      - 命令カウンタを0から始める（例: address = 0）
      - 各lineについて p.instruction_type(line) を見る
          "L" なら table[p.symbol(line)] = address を登録（addressは増やさない）
          それ以外なら address += 1 する
    """
    table = dict(st.PREDEFINED_SYMBOLS)
    address = 0
    for line in lines:
        if p.instruction_type(line) == "L":
            table[p.symbol(line)] = address ##ROMのアドレスを登録
        else:
            address += 1
    return table
        
    pass


def resolve_symbol(sym, table, next_var_addr):
    """
    A命令の中身(sym、文字列)を実際のアドレス(int)にする（2パス目で使う）。
    ヒント:
      - sym.isdigit() で「これは数字か」を判定できる
      - 数字ならそのまま int(sym) を返す
      - 数字じゃない場合、すでに table にあればその値を返す
      - table に無ければ、新しい変数として扱う：
          table[sym] = next_var_addr[0]
          next_var_addr[0] += 1
          として、割り当てた値を返す
        （next_var_addr はリスト [16] のような「箱」で渡ってくる。
          int同士だと関数の中で書き換えても外に反映されないので、
          リストに包んで中身を書き換える、という手を使う）
    """
    if sym.isdigit():
        return int(sym)
    elif sym in table:
        return table[sym]
    else:
        table[sym] = next_var_addr[0]  ##16から順にRAMの変数のアドレスを割り当てる
        next_var_addr[0] += 1
        return table[sym]
    pass


def assemble_a_instruction(line, table, next_var_addr):
    """
    A命令の行を16bitの2進数文字列にする。
    例: "@100" -> "0000000001100100"
    ヒント:
      - p.symbol(line) でシンボル・数値の文字列が取れる
      - resolve_symbol(sym, table, next_var_addr) で実際のアドレス(int)にする
      - 15bit分の2進数にする（Pythonの format か bin を調べてみる）
      - 先頭に "0" を1個くっつけて16bitにする
    """
    num10 = int(resolve_symbol(p.symbol(line), table, next_var_addr))
    num2=format(num10, "016b")
    return num2
    pass


def assemble_c_instruction(line):
    """
    C命令の行を16bitの2進数文字列にする。
    例: "D=M" -> "1111110000010000"
    ヒント:
      - p.dest(line), p.comp(line), p.jump(line) でそれぞれの文字列が取れる
      - c.DEST_TABLE, c.COMP_TABLE, c.JUMP_TABLE でビットに変換する
      - "111" + comp(7bit) + dest(3bit) + jump(3bit) の順で並べる
    """
    bdest=c.DEST_TABLE[p.dest(line)]
    bcomp=c.COMP_TABLE[p.comp(line)]
    bjump=c.JUMP_TABLE[p.jump(line)]
    return "111"+bcomp+bdest+bjump
    pass


def assemble(input_path, output_path):
    lines = p.clean_lines(input_path)
    table = first_pass(lines)
    next_var_addr = [16]

    binary_lines = []
    for line in lines:
        itype = p.instruction_type(line)
        if itype == "L":
            continue
        elif itype == "A":
            binary_lines.append(assemble_a_instruction(line, table, next_var_addr))
        else:
            binary_lines.append(assemble_c_instruction(line))

    with open(output_path, "w") as f:
        for b in binary_lines:
            f.write(b + "\n")


if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = input_path.replace(".asm", ".hack")
    assemble(input_path, output_path)
