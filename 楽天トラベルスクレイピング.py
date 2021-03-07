#====================================================================================
#ライブラリインポート	
#====================================================================================
from bs4 import BeautifulSoup
import csv
import datetime
import numpy as np
import re
import requests
import time
import sys


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


def main():
	#情報を取得する
	response = requests.get(hotel_review_url)

	#そのままスクレイピングしちゃうと文字化けしちゃったので、エンコードを指定
	#https://orangain.hatenablog.com/entry/encoding-in-requests-and-beautiful-soup
	content_type_encoding = response.encoding if response.encoding != 'ISO-8859-1' else None

	soup = BeautifulSoup(response.content, 'html.parser', from_encoding=content_type_encoding)

	#取得できるホテル名とホテルIDは先に取得しておく
	#====================================================================================
	#ホテル名		
	#====================================================================================
	hotel_name = soup.select("#RthNameArea > h2")[0].text
	#print("ホテル名 :",hotel_name)

	#====================================================================================
	#ホテルID
	#====================================================================================
	#<script>の中で定義されいてる
	hotel_script = soup.find_all(text=re.compile("var actionvirus_hotel_no="))[0]
	hotel_ID = hotel_script.replace("\n"," ").replace('"; '," ").replace('var actionvirus_hotel_no="'," ").replace(" ","")


	#口コミすべてを取得するためにすべてのURLをスクレイピングしCSVに落とし込む
	next_url = soup.select("ul.pagingNumber > li.pagingNext > a")[0]
	next_url_link_format = next_url["href"][:-2]

	#ページの総数取得
	number_of_pages = soup.select("div.pagingArea > ul.pagingNumber > li > a:last-child")
	all_page = number_of_pages[0].text


	all_page_list = []
	for num in range(int(all_page)):
	    page_num = num*20
	    url = next_url_link_format+str(page_num)
	    all_page_list.append(url)


	comment_list = []

	for index, page in enumerate(all_page_list):
	    try:
	        response_throgh_page = requests.get(page)

	        #対策のため、適度に動作を停止させる
	        random = np.random.randint(2,5)
	        time.sleep(random)

	        soup_throgh_page= BeautifulSoup(response_throgh_page.content, 'html.parser', from_encoding=content_type_encoding)

	        #ページにある口コミのURLを取得する
	        comments_link_list = soup_throgh_page.select(".commentBox > .commentTitle > a")

	        for comment_link_tag in comments_link_list:
	            comment_link = comment_link_tag["href"]

	            #各レビューページをスクレイピング
	            response_comment = requests.get(comment_link)

	            #対策のため、適度に動作を停止させる
	            random = np.random.randint(1,3)
	            time.sleep(random)


	            soup_comment = BeautifulSoup(response_comment.content,"html.parser")

				#====================================================================================
				##ユーザー名、年代、性別
				#====================================================================================
	            user_sex_gen = soup_comment.select("dl.commentReputation > dt > span.user")
	            #正規表現で\s（半角スペースかつ\n,\t,\rを含む）を置換
	            user_gen_sex_split = re.sub("\s","",user_sex_gen[0].text)\
	                                .replace("さん"," ").replace("[","").replace("/"," ").replace("]","")\
	                                .split(" ")
				#====================================================================================
				#ユーザー名
				#====================================================================================
	            user_name = user_gen_sex_split[0]

				#====================================================================================
				#年代
				#====================================================================================
	            user_gen = user_gen_sex_split[1] if len(user_gen_sex_split)>1 else ""

				#====================================================================================
				#性別
				#====================================================================================
	            user_sex = user_gen_sex_split[2] if len(user_gen_sex_split)>2 else ""

				#====================================================================================
				#URL
				#====================================================================================
	            url = comment_link

	            #クチコミID
	            #場所不明のため保留

				#====================================================================================
				#投稿日
				#====================================================================================
	            post_date_select = soup_comment.select(".commentReputation > dt > span.time")
	            post_date_select_list = post_date_select[0].text.split()

	            post_date = datetime.datetime.strptime(str(post_date_select_list[5])+","+\
	                                                   str(post_date_select_list[1])+","+\
	                                                   str(post_date_select_list[2])+","+str(post_date_select_list[3])\
	                                                  ,"%Y,%b,%d,%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

				#====================================================================================
				#宿泊年月
				#====================================================================================
	            if len(soup_comment.find("dt",text=re.compile("宿泊年月")))>0 :
	                datetime_of_stay = soup_comment.find("dt",text=re.compile("宿泊年月")).next_sibling.next_sibling

	                date_list = datetime_of_stay.text.split()

	                date_of_stay_year_mon_day = datetime.datetime.strptime(str(date_list[5])+","+str(date_list[1]),"%Y,%b")\
	                                            .strftime("%Y-%m-%d %H:%M:%S").split()[0]

	                date_split = date_of_stay_year_mon_day.split("-")
	                date_of_stay = date_split[0]+"月"+date_split[1]+"月"
	            else:
	                date_of_stay =""

				#====================================================================================
				#評価
				#====================================================================================
	            review_all = soup_comment.select("ul.rateDetail > li> span")

	            if len(review_all) > 0:
	                #総合
	                review_total = review_all[0].text
	                #サービス
	                review_service =review_all[1].text
	                #立地
	                review_location = review_all[2].text
	                #部屋
	                review_room = review_all[3].text
	                #設備・アメニティ
	                review_facility = review_all[4].text
	                #風呂
	                review_bath = review_all[5].text
	                #食事
	                review_meal = review_all[6].text

	            else:
	                #総合
	                review_total = "-"
	                #サービス
	                review_service ="-"
	                #立地
	                review_location = "-"
	                #部屋
	                review_room = "-"
	                #設備・アメニティ
	                review_facility = "-"
	                #風呂
	                review_bath = "-"
	                #食事
	                review_meal = "-"

	            #口コミ種別
	            #種別は一旦保留

				#====================================================================================
				#口コミ内容
				#====================================================================================
	            comment_sentence_list = soup_comment.find_all("p",class_= "commentSentence")

	            #投稿者の口コミ
	            user_comment= comment_sentence_list[0].text
	            user_comment = re.sub("\s","",user_comment)

	            #ホテル側の返信
	            if len(comment_sentence_list)>1:
	                hotel_comment= comment_sentence_list[1].text

	            else:
	                hotel_comment = ""

				#====================================================================================
				#ご利用の宿泊プラン
				#====================================================================================
	            class_plan = soup_comment.find("dt",text = re.compile("ご利用の宿泊プラン"))
	            if len(class_plan)>0:
	                used_plan = re.sub("\s","",class_plan.next_sibling.next_sibling.text)
	            else:
	                used_plan = ""

	            #ご利用のお部屋
	            class_plan = soup_comment.find("dt",text = re.compile("ご利用のお部屋"))
	            if len(class_plan)>0:
	                used_room = re.sub("\s","",class_plan.next_sibling.next_sibling.text)
	            else:
	                used_room = ""


	            #取得したデータの格納 
	            review_data_list = []

	            #ホテル名
	            review_data_list.append(hotel_name)
	            #ホテルID
	            review_data_list.append(hotel_ID)
	            #ユーザ名
	            review_data_list.append(user_name)
	            #性別
	            review_data_list.append(user_gen)
	            #年代
	            review_data_list.append(user_sex)
	            #URL
	            review_data_list.append(comment_link)
	            #クチコミID
	            #場所不明のため保留
	            review_data_list.append("")
	            #投稿日
	            review_data_list.append(post_date)
	            #宿泊年月
	            review_data_list.append(date_of_stay)
	            #評価(総合)
	            review_data_list.append(review_total)
	            #評価(サービス)
	            review_data_list.append(review_service)
	            #評価(立地)
	            review_data_list.append(review_location)
	            #評価(部屋)
	            review_data_list.append(review_room)
	            #評価(設備・アメニティ)
	            review_data_list.append(review_facility)
	            #評価(風呂)
	            review_data_list.append(review_bath)
	            #評価(食事)
	            review_data_list.append(review_meal)
	            #口コミ種別
	            #種別は一旦保留
	            review_data_list.append("")
	            #口コミ
	            review_data_list.append(user_comment)
	            #ホテル側の返答
	            review_data_list.append(hotel_comment)
	            #ご利用の宿泊プラン
	            review_data_list.append(used_plan)
	            #ご利用のお部屋
	            review_data_list.append(used_room)


	            #できたreview_data_listをcomment_listに格納する
	            comment_list.append(review_data_list)

	        print("{} :終了".format(index))
	        
	    except:
	        print("{}ページはスキップされました".format(index))
	        pass
	        
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

#実行
if __name__=="__main__":
	main()