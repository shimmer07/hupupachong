'''虎扑用户性别比例图'''

from pyecharts import options as opts
from pyecharts.charts import Page, Pie
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import os


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


def get_gender(link):
    r = requests.get(link)
    html = r.content
    html = html.decode('UTF-8')
    soup = BeautifulSoup(html, 'lxml')
    gender_soup = soup.find('span', itemprop="gender")
    if gender_soup is not None:
        gender = gender_soup.text.strip()
    else:
        gender = '未知'
    return gender


# c = (
#     Pie()
#     .add("", [list(z) for z in zip(Faker.choose(), Faker.values())])
#     .set_global_opts(title_opts=opts.TitleOpts(title="虎扑用户性别比例图"))
#     .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
# )
# # c.render('render.html')
# print([list(z) for z in zip(Faker.choose(), Faker.values())])

hupu_post = MongoAPI('localhost', 27017, 'hupu', 'vote')
the_list = list(hupu_post.get_all({}))
author_gender = {'男': 0, '女': 0, '未知': 0}
for eachone in the_list:
    link = eachone['author_link']
    gender = get_gender(link)
    if gender == '男':
        author_gender['男'] += 1
        print(author_gender['男'])
    elif gender == '女':
        author_gender['女'] += 1
        print(author_gender['女'])
    elif gender == '未知':
        author_gender['未知'] += 1
        print(author_gender['未知'])
print("author_gender['男']{}".format(author_gender['男']))
print("author_gender['女']{}".format(author_gender['女']))
print("author_gender['未知']{}".format(author_gender['未知']))
gender_rate = []
gender_rate.append(['男', author_gender['男']])
gender_rate.append(['女', author_gender['女']])
gender_rate.append(['未知', author_gender['未知']])
c = (Pie().add("", gender_rate).set_global_opts(title_opts=opts.TitleOpts(
    title="虎扑用户性别比例图")).set_series_opts(label_opts=opts.LabelOpts(
        formatter="{b}: {c}")))
c.render(r'F:\\python exercise\\虎扑爬虫\\results\\userrating.html')
