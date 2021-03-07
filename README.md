# rakuten-travel-scraping
楽天トラベルのレビューページをホテルごとに一括で取得するコードです。		
最終的にはFlaskもしくはDjangoなどで実装をゴールにしているため、定期的なアップデートを予定しています。

・使い方
事前に準備するものはホテルIDです
たとえば、渋谷グランベルホテルの場合、URLの52992がIDとなります。
https://travel.rakuten.co.jp/HOTEL/52992/?l-id=_rechotel

-操作
コマンドプロンプトやターミナルでフォルダまでcdコマンドで移動します。
その後、
「python 楽天トラベルスクレイピング.py {ホテルID} {文字コード※}」
で実行します。
※文字コードはutf-8 や cp932などです。
エラー発生回避のため、デフォルトはcp932で指定済み

取得完了すれば、直下にcsvファイルが生成されます。	