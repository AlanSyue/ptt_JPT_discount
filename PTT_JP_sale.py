# 撈取 PTT Web 推文數、標題名稱、發文日期、作者，參考來源：https://github.com/leVirve/CrawlerTutorial
import requests
import urllib.parse
from bs4 import BeautifulSoup
import sqlite3
from fbchat import Client
from fbchat.models import *
import datetime

x = datetime.datetime.now()
time = str(x.month)+"/"+str(x.day)
conn = sqlite3.connect('C:/Users/user/sqlite01.db')
c = conn.cursor()
print ("Opened database successfully")

INDEX = 'https://www.ptt.cc/bbs/Japan_Travel/index.html'
NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a


def get_posts_on_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    posts = list()
    for article in soup.find_all('div', 'r-ent'):
        meta = article.find('div', 'title').find('a') or NOT_EXIST
        posts.append({
            'title': meta.getText().strip(),
            'link': meta.get('href'),
            'push': article.find('div', 'nrec').getText(),
            'date': article.find('div', 'date').getText(),
            'author': article.find('div', 'author').getText(),
        })

    next_link = soup.find('div', 'btn-group-paging').find_all('a', 'btn')[1].get('href')

    return posts, next_link


def get_pages(num):
    page_url = INDEX
    all_posts = list()
    for i in range(num):
        posts, link = get_posts_on_page(page_url)
        all_posts += posts
        page_url = urllib.parse.urljoin(INDEX, link)
    return all_posts



if __name__ == '__main__':
    pages = 5 #撈取頁數

    for post in get_pages(pages):
        sale_title = post['title'].find("促銷")
        if sale_title>=0:
            print(post['title'])
            db_PM_url = "https://www.ptt.cc"+post['link']
            try:
                c.execute("INSERT INTO ptt_jp_ticket (url,title,date)\
                    VALUES (?,?,? )", (db_PM_url,post['title'],post['date']))
            except:
                print("None")

url = c.execute("select url from ptt_jp_ticket where date like ?",[time])
data_url = url.fetchall()
title = c.execute("select title from ptt_jp_ticket where date like ?",[time])
data_title = title.fetchall()
message = "PTT-JP "+"網址："+str(data_url[0])+"\t"+"主旨："+str(data_title[0])
client = Client('facebook帳號', 'facebook密碼')
print("login success")
#帶入訊息，thread_id 需查找傳送對象之 fb id
client.send(Message(text=message), thread_id='facebook User id', thread_type=ThreadType.USER)
print("send correct")
client.logout()
print("finish")
conn.commit()
conn.close()