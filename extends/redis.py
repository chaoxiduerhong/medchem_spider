# coding: utf-8
# Desc: redis

import time
import redis
from config.database import DBConfig


class SimpleRedis:
    def __init__(self, connect_dbname="default"):
        self.connect_dbname = connect_dbname
        self.redisConn = redis.Redis(
            host=DBConfig.redis[self.connect_dbname]['host'],
            port=DBConfig.redis[self.connect_dbname]['port'],
            password=DBConfig.redis[self.connect_dbname]['password'],
            db=DBConfig.redis[self.connect_dbname]['db'],
        )

    def connect_redis(self):
        self.redisConn = redis.Redis(
            host=DBConfig.redis[self.connect_dbname]['host'],
            port=DBConfig.redis[self.connect_dbname]['port'],
            password=DBConfig.redis[self.connect_dbname]['password'],
            db=DBConfig.redis[self.connect_dbname]['db']
        )

    def redisServer(self):
        """
        如果断开，应该有重连机制
        :return:
        """
        return self.redisConn

    def re_connect_redis(self, num=2, stime=3):  # 重试连接总次数为1天,这里根据实际情况自己设置,如果服务器宕机1天都没发现就......
        _number = 0
        _status = True
        while _status and _number <= num:
            try:
                self.redisConn.ping()  # cping 校验连接是否异常
                _status = False
            except Exception as e:
                print("Missing connect! connecting...")
                if self.connect_redis() is True:  # 重新连接,成功退出
                    _status = False
                    break
                _number += 1
                time.sleep(stime)

    def close(self):
        self.redisConn.close()


