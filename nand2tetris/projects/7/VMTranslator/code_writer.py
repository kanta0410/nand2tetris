# VM変換器: CodeWriter モジュール
# parserが分解したコマンド情報を受け取り、Hackアセンブリの文字列（複数行）を組み立てる
#
# 今回（第3段階）で対応するのは以下だけ:
#   算術・論理コマンド: add, sub, neg, and, or, not, eq, gt, lt
#   メモリアクセス:      push/pop constant, local, argument, this, that, temp
#                        ※pointer, static は次の段階

# local/argument/this/that は「ベースアドレスがこのレジスタに入っていて、
# そこからのオフセットでアクセスする」segment（4つとも同じ型で書ける）
SEGMENT_POINTER = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}


def write_push_constant(index):
    """
    "push constant N" のアセンブリを返す（複数行の文字列。改行区切り）。
    やること: Nを計算してDレジスタに入れ、スタックトップに書いて、SPを1つ進める。
    ヒント（テンプレート）:
      @N
      D=A
      @SP
      A=M
      M=D
      @SP
      M=M+1
    "\n".join([...]) で各行を組み立てて返すとよい。Nはf-stringで埋め込む。
    """
    return "\n".join([f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
    pass
    

def write_arithmetic(command):
    """
    算術・論理コマンド1つ分のアセンブリを返す（複数行の文字列）。
    対応するのは "add", "sub", "neg", "and", "or", "not" の6つ。

    考え方:
      - 2引数コマンド(add, sub, and, or)は共通の型:
          @SP
          AM=M-1     // SPを1減らし、そのアドレスを指す（2番目に積んだ値の場所）
          D=M        // Dに2番目の値を入れる
          A=A-1      // 1番目に積んだ値の場所を指す（SPは動かさない）
          M=??       // ここだけコマンドごとに変わる: D+M / M-D / D&M / D|M
      - 1引数コマンド(neg, not)は「1個の値を書き換えるだけ」なので、
        SPを動かさず、スタックトップ(@SP → A=M-1)を直接書き換えればよい:
          @SP
          A=M-1
          M=??       // neg なら -M、not なら !M

    ヒント:
      - コマンド名 -> 埋め込む演算子・式 の対応表を辞書で持っておくとif地獄にならない
        例: {"add": "D+M", "sub": "M-D", "and": "D&M", "or": "D|M"}
             {"neg": "-M", "not": "!M"}
      - command が2引数系(上の辞書のキーにある)か1引数系かで分岐し、
        該当するテンプレートに演算子を埋め込んで返す
    """
    two_arg_commands = {"add": "D+M", "sub": "M-D", "and": "D&M", "or": "D|M"}
    one_arg_commands = {"neg": "-M", "not": "!M"}
    template_two_arg = ["@SP", "AM=M-1", "D=M", "A=A-1", "M={op}"]
    template_one_arg = ["@SP", "A=M-1", "M={op}"]
    if command in two_arg_commands:
        op = two_arg_commands[command]
        return "\n".join([line.format(op=op) for line in template_two_arg])
    elif command in one_arg_commands:
        op = one_arg_commands[command]
        return "\n".join([line.format(op=op) for line in template_one_arg])
    pass


def write_comparison(command, label_id):
    """
    比較コマンド1つ分のアセンブリを返す（複数行の文字列）。
    対応するのは "eq", "gt", "lt" の3つ。

    考え方（3つとも同じ型で、ジャンプ命令だけ変わる）:
      @SP
      AM=M-1
      D=M        // D = 2番目に積んだ値(y)
      A=A-1
      D=M-D      // D = x - y
      @TRUE_{label_id}
      D;J??      // eqならJEQ, gtならJGT, ltならJLT
      @SP
      A=M-1
      M=0        // false(0)を書く
      @END_{label_id}
      0;JMP
      (TRUE_{label_id})
      @SP
      A=M-1
      M=-1       // true(-1)を書く
      (END_{label_id})

    ヒント:
      - label_id は「このeq/gt/ltが何回目の呼び出しか」を表す数値。
        呼び出すたびに違う数値が来る前提（＝ラベル名が毎回変わり、衝突しない）。
        カウンタの管理はこの関数の外（呼び出す側）でやる。
      - コマンド名 -> ジャンプ命令 の対応表を辞書で持つ:
          {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
      - 上のテンプレートを1つのリストにして、
        .format(jump=jump, id=label_id) のように複数の値を一度に埋め込める
        （書き方: "@TRUE_{id}" みたいに複数のプレースホルダーを混ぜてOK）
    """
    jump_commands = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
    jump = jump_commands[command]
    template = ["@SP",
        "AM=M-1",
        "D=M",
        "A=A-1",
        "D=M-D",
        "@TRUE_{id}",
        "D;{jump}",
        "@SP",
        "A=M-1",
        "M=0",
        "@END_{id}",
        "0;JMP",
        "(TRUE_{id})",
        "@SP",
        "A=M-1",
        "M=-1",
        "(END_{id})"]
    return "\n".join([line.format(jump=jump, id=label_id) for line in template])
    pass


def write_push(segment, index, filename=None):
    """
    "push segment index" のアセンブリを返す（複数行の文字列）。
    segmentは constant, local, argument, this, that, temp のどれか。

    3パターンに分かれる:
      1. segment == "constant" のとき: write_push_constant(index) をそのまま使えばよい
      2. segment == "temp" のとき: ベースアドレスは固定で5。
         5+index番地の中身を直接読んでスタックに積む:
           @{5+index}
           D=M
           @SP
           A=M
           M=D
           @SP
           M=M+1
      3. それ以外(local/argument/this/that)のとき: SEGMENT_POINTER[segment] で
         レジスタ名(LCL等)を引いて、ポインタ経由でアクセスする:
           @LCL          (← SEGMENT_POINTER[segment])
           D=M
           @{index}
           A=D+A
           D=M
           @SP
           A=M
           M=D
           @SP
           M=M+1
      4. segment == "static" のとき: シンボル名を "{filename}.{index}" にすればよい。
         あとは6のアセンブラが変数として勝手にRAM番地を割り当ててくれる:
           @{filename}.{index}
           D=M
           @SP
           A=M
           M=D
           @SP
           M=M+1

    ヒント:
      - if/elif/elseの4分岐で書く
      - テンプレートは "\n".join([...]) でOK。f-stringで index や
        SEGMENT_POINTER[segment], filename を埋め込む
    """
    if segment == "constant":
        return write_push_constant(index)
    elif segment == "pointer":
        target = "THIS" if index == 0 else "THAT"
        return "\n".join([f"@{target}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
    elif segment == "temp":
        return "\n".join([f"@{5+index}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
    elif segment == "static":
        return "\n".join([f"@{filename}.{index}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
    else:
        return "\n".join([f"@{SEGMENT_POINTER[segment]}", "D=M", f"@{index}", "A=D+A", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])


def write_pop(segment, index, filename=None):
    """
    "pop segment index" のアセンブリを返す（複数行の文字列）。
    segmentは local, argument, this, that, temp のどれか（constantのpopは存在しない）。

    2パターンに分かれる:
      1. segment == "temp" のとき: 書き込み先が固定アドレス(5+index)とわかっているので、
         popした値を直接そこに書けばよい（アドレス退避が不要、pushの逆）:
           @SP
           AM=M-1
           D=M
           @{5+index}
           M=D
      2. それ以外(local/argument/this/that)のとき: 書き込み先アドレスを先に計算して
         R13に退避してから、popした値をそこに書く:
           @LCL          (← SEGMENT_POINTER[segment])
           D=M
           @{index}
           D=D+A
           @R13
           M=D
           @SP
           AM=M-1
           D=M
           @R13
           A=M
           M=D
      3. segment == "static" のとき: tempと同じ発想（書き込み先が最初からわかってる）。
         popした値を直接 "{filename}.{index}" というシンボルの場所に書けばよい:
           @SP
           AM=M-1
           D=M
           @{filename}.{index}
           M=D

    ヒント: write_pushと同じ形。if/elifで分岐し、"\n".join([...])で組み立てる。
    """
    if segment == "pointer":
        target = "THIS" if index == 0 else "THAT"
        return "\n".join(["@SP", "AM=M-1", "D=M", f"@{target}", "M=D"])
    elif segment == "temp":
        return "\n".join(["@SP", "AM=M-1", "D=M", f"@{5+index}", "M=D"])
    elif segment == "static":
        return "\n".join(["@SP", "AM=M-1", "D=M", f"@{filename}.{index}", "M=D"])
    else:
        return "\n".join([f"@{SEGMENT_POINTER[segment]}", "D=M", f"@{index}", "D=D+A", "@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"])
    