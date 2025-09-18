"""
AI 方案文档
https://chatgpt.com/share/67f60f71-4544-8005-895d-915c090067cf


"""
import sqlite3
import traceback
import time
import threading

# 示例配置，对于 sqlite 来说只需要配置数据库文件路径
DBConfig = {
    'sqlite': {
        'default': {
            'db_file': 'database.sqlite3'
        }
    }
}

def safe_connect(func):
    """
    安全连接
    当数据库断开后，重连机制
    """
    def wrapper(self, *args, **kwargs):
        result = None
        try:
            result = func(self, *args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            # 如果出现 sqlite3 错误，则尝试重连
            if isinstance(e, sqlite3.Error):
                self.re_connect_db()
                print("call function name [%s] error, reason sqlite disconnect...." % func.__name__, e)
            else:
                print(traceback.format_exc())
        return result
    return wrapper

# 使用 metaclass 实现单例
class SingletonType(type):
    _instances = {}
    _lock = threading.Lock()  # 保证线程安全
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super(SingletonType, cls).__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class SimpleSqlite(metaclass=SingletonType):
    def __init__(self, connect_dbname="default", config={}):
        # 通过传入的 config 或使用默认全局配置，获取数据库文件路径
        self.connect_dbname = connect_dbname
        conf = config if config else DBConfig['sqlite'][self.connect_dbname]
        self.db_file = conf.get('db_file', 'database.sqlite3')
        # 建立数据库连接
        self.conn_db = self.connect_db()

    def connect_db(self):
        """
        链接到数据库文件，返回 sqlite3.Connection 对象
        """
        try:
            # 设置 check_same_thread=False 允许多线程访问，row_factory 设置字典模式
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print("Error connecting to sqlite database:", e)
            return None

    def re_connect_db(self, num=5, stime=3):
        """
        当连接失败时，尝试重新连接数据库
        :param num: 尝试次数
        :param stime: 每次重连间隔秒数
        """
        count = 0
        while count < num:
            try:
                self.conn_db = self.connect_db()
                if self.conn_db is not None:
                    print("Reconnected to SQLite database.")
                    break
            except Exception as e:
                print("Reconnect attempt failed:", e)
            count += 1
            time.sleep(stime)
        if self.conn_db is None:
            raise Exception("Could not reconnect to SQLite database after %d attempts" % num)

    def close(self):
        """
        关闭数据库连接
        """
        if self.conn_db:
            self.conn_db.close()
            self.conn_db = None

    @safe_connect
    def get_dbs(self):
        """
        获取附加的数据库列表（SQLite 内置 main 和 temp）
        """
        cursor = self.conn_db.execute("PRAGMA database_list;")
        dbs = [dict(row) for row in cursor.fetchall()]
        return dbs

    def get_tables(self):
        """
        获取当前数据库下所有的数据表
        """
        cursor = self.conn_db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        return tables

    @safe_connect
    def first(self, table_name, condition=None, fields=None, order_by=None):
        """
        查询第一条记录,以字典形式返回
        :param table_name: 数据表名称
        :param condition: 查询条件（字符串），例如 "id=1"
        :param fields: 返回的字段列表，默认全部字段
        :param order_by: 排序规则
        """
        field_str = ", ".join(fields) if fields else "*"
        sql = f"SELECT {field_str} FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        sql += " LIMIT 1"
        cursor = self.conn_db.execute(sql)
        row = cursor.fetchone()
        return dict(row) if row else None

    @safe_connect
    def all(self, table_name):
        """
        查询所有记录, 返回字典列表
        """
        sql = f"SELECT * FROM {table_name}"
        cursor = self.conn_db.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @safe_connect
    def get(self, table_name, condition=None, fields=None, order_by=None, start: int = 0, length: int = 999):
        """
        根据条件查询多条记录, 返回字典列表
        :param start: 起始位置
        :param length: 查询长度
        """
        field_str = ", ".join(fields) if fields else "*"
        sql = f"SELECT {field_str} FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        sql += f" LIMIT {length} OFFSET {start}"
        cursor = self.conn_db.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @safe_connect
    def total(self, table_name, condition=None):
        """
        根据条件查询记录数量，返回整数
        """
        sql = f"SELECT COUNT(*) as count FROM {table_name}"
        if condition:
            sql += f" WHERE {condition}"
        cursor = self.conn_db.execute(sql)
        row = cursor.fetchone()
        return row['count'] if row else 0

    @safe_connect
    def all_total(self, table_name):
        """
        获取表中总记录数量
        """
        return self.total(table_name)

    @safe_connect
    def insert_one(self, table_name, data):
        """
        插入一条记录, 并返回插入记录的ID
        :param data: 字典形式，键为字段，值为数据
        """
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        cursor = self.conn_db.cursor()
        cursor.execute(sql, tuple(data.values()))
        self.conn_db.commit()
        return cursor.lastrowid

    @safe_connect
    def insert_many(self, table_name, data_list):
        """
        插入多条记录, 并返回每条记录的ID列表
        :param data_list: 记录列表，每条记录为字典
        """
        if not data_list:
            return []
        keys = ", ".join(data_list[0].keys())
        placeholders = ", ".join(["?"] * len(data_list[0]))
        sql = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        cursor = self.conn_db.cursor()
        cursor.executemany(sql, [tuple(data.values()) for data in data_list])
        self.conn_db.commit()
        # SQLite 不支持直接返回所有插入ID，这里用一个简单算法推算
        last_id = cursor.lastrowid
        rowcount = cursor.rowcount
        return list(range(last_id - rowcount + 1, last_id + 1))

    @safe_connect
    def update_one(self, table_name, data, condition, upsert=False):
        """
        只修改查询到的第一条记录，如果未查到记录且 upsert 为 True，则插入一条新记录
        """
        # 先查询符合条件的一条记录
        row = self.first(table_name, condition=condition, fields=['rowid'])
        if not row:
            if upsert:
                return self.insert_one(table_name, data)
            return 0
        rowid = row['rowid']
        set_clause = ", ".join([f"{key}=?" for key in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE rowid=?"
        cursor = self.conn_db.cursor()
        cursor.execute(sql, tuple(data.values()) + (rowid,))
        self.conn_db.commit()
        return cursor.rowcount

    @safe_connect
    def update_many(self, table_name, data, condition):
        """
        更新所有符合条件的记录
        """
        set_clause = ", ".join([f"{key}=?" for key in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        cursor = self.conn_db.cursor()
        cursor.execute(sql, tuple(data.values()))
        self.conn_db.commit()
        return cursor.rowcount

    @safe_connect
    def delete_one(self, table_name, condition):
        """
        删除符合条件的单个记录（通过子查询限定只删除一条）
        """
        # SQLite不支持直接对DELETE语句使用LIMIT，此处通过rowid子查询实现
        subquery = f"SELECT rowid FROM {table_name} WHERE {condition} LIMIT 1"
        sql = f"DELETE FROM {table_name} WHERE rowid IN ({subquery})"
        cursor = self.conn_db.cursor()
        cursor.execute(sql)
        self.conn_db.commit()
        return cursor.rowcount

    @safe_connect
    def delete_many(self, table_name, condition):
        """
        删除符合条件的所有记录
        """
        sql = f"DELETE FROM {table_name} WHERE {condition}"
        cursor = self.conn_db.cursor()
        cursor.execute(sql)
        self.conn_db.commit()
        return cursor.rowcount

    @safe_connect
    def query(self, table_name, sql_query):
        """
        执行原始 SQL 查询, 返回字典列表
        """
        cursor = self.conn_db.execute(sql_query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# 示例用法
if __name__ == '__main__':
    # 获取单例对象
    db = SimpleSqlite()

    # 示例：打印当前附加数据库列表
    print("数据库列表：", db.get_dbs())

    # 示例：创建表（如果不存在）
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    );
    """
    db.conn_db.execute(create_table_sql)
    db.conn_db.commit()

    # 示例：插入数据
    user_id = db.insert_one("users", {"name": "Alice", "age": 30})
    print("插入用户ID:", user_id)

    # 示例：查询第一条记录
    user = db.first("users", condition="age > 20", order_by="id DESC")
    print("查询第一条记录:", user)

    # 示例：更新单条记录
    rows_updated = db.update_one("users", {"age": 31}, condition="name='Alice'")
    print("更新条数:", rows_updated)

    # 查询所有用户
    users = db.all("users")
    print("所有用户:", users)

    # 最后关闭连接
    db.close()
