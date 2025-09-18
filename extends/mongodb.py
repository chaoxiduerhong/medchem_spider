"""
该脚本没有对参数做安全话校验，使用需要注意，避免sql注入攻击

常见操作符
$eq - =
$ne - !=
$gt - >
$gte - >=
$lt - <
$lte - <=
$in - in [start, end]
$nin - not in
$exists 检查字段是否存在 true or false
$regex 正则 $regex:/^a/

condition 格式
{
    "name": {"$eq": "zhangsan"}
}
order_by 格式(1升序，-1降序)
{
    "name": 1,
    "id": -1
}

"""
# coding: utf-8
# Desc: mongodb crud

from pymongo import MongoClient
import time
import traceback
from config.database import DBConfig


def safe_connect(func):
    """
    安全连接
    当数据库断开后，重连极致
    :param func:
    :return:
    """
    def wrapper(self, *args, **kw):
        result = None
        try:
            result = func(self, *args, **kw)
        except Exception as e:
            # TODO 这里记录重要日志
            print(traceback.format_exc())
            if "ServerSelectionTimeoutError" in str(traceback.format_exc()):
                self.re_connect_db()
                print("call function name [%s] error, reason mongodb disconnect...." % func.__name__, e)
            else:
                print(traceback.format_exc())

        return result
    return wrapper


class SimpleMongoDB:
    def __init__(self, connect_dbname="default"):
        # 要连接的数据库配置key
        self.connect_dbname = connect_dbname
        self.host = DBConfig.mongodb[self.connect_dbname]['host']
        self.user = DBConfig.mongodb[self.connect_dbname]['user']
        self.port = DBConfig.mongodb[self.connect_dbname]['port']
        self.password = DBConfig.mongodb[self.connect_dbname]['password']
        self.db = DBConfig.mongodb[self.connect_dbname]['db']
        # 连接到数据库服务
        self.conn_server = self.connect_server()
        # 连接到数据库, 返回数据库连接
        self.conn_db = self.connect_db()

    def connect_server(self):
        conn = MongoClient('mongodb://%s:%s' % (self.host, self.port))
        conn.server_selection_timeout = 5000
        return conn

    def connect_db(self):
        try:
            return self.conn_server[self.db]
        except Exception as e:
            print("connect mongodb failed! Error:%s" % e)
            return None

    def re_connect_db(self, num=5, stime=3):
        """

        :param num: 总共尝试的次数
        :param stime: 每次尝试结束后停留时间
        :return:
        """
        idx = 1
        _status = True
        print("check mongodb disconnect, retry connecting...")
        while _status and num >= idx:
            print("connecting retry %s/%s..." % (idx, num))
            try:
                self.conn_db = self.connect_server()
                # 连接到数据库, 返回数据库连接
                self.conn_db = self.connect_db()
                if self.conn_db:
                    print("success connect mongodb")
                    _status = False
            except Exception as e:
                if "ServerSelectionTimeoutError" in str(traceback.format_exc()):
                    print("Missing connect! Connecting...")
                    idx += 1
                    time.sleep(stime)
                else:
                    print('mongo error %s' % e)
                    _status = False

    def close(self):
        self.conn_server.close()

    @staticmethod
    def get_order_by(order_by):
        result = []
        for key in order_by:
            result.append((key, order_by[key]))
        return result

    @safe_connect
    def get_dbs(self):
        return self.conn_server.list_database_names()

    def get_tables(self):
        return self.conn_db.list_collection_names()

    @safe_connect
    def first(self, table_name, condition=None, fields=None, order_by=None):
        """
        查询第一条记录
        条件查询语句：
        {
            "name": {"$eq": "zhangsan"}
        }
        :param table_name:
        :param condition:
        :param fields:
        :param order_by:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        if not condition:
            condition = {}
        return tableCollection.find_one(condition)

    @safe_connect
    def all(self, table_name):
        try:
            tableCollection = self.conn_db[table_name]
            return list(tableCollection.find())
        except:
            return None

    @safe_connect
    def get(self, table_name, condition=None, fields=None, order_by=None, start: int = 0, length: int = 999):
        """
        limit()接受一个数字的参数，表示要读取多少条数据记录。
        skip()接受一个数字的参数，表示我们要跳过多少条数据记录。
        :param length:
        :param table_name:
        :param condition:
        :param fields:
        :param order_by:
        :param start:
        :return:
        """
        if order_by is None:
            order_by = {"time": -1}
        if fields is None:
            fields = {}
        start = int(start)
        length = int(length)

        # 不允许出现小于0的情况
        if start < 0:
            start = 0
        tableCollection = self.conn_db[table_name]
        return list(tableCollection.find(condition).sort(self.get_order_by(order_by)).skip(start).limit(length))

    def lock_find_one_and_update(self, table_name, condition, data, sort, return_document):
        tableCollection = self.conn_db[table_name]
        return tableCollection.find_one_and_update(
                condition,
                data,
                sort=sort,
                return_document=return_document
        )

    @safe_connect
    def total(self, table_name, condition=None):
        """
        按条件统计文档数量
        :param table_name:
        :param condition:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        return tableCollection.count_documents(condition)

    @safe_connect
    def all_total(self, table_name):
        """
        获取文档总数量
        :param table_name:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        return tableCollection.estimated_document_count()

    @safe_connect
    def group_total(self, table_name, fields, condition=None):
        """暂时不实现"""
        pass

    @safe_connect
    def insert_one(self, table_name, data):
        """
        插入单个文档, 并且返回id
        :param table_name:
        :param data:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        return tableCollection.insert_one(data).inserted_id

    @safe_connect
    def insert_many(self, table_name, data):
        """
        插入多个文档，并且返回ids
        :param table_name:
        :param data:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        return tableCollection.insert_many(data).inserted_ids

    @safe_connect
    def update_one(self, table_name, data, condition, upsert=False):
        """
        根据条件更新文档
        方法只能修匹配到的第一条记录
        :param table_name:
        :param data:
        :param condition:
        :return:
        """
        newValue = {"$set": data}
        tableCollection = self.conn_db[table_name]
        if not condition:
            condition = {}
        ret = tableCollection.update_one(condition, newValue, upsert=upsert)
        return ret.modified_count

    @safe_connect
    def update_many(self, table_name, data, condition):
        """
        根据条件更新文档
        适合条件的全部修改。必须符合condition，否则不做任何修改
        :param table_name:
        :param data:
        :param condition:
        :return:
        """
        if not condition:
            return None
        newValue = {"$set": data}
        tableCollection = self.conn_db[table_name]
        ret = tableCollection.update_many(condition, newValue)
        return ret.modified_count

    @safe_connect
    def delete_one(self, table_name, condition):
        """
        根据条件 删除单个文档
        :param table_name:
        :param condition:
        :return:
        """
        tableCollection = self.conn_db[table_name]
        return tableCollection.delete_one(condition).deleted_count

    @safe_connect
    def delete_many(self, table_name, condition):
        """
        根据条件 删除多个文档
        :param table_name:
        :param condition:
        :return:
        """
        # tableCollection = self.conn_db[table_name]
        # return tableCollection.delete_many(condition).deleted_count
        print("***** 安全起见，这里不启用一次删除多个记录 *****")
        return False

    @safe_connect
    def query(self, table_name, query):
        tableCollection = self.conn_db[table_name]
        return tableCollection.aggregate(query)

    # function for create unique index
    @safe_connect
    def create_index(self, table_name, field, uniq=False):
        tableCollection = self.conn_db[table_name]
        if uniq:
            return tableCollection.create_index(field, unique=True)
        else:
            return tableCollection.create_index(field)