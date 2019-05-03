"""抓取虎扑论坛数据"""

# coding:utf-8
import datetime
import time

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# 建立MongoAPI类便于访问数据库
class MongoAPI(object):
    def __init__(self, db_ip, db_port, db_name, table_name):
        self.db_ip = db_ip
        self.db_port = db_port
        self.db_name = db_name
        self.table_name = table_name
        self.cnn = MongoClient(host=self.db_ip, port=self.db_port)
        self.db = self.cnn[self.db_name]
        self.table = self.db[self.table_name]

    def get_one(self, query):
        return self.table.find_one(query, projection={"_id": False})

    def get_all(self, query):
        return self.table.find(query)

    def add(self, kv_dict):
        return self.table.insert_one(kv_dict)

    def delete(self, query):
        return self.table.delete_many(query)

    def check_exit(self, query):
        ret = self.table.find_one(query)
        return ret != None

    def update(self, query, kv_dict):
        self.table.update_one(query, {'$set': kv_dict}, upsert=True)


# 得到链接的内容,返回BeatifulSoup对象
def get_page(link):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    r = requests.get(link, headers=headers)
    html = r.content
    html = html.decode('UTF-8')
    soup = BeautifulSoup(html, 'lxml')
    return soup


# 获取文章列表的中的标题及链接、作者及链接、发表日期、浏览数及回复数、最近回复时间


def get_data(post_list):
    data_list = []
    for post in post_list:
        # 得到帖子名称标题
        title = post.find("div", class_="titlelink box")
        title_name = title.a.text.strip()
        title_link = "https://bbs.hupu.com" + title.a['href']
        # 得到作者及发帖时间
        author_name = post.find("div", class_="author box").contents[1].text
        author_link = post.find("div", class_="author box").contents[1]['href']
        start_time = post.find("div",
                               class_="author box").contents[5].text.strip()
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d").date()
        # 得到浏览数/回复数
        reply_view = post.find("span",
                               class_="ansour box").text.split('\xa0/\xa0')
        reply = reply_view[0]
        view = reply_view[1]
        # 得到最新回复的时间
        reply_last = post.find("div", class_="endreply box")
        reply_last_user = reply_last.find("span").text.strip()
        reply_last_time = reply_last.a.text.strip()
        # 如果没有日期，生成今天的日期
        if ':' in reply_last_time:
            reply_last_time = str(
                datetime.date.today()) + ' ' + reply_last_time
            reply_last_time = datetime.datetime.strptime(
                reply_last_time, "%Y-%m-%d %H:%M")
        else:
            reply_last_time = datetime.datetime.strptime(
                '2019-' + reply_last_time, '%Y-%m-%d').date()
        data_list.append([
            title_name, title_link, author_name, author_link, start_time,
            reply, view, reply_last_time, reply_last_user
        ])
    return data_list


# 获取页面中文章等信息


def get_page_data(link, i, hupu_post):
    soup = get_page(link)
    post_list = soup.select("ul.for-list > li")
    data_list = get_data(post_list)
    f = 0
    for each in data_list:
        f += 1
        hupu_entry = {
            'title_name': each[0],
            'title_link': each[1],
            'author_name': each[2],
            'author_link': each[3],
            'start_time': str(each[4]),
            # 时间进行过格式化，这里转化成字符串，下面同理
            'reply': each[5],
            'view': each[6],
            'reply_last_time': str(each[7]),
            'reply_last_user': each[8]
        }
        # 匹配插入数据库
        hupu_post.update({'title_link': each[1]}, hupu_entry)
    print('第', i, '页获取完成,休息3秒')
    print("共有", f, "条记录")
    # 沉睡3秒
    time.sleep(3)


# 获取步行街信息


def get_bxj_data():
    main_link = "https://bbs.hupu.com/bxj"
    # 连接数据库 localhost: 27017 数据库："hupu" 表："post"
    hupu_post = MongoAPI("localhost", 27017, "hupu", "bxj")
    # 获取第一页到第十页的信息，第十页之后需要登陆
    for i in range(1, 11):
        get_page_data(main_link + '-' + str(i), i, hupu_post)


# 获取影视圈中信息


def get_ent_data():
    main_link = "https://bbs.hupu.com/ent"
    # 连接数据库 localhost: 27017 数据库："hupu" 表："post"
    hupu_post = MongoAPI("localhost", 27017, "hupu", "ent")
    # 获取第一页到第十页的信息，第十页之后需要登陆
    for i in range(1, 11):
        get_page_data(main_link + '-' + str(i), i, hupu_post)


# 获取影视圈中信息


def get_vote_data():
    main_link = "https://bbs.hupu.com/vote"
    # 连接数据库 localhost: 27017 数据库："hupu" 表："post"
    hupu_post = MongoAPI("localhost", 27017, "hupu", "vote")
    # 获取第一页到第十页的信息，第十页之后需要登陆
    for i in range(1, 11):
        get_page_data(main_link + '-' + str(i), i, hupu_post)


if __name__ == "__main__":
    get_ent_data()
    get_bxj_data()
    get_vote_data()
