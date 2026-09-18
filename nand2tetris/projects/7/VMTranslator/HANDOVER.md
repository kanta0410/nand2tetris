# nand2tetris プロジェクト7 引き継ぎ

## 進捗

`7/VMTranslator/`にVM変換器(VM→Hackアセンブリ)を実装完了。5テスト全部クリア済み。

- ✅ ①StackArithmetic/SimpleAdd
- ✅ ②StackArithmetic/StackTest（eq/gt/ltのラベル一意性問題も解決済み）
- ✅ ③MemoryAccess/BasicTest（local/argument/this/that/temp対応）
- ✅ ④MemoryAccess/PointerTest（pointer対応）
- ✅ ⑤MemoryAccess/StaticTest（static対応、write_push/write_pop両方完成）

プロジェクト7は完全終了。**次はプロジェクト8**（ProgramFlow: goto/if-goto/label、
FunctionCalls: function/call/return）に進む。

## ファイル構成

```
7/VMTranslator/
  parser.py       完成（command_type, arg1, arg2）
  code_writer.py  完成（write_push_constant, write_arithmetic, write_comparison,
                        write_push, write_pop 全部実装済み、8segment対応）
  main.py         完成
```

## 次にやること

プロジェクト8開始。`8/ProgramFlow`と`8/FunctionCalls`のディレクトリ構成を確認し、
新しいVMコマンド（`label`, `goto`, `if-goto`, `function`, `call`, `return`）を
このVMTranslatorに追加していく。進め方は7と同じく、テストの難易度順に
段階的に実装→検証のサイクル。

## 検証コマンド

```bash
cd /home/kanta/project/nand2tetris/nand2tetris/projects/7/VMTranslator
python3 main.py ../MemoryAccess/StaticTest/StaticTest.vm

cd /home/kanta/project/nand2tetris/nand2tetris/tools
java -Djava.awt.headless=true -classpath "bin/classes:bin/lib/Hack.jar:bin/lib/HackGUI.jar:bin/lib/Simulators.jar:bin/lib/SimulatorsGUI.jar:bin/lib/Compilers.jar" \
  CPUEmulatorMain "/home/kanta/project/nand2tetris/nand2tetris/projects/7/MemoryAccess/StaticTest/StaticTest.tst"
```
"Comparison ended successfully"が出ればOK。

GUIツール（VM Emulator等）はClaude Codeのサンドボックス内からは起動不可（X11に届かない）。
ユーザーの手元の通常ターミナルから`sh VMEmulator.sh`等で起動してもらう必要がある。

## 学習スタイル（重要）

- 「ボス」役として、雛形（ヒントコメント付き・中身は`pass`）を渡し、本人が埋める→動作確認、
  のサイクルで進めてきた。答えを先に書かず、まず考えさせる。
- ただし本人が疲れて「作りたくなくなった」場面が一度あった。そのときはコーチ役が
  巻き取って一気に動くところまで持っていき、達成感を優先する対応をした。
  ペースに応じてこの2モードを切り替える。
- 理解のために、抽象的な話をするときは必ず**具体的な数値でステップごとに追う**
  （例: SP=258, LCL=300のような実例でアセンブリを1行ずつ手計算する）のが本人に一番刺さった。
- 音声入力で使っているらしく、誤変換が頻発する（例:「添付」→temp、「リス」→LCL、
  「ホストとゲスト」は文脈と無関係だった等）。文意が通らない単語は文脈から推測して確認する。
- 詰まったら「シンプルに」「一言で」と要求されることが多い。長文よりも短い結論を先に。
- CPU Emulatorはこの環境でCLI実行可能（`-Djava.awt.headless=true`必須）。
  `.tst`を渡して`Comparison ended successfully`を見るのが検証の型として定着している。

## すでに理解済みの概念（再説明不要）

- VMコード＝アセンブリとJackの中間表現（本人曰く「仲介人」）
- スタック/セグメントは全部RAMという1枚の配列の中の「区画」に過ぎない
- SP=RAM[0], LCL=RAM[1], ARG=RAM[2], THIS=RAM[3], THAT=RAM[4]（可変の値を持つポインタ変数）
- `A`はRAMの番地指定、`M`は「Aが指す番地の中身」
- `AM=M-1`は1命令で2箇所に同時代入するテクニック
- push: 読み取り元計算→書き込み先(SP)は単純なので競合なし、一直線
- pop: 書き込み先を先に計算してR13に退避→スタックから読む(Dを使い回す)→
  `A=M`でAだけ復元して書く、という順序でないと退避が2回必要になり非効率
- temp/pointerは固定アドレス、local/argument/this/thatは間接参照（2段階）
- staticはVM変換器がシンボル名(`filename.index`)を作るだけで、番地割り当ては
  プロジェクト6のアセンブラに委任
