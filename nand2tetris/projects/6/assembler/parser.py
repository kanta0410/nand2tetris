# Hack アセンブラ: Parser モジュール
# .asmファイルを読んで、コメント/空行を除いた命令の並びにし、
# 各命令を種類判定・フィールド分解する


def clean_lines(filepath):
    """ファイルを読んで、コメントと空白を取り除いた行のリストを返す"""
    lines = []
    with open(filepath) as f:
        for raw_line in f:
            line = raw_line.split("//")[0].strip()
            if line:
                lines.append(line)
    return lines


def instruction_type(line):
    """
    1行を受け取り、"A"（A命令）か "C"（C命令）かを返す。
    （ラベル"L"は基本版では一旦考えなくてよい）
    ヒント: line[0] を見る
    """
    if line[0]== "@":
        return "A"
    elif line[0]== "(":  # ラベル
        return "L"
    else:
        return"C"
    pass


def symbol(line):
    """
    A命令 "@値" から、"@"を取り除いた中身（数値やシンボルの文字列）を返す。
    例: "@100" -> "100"
    """
    if line[0] == "@":
        line = line.split("@")[1].strip()
    elif line[0] == "(":
        line = line.split("(")[1].strip(")")
    return line

    pass


def dest(line):
    """
    C命令から dest部分を取り出す。"="が無ければ空文字列を返す。
    例: "AMD=D+A" -> "AMD"
    例: "0;JMP"   -> ""
    """
    if "=" in line:
        line = line.split("=")[0].strip()
        return line
    else: 
        return ''

    pass


def comp(line):
    """
    C命令から comp部分を取り出す（"="と";"を除いた計算式そのもの）。
    例: "AMD=D+A" -> "D+A"
    例: "0;JMP"   -> "0"
    """
    if "=" in line:
        line = line.split("=")[1].strip()
    if ";" in line:
        line = line.split(";")[0].strip()
    return line


def jump(line):
    """
    C命令から jump部分を取り出す。";"が無ければ空文字列を返す。
    例: "AMD=D+A" -> ""
    例: "0;JMP"   -> "JMP"
    """
    if ";" in line:
        line = line.split(";")[1].strip()
        return line
    else: 
        return ''
    pass
