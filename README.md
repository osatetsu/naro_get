# NARO_GET

## 概要

本ツール群は、[小説を読もう!]() / [小説家になろう]() ウェブサイトから任意の小説をダウンロードし、本文部分を結合した html ファイルを作成する。この結合した html ファイルは、kindle で読むことを意図している。

### 主な機能

* html 形式でのダウンロード
* 本文部分を結合した html ファイルの作成
* 結合(分割)の単位
    * 章
    * (未実装) 任意の話数、もしくは、ファイルサイズ。章立ての無い小説を、どこで区切るか。
* 空行の削除
* 目次の作成
* 横書き

結合(分割)は、単一の大きなファイルでは kindle での操作性が悪化するための措置である。ファイルが 500KiB くらいであれば、特に問題ないように見える。

### このツールに実装しないもの

 * epub 形式への変換
   * 悪用が怖いため実装しない。

 * eメールによる Send to Kindle
   * SMTPサーバーを用意したくない。見知らぬサーバーを経由させたいか？

 * 縦書き
   * 縦書きを利用したい場合は、[小説を読もう!]()公式機能の縦書きPDFを使用されたい。
   * 本ツールで非対応の理由は、英単語やルビの処理を共通にできないことから。例えば、英単語や数字を、回転させるのか縦中横にするのかなど。


## 事前に必要なもの

 * python 3.x
    * Windows 11 であれば、Microsoft store からインストールできる。

## 使用例

 1. [小説を読もう!]から、読みたい小説のNコードを調べる。
     1. 例えば https://ncode.syosetu.com/n6316bn/ であれば、n6316bn がNコードとなっている。
 2. `download.py Nコード` を実行する。
     1. Nコードは小文字とすること。
     2. 既定ではカレントディレクトリに `download/Nコード/` ディレクトリが作成され、そこへダウンロードしていく。
     3. すでにダウンロードしたファイル(話数)が存在した場合、ダウンロードはスキップする。
 3. `cat_html.py Nコード` を実行する。
     1. `download/Nコード.output/` ディレクトリが作成され、そこへ結合した html ファイルを出力する。
 4. [Send to Kindle]() を使用し、結合した html ファイルを Kindle ライブラリへ追加する。Amazon 側で変換処理がなされるため、少し時間がかかる。
 5. お手持ちの Kindle にて小説を読む。

## Tips

 1. Send to Kindle で送るファイルは、少数が良いかと思う。
    大量に送った場合、変換時間がかかること、および、Kindle で見つけにくいことから。
 2. 読み終わったファイルは Kindle ライブラリから削除していくと良いかと思う。
    大量のファイルに埋もれて、目的とする書籍を探し出しにくくなることから。
 3. 同一小説に対し `download.py` の実行頻度は、多くても1日1回程度が望ましい。
    更新頻度の高い小説でも1日1話が追加されるかどうかであるため。

## 免責事項 / 利用条件

  1. 本ツールは使用者の自己責任で使用すること。
  2. 小説の著作者、および、[小説を読もう!]()運営の権利や規約に則り使用すること。
  3. 本ツールは[小説を読もう!]()運営とは無関係である。本ツールに関し、そちらの運営企業への問い合わせはしないこと。
  4. 本ツールを使用することにより、[小説を読もう!]()サーバーへ、いたずらに負荷をかけないこと。
  5. 本ツールで作成したファイルは、使用者個人が楽しむことのみ利用可とする。商用利用、あるいは、公開は禁止とする。

- - -

## Appendix

 * [小説を読もう!](https://yomou.syosetu.com/)
 * [小説家になろう](https://syosetu.com/)
 * [Send to Kindle](https://www.amazon.co.jp/sendtokindle)
 * [Python](https://www.python.org/)
