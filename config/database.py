"""
数据库相关配置
支持 redis  mongodb mysql 数据库的配置
"""

# -*- coding:utf-8 -*-
# Author： 1186969412@qq.com
# Desc: database configuration

from utils import env
import subprocess,re

class DBConfig:
    db_type: str = "mongodb"
    cache_type: str = "redis"

    @staticmethod
    def get_db_server_ipv4():
        ipv4 = None
        try: 
            process = subprocess.Popen(['ping', '-4', 'zq-02'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            stdout_str = stdout.decode('gbk')
            ipv4_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', stdout_str)
            if ipv4_match:
                ipv4 = ipv4_match.group(1)
                print(f"成功获取 DB-Server IPv4 地址: {ipv4}")
        except Exception as e:
            print(f"获取 DB-Server IPv4 地址时发生错误：{e}")
        if not ipv4:
            ipv4 = env("PRODUCTS_MONGODB_HOST", "192.168.100.13")

        return ipv4


    redis: dict = {
        "default": {
            'host': env("REDIS_HOST", "127.0.0.1"),
            'port': env("REDIS_PORT", 6379),
            'db': env("REDIS_DB", 3),
            'user': "",
            'password': env("REDIS_PASSWORD", ""),
        }
    }
    mongodb: dict = {
        "default": {
            'host': env("PRODUCTS_MONGODB_HOST", "192.168.0.123"),
            'port': env("PRODUCTS_MONGODB_PORT", 27017),
            'db': env("MONGODB_DB", "smolecule"),
            'user': env("PRODUCTS_MONGODB_USER", ""),
            'password': env("PRODUCTS_MONGODB_PASSWORD", ""),
        },
        "products": {
            'host': env("PRODUCTS_MONGODB_HOST", "192.168.0.123"),
            'port': env("PRODUCTS_MONGODB_PORT", 32770),
            'db': env("PRODUCTS_MONGODB_DB", "smolecule"),
            'user': env("PRODUCTS_MONGODB_USER", ""),
            'password': env("PRODUCTS_MONGODB_PASSWORD", ""),
        },
    }

    mysql: dict = {
        "default": {
            'host': env("MYSQL_HOST", "127.0.0.1"),
            'port': env("MYSQL_PORT", 3306),
            'db': env("MYSQL_DB", "test"),
            'user': "",
            'password': env("MYSQL_PASSWORD", ""),
        }
    }


