# VM変換器: Parser モジュール
# .vmファイルを読んで、コメント/空行を除いたコマンドの並びにし、
# 各コマンドを種類判定・引数(arg1, arg2)に分解する

# プロジェクト7で登場する算術・論理コマンド一覧
ARITHMETIC_COMMANDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}


def clean_lines(filepath):
    """
    ファイルを読んで、コメントと空白を取り除いた行のリストを返す。
    ヒント: 6のparser.pyのclean_linesと全く同じロジックで書ける。
      - "//"より前の部分だけを残す（line.split("//")[0]）
      - strip()して、空行になったものは捨てる
    """
    return [line.split("//")[0].strip() for line in open(filepath) if line.split("//")[0].strip()]
    pass


def command_type(line):
    """
    1行を受け取り、コマンドの種類を文字列で返す。
    プロジェクト8では、まずlabelも登場する:
      "C_ARITHMETIC" : add, sub, neg, eq, gt, lt, and, or, not のどれか
      "C_PUSH"       : "push"で始まる行
      "C_POP"        : "pop"で始まる行
      "C_LABEL"      : "label"で始まる行
      "C_GOTO"       : "goto"で始まる行
      "C_IF"         : "if-goto"で始まる行
      "C_FUNCTION"   : "function"で始まる行
      "C_RETURN"     : "return"で始まる行
      "C_CALL"       : "call"で始まる行
    ヒント:
      - line.split() で空白区切りの単語リストにする
        （例: "push local 2" -> ["push", "local", "2"]）
      - 先頭の単語（words[0]）が "push" か "pop" ならそれぞれ返す
      - それ以外は ARITHMETIC_COMMANDS に入っているはずなので "C_ARITHMETIC"
    """
    words = line.split()
    if words[0] == "push":
        return "C_PUSH"
    elif words[0] == "pop":
        return "C_POP"
    elif words[0] == "label":
      # ここを埋める: label命令の種類名を返す
        return "C_LABEL"
    elif words[0] == "goto":
      # ここを埋める: goto命令の種類名を返す
        return "C_GOTO"
    elif words[0] == "if-goto":
        return "C_IF"
    elif words[0] == "function":
        return "C_FUNCTION"
        # ここを埋める: function命令の種類名を返す
        
    elif words[0] == "return":
        return "C_RETURN"
        # ここを埋める: return命令の種類名を返す
    elif words[0] == "call":
      # ここを埋める: call命令の種類名を返す
        return "C_CALL"
  
    elif words[0] in ARITHMETIC_COMMANDS:
        return "C_ARITHMETIC"
    pass


def arg1(line):
    """
    コマンドの1つ目の引数を返す。
      - C_ARITHMETIC の場合: コマンド自体の文字列（例: "add" -> "add"）
      - C_PUSH / C_POP の場合: セグメント名（例: "push local 2" -> "local"）
      - C_LABEL の場合: ラベル名（例: "label LOOP" -> "LOOP"）
    ヒント:
      - words = line.split() を使う
      - command_type(line) が "C_ARITHMETIC" なら words[0] を返す
      - そうでなければ words[1] を返す
    """
    if command_type(line) == "C_ARITHMETIC":
        return line.split()[0]
    elif command_type(line) == "C_RETURN":
      # ここを埋める: returnにはarg1がない
      pass
    else:
        return line.split()[1]
    pass


def arg2(line):
    """
    コマンドの2つ目の引数（index）をintで返す。C_PUSH/C_POPのときだけ呼ばれる想定。
    例: "push local 2" -> 2
    ヒント: words[2] を int() に通す。
    """
    if command_type(line) == "C_ARITHMETIC":
        return None
    else:
        return int(line.split()[2])
    pass
