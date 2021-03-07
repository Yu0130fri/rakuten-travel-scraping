#====================================================================================
#ライブラリインポート	
#====================================================================================
import csv
import sys
from mypackage import module

#====================================================================================
#コマンドライン引数でhotel_idを取得する			
#====================================================================================
try:
	hotel_id = sys.argv[1]
	hotel_id = str(hotel_id)
except:
	#デフォルトでサンプルのIDを設定しておく	
	hotel_id = "138039"

#====================================================================================
#必要な変数の準備		
#====================================================================================
hotel_review_url = "https://travel.rakuten.co.jp/HOTEL/" + hotel_id +"/review.html"

header=[
    "ホテル名",
    "ホテルID",
    "ユーザ名",
    "性別",
    "年代",
    "URL",
    "クチコミID",
    "投稿日",
    "宿泊年月",
    "評価(総合)",
    "評価(サービス)",
    "評価(立地)",
    "評価(部屋)",
    "評価(設備・アメニティ)",
    "評価(風呂)",
    "評価(食事)",
    "口コミ種別",
    "口コミ",
    "ホテル側の返答",
    "ご利用の宿泊プラン",
    "ご利用のお部屋"
]


#実行
if __name__=="__main__":
	hotel_name,comment_list = module.make_csv(hotel_review_url)
	#エンコードの指定を行う（デフォルトはUTF-8で指定する）
	try:
		file_encode = sys.argv[2]

	except:
		file_encode ="utf-8"

	file_name = "楽天トラベル_"+hotel_name+"_レビュー_"+file_encode+".csv"

	try:
		with open(file_name,"w",encoding=file_encode, newline="") as f:
		    writer = csv.writer(f)
		    
		    writer.writerow(header)
		    
		    for comment_row in comment_list:
		        writer.writerow(comment_row)
	except:
		#念のため、エラー時はsjis形式で落とせるようにエラー処理を格納しておく
		file_name_sjis = "楽天トラベル_"+hotel_name+"_レビュー_sjis.csv"
		with open(file_name_sjis,"w",encoding="cp932", newline="") as f:
		    writer = csv.writer(f)
		    
		    writer.writerow(header)
		    
		    for comment_row in comment_list:
		        writer.writerow(comment_row)

