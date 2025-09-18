# coding: utf-8
# Desc: crud base

from utils import common
from extends import SimpleMongoDB
from abc import ABCMeta, abstractmethod


class BaseModel(metaclass=ABCMeta):
    def __init__(self):
        # 要连接的数据库
        self.connection = "default"
        # 表名称，子类必须重写该表名称
        self.table_name = None
        # 展示的常规日期格式字段
        self.created_at = "created_at"
        # 展示的常规日期格式字段
        self.updated_at = "updated_at"
        # 自增字段，用于倒序排序 unix 毫秒时间戳
        self.time = "time"
        # 定义主键
        self.key = "cid"
        self.MongoDB = None

    def ConnDB(self):
        if not self.MongoDB:
            self.MongoDB = SimpleMongoDB(self.connection)
        return self.MongoDB

    def lock_find_one_and_update(self, condition, data, sort, return_document):
        """
        sort格式 [("field", 1),("field1", 1)]
        """
        return self.ConnDB().lock_find_one_and_update(
                table_name=self.table_name,
                condition=condition,
                data=data,
                sort=sort,
                return_document=return_document
        )
    
    def create_index(self, field, uniq=False):
        return self.ConnDB().create_index(self.collection, field, uniq)

    def add_one(self, data):
        # 如果开启了updated_at 和created_at 这里自动注入
        data[self.time] = common.ts()
        data[self.created_at] = common.get_now_str()
        data[self.updated_at] = common.get_now_str()
        data[self.key] = common.get_cid()
        return self.ConnDB().insert_one(self.table_name, data)

    def add_many(self, data):
        # 如果开启了updated_at 和created_at 这里自动注入
        for item in data:
            data[item][self.time] = common.ts()
            data[item][self.created_at] = common.get_now_str()
            data[item][self.updated_at] = common.get_now_str()
            data[item][self.key] = common.get_cid()
        return self.ConnDB().insert_many(self.table_name, data)

    def update_one(self, data, condition, upsert=False):
        data[self.updated_at] = common.get_now_str()
        return self.ConnDB().update_one(
            table_name=self.table_name,
            condition=condition,
            data=data,
            upsert=upsert
        )

    def update_many(self, data, condition):
        data[self.updated_at] = common.get_now_str()
        return self.ConnDB().update_many(
            table_name=self.table_name,
            condition=condition,
            data=data
        )

    def delete(self, condition):
        return self.ConnDB().delete_one(
            table_name=self.table_name,
            condition=condition
        )

    def delete_many(self, condition):
        return self.ConnDB().delete_many(
            table_name=self.table_name,
            condition=condition
        )

    def get(self, condition=None, fields=None, order_by=None, start: int = 0, length: int = 999999999):
        return self.ConnDB().get(
            table_name=self.table_name,
            condition=condition,
            order_by=order_by,
            start=start,
            length=length
        )

    def total(self, condition=None):
        return self.ConnDB().total(
            table_name=self.table_name,
            condition=condition,
        )

    def query(self, query=None):
        return self.ConnDB().query(
            table_name=self.table_name,
            query=query,
        )

    def all_total(self):
        return self.ConnDB().all_total(
            table_name=self.table_name
        )

    def get_dbs(self):
        return self.ConnDB().get_dbs()

    def get_tables(self):
        return self.ConnDB().get_tables()

    def first(self, condition=None, fields=None, order_by=None):
        """
        暂不支持fields 和 order_by
        :param condition:
        :param fields:
        :param order_by:
        :return:
        """
        return self.ConnDB().first(
            table_name=self.table_name,
            condition=condition,
            fields=fields,
            order_by=order_by
        )

