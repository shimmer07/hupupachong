'''将数据库中的标题数据导出到文件中，并对其生成词云'''

# coding=utf-8
import os

import imageio
import jieba
import wordcloud
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


# 数据导出到文件中
def data_to_file(table_name):
    hupu_post = MongoAPI("localhost", 27017, "hupu", table_name)
    title_list = list(hupu_post.get_all({}))
    ingore = [
        'zt', 'jr', 'JR', '什么', '水平', '什么', '应该', '是不是', '现在', '流言', '这个',
        '如果', '为什么', '一个'
    ]
    with open(os.path.dirname(os.path.abspath(__file__)) + '\\results\\' +
              table_name + ".txt",
              mode="w",
              encoding="utf-8") as f:
        for eachone in title_list:
            for each in ingore:
                if each in eachone['title_name']:
                    eachone['title_name'] = eachone['title_name'].replace(
                        each, ' ')
            f.write(eachone['title_name'])
        f.close()


# 生成词云
def to_wordcloud(table_name, background):
    # 打开文件导入数据
    f = open(os.path.dirname(os.path.abspath(__file__)) + '\\results\\' +
             table_name + ".txt",
             "r",
             encoding="utf-8")
    t = f.read()
    f.close()
    ls = jieba.lcut(t)
    txt = " ".join(ls)
    # 设置背景图片basketball.png
    mask = imageio.imread(
        os.path.dirname(os.path.abspath(__file__)) + '\\resources\\' +
        background + ".png")
    # excludes = {}
    w = wordcloud.WordCloud(
        width=1000,
        height=700,
        background_color="white",
        mask=mask,
        # 没有设置字体可能出现，词云的结果均为方框。建议设置MSYH.ttc/MSYH.TTC（微软雅黑）
        font_path=r"C:\\Windows\\Fonts\simkai.ttf")
    w.generate(txt)
    # 在程序当前目录，生成图片table_name.png
    w.to_file(
        os.path.dirname(os.path.abspath(__file__)) + '\\results\\' +
        table_name + ".png")
    print("生成词云成功")


def data_to_wordcloud(table_name, background):
    data_to_file(table_name)
    to_wordcloud(table_name, background)


if __name__ == "__main__":
    data_to_wordcloud('vote', 'votebackground')
    data_to_wordcloud('bxj', 'bxjbackground')
    data_to_wordcloud('ent', 'entbackground')
