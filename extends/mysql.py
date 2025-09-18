# coding: utf-8
# Desc: mysql crud

import pymysql
import time
from pymysql.converters import escape_string

from ..config import setting
import threading

mysql_safe_lock = threading.Lock()


def safe_connect(func):
    def wrapper(self, *args, **kw):
        result = None
        mysql_safe_lock.acquire()
        try:
            result = func(self, *args, **kw)
        except Exception as e:
            print("call function name [%s] error, reason mysql disconnect...." % func.__name__, e)
            self.re_connect_db()
        mysql_safe_lock.release()
        return result

    return wrapper


class baseDB:
    def __init__(self):
        self.host = setting.mysql_host
        self.user = setting.mysql_user
        self.port = setting.mysql_port
        self.passwd = setting.mysql_password
        self.db = setting.mysql_database
        self.conn = False
        self.cursor = False
        self.connect_db()

    def connect_db(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                        connect_timeout=1)
            self.cursor = self.conn.cursor()
        except:
            print("connect mysql failed!")
            self.cursor = False
            self.cursor = False

    def re_connect_db(self, num=1, stime=1):  # 重试连接总次数为1天,这里根据实际情况自己设置,如果服务器宕机1天都没发现就......
        _number = 1
        _status = True
        while _status and _number <= num:
            try:
                self.conn.ping()  # cping 校验连接是否异常
                _status = False
            except:
                print("Missing connect! Connecting...")
                if self.connect_db() is True:  # 重新连接,成功退出
                    _status = False
                    break
                _number += 1
                time.sleep(stime)

    def close(self):
        self.conn.close()

    @safe_connect
    def first(self, table_name, condition=None, fields=None, order_by=None):
        fieldsStr = ""
        if not fields:
            # 通过查询获取所有的field
            fieldsStr = "*"
        else:
            for field in fields:
                fieldsStr = fieldsStr + "`%s`," % field
            fieldsStr = fieldsStr.strip(",")
        sql = "select %s from %s" % (fieldsStr, table_name)

        safe_params = []
        if condition:
            where = " where 1 "
            for item in condition:
                where = where + " and " + item + " " + condition[item][0] + "%s"
                safe_params.append(condition[item][1])
            sql = sql + where

        if safe_params:
            self.cursor.execute(sql, tuple(safe_params))
        else:
            self.cursor.execute(sql)

        result = self.cursor.fetchone()
        if result:
            # 根据 fields 封装
            fields = [i[0] for i in self.cursor.description]
            return dict(zip(fields, result))
        else:
            return result

    @safe_connect
    def all(self, sql):
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return data

    @safe_connect
    def get(self, table_name, condition=None, fields=None, order_by=None, start: int = 0, len: int = 999):
        """
        条件查询目前只支持 and 查询，不支持组合查询。组合查询请使用其他
        condition Demo {
                "progress_type": ['=', progress_type],
                'version': ["=", version],
                'progress_info': ["=", progress_info]
        }
        order_by Demo {
            "id": "desc"
        }
        :param len:
        :param start:
        :param fields:
        :param table_name:
        :param condition:
        :param order_by:
        :return:
        """
        start = int(start)
        len = int(len)
        # 不允许出现小于0的情况
        if start < 0:
            start = 0
        fieldsStr = ""
        if not fields:
            # 通过查询获取所有的field
            fieldsStr = "*"
        else:
            for field in fields:
                fieldsStr = fieldsStr + "`%s`," % field
            fieldsStr = fieldsStr.strip(",")
        sql = "select %s from %s" % (fieldsStr, table_name)

        safe_params = []
        if condition:
            where = " where 1 "
            for item in condition:
                where = where + " and " + item + " " + condition[item][0] + "%s"
                safe_params.append(condition[item][1])
            sql = sql + where

        if order_by:
            orderByStr = " order by "
            for item in order_by:
                # TODO  item 和 orderByStr[item] 都必须为字符串。避免混淆sql注入
                orderByStr = orderByStr + " " + str(item) + " " + str(order_by[item]) + ","
            orderByStr = orderByStr.strip(",")
            sql = sql + orderByStr
        sql = sql + " limit %s, %s" % (start, len)
        if safe_params:
            self.cursor.execute(sql, tuple(safe_params))
        else:
            self.cursor.execute(sql)
        result = self.cursor.fetchall()
        # 根据 fields 封装
        fields = [i[0] for i in self.cursor.description]
        return [dict(zip(fields, row)) for row in result]

    @safe_connect
    def total(self, table_name, condition=None):
        """
        条件查询目前只支持 and 查询，不支持组合查询。组合查询请使用其他
        condition Demo {
                "progress_type": ['=', progress_type],
                'version': ["=", version],
                'progress_info': ["=", progress_info]
        }
        :param table_name:
        :param condition:
        :return:
        """
        sql = "select * from %s" % table_name
        safe_params = []
        if condition:
            where = " where 1 "
            for item in condition:
                where = where + " and " + item + " " + condition[item][0] + "%s"
                safe_params.append(condition[item][1])
            sql = sql + where
        if safe_params:
            self.cursor.execute(sql, tuple(safe_params))
        else:
            self.cursor.execute(sql)
        return self.cursor.rowcount

    @safe_connect
    def group_total(self, table_name, fields, condition=None):
        """
        条件查询目前只支持 and 查询，不支持组合查询。组合查询请使用其他
        condition Demo {
                "progress_type": ['=', progress_type],
                'version': ["=", version],
                'progress_info': ["=", progress_info]
        }
        :param table_name:
        :param condition:
        :return:
        """
        fieldStr = ""
        for f in fields:
            fieldStr = "%s`%s`," % (fieldStr, escape_string(f))
        fieldStr = fieldStr.strip(",")
        sql = "select %s from %s" % (fieldStr, table_name)
        safe_params = []
        if condition:
            where = " where 1 "
            for item in condition:
                where = where + " and " + item + " " + condition[item][0] + "%s"
                safe_params.append(condition[item][1])
            sql = sql + where

        sql = "%s group by %s" % (sql, fieldStr)
        if safe_params:
            self.cursor.execute(sql, tuple(safe_params))
        else:
            self.cursor.execute(sql)
        return self.cursor.rowcount

    @safe_connect
    def insert(self, table_name, data):
        keys = data.keys()
        values = data.values()
        values = ['%s' % row for row in values]
        key_str = "`%s`" % "`,`".join(keys)
        value_str = "'%s'" % "','".join(values)
        sql = "insert into `%s` (%s) value(%s)" % (table_name, key_str, value_str)
        return self.exec(sql)

    @safe_connect
    def update(self, table_name, data, condition):
        sql = "update %s set " % table_name
        for item in data:
            sql = "%s `%s`='%s'," % (sql, item, data[item])
        sql = sql.strip(",")
        if condition:
            where = " where 1 "
            for item in condition:
                where = "%s and `%s` %s '%s'" % (
                where, escape_string(item), escape_string(condition[item][0]), escape_string(condition[item][1]))
            sql = sql + where
        else:
            # 更新必须输入条件，否则不能更新数据
            return False
        return self.exec(sql)

    @safe_connect
    def delete(self, table_name, condition):
        sql = "delete from %s " % table_name
        if condition:
            where = " where 1 "
            for item in condition:
                where = "%s and `%s` %s '%s'" % (
                where, escape_string(item), escape_string(condition[item][0]), escape_string(condition[item][1]))
            sql = sql + where
        else:
            # 更新必须输入条件，否则不能更新数据
            return False
        return self.exec(sql)

    @safe_connect
    def insertGetId(self, table_name, data):
        keys = data.keys()
        values = data.values()
        values = ['%s' % row for row in values]
        key_str = "`%s`" % "`,`".join(keys)
        value_str = "'%s'" % "','".join(values)
        sql = "insert into `%s` (%s) value(%s)" % (table_name, key_str, value_str)
        try:
            ret = self.cursor.execute(sql)
            retID = self.conn.insert_id()
            self.conn.commit()
        except Exception as e:
            retID = None
            self.conn.rollback()
        return retID

    def exec(self, sql):
        try:
            # 执行sql语句
            ret = self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            # Rollback in case there is any error
            self.conn.rollback()
        return False


BDB = baseDB()
