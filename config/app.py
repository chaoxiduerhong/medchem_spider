# -*- coding:utf-8 -*-
# Desc: project app configuration

from utils import env


class appConf:
    debug: bool = env("DEBUG", True)

    """
    计划任务最小运行周期。单位秒
    """

    scheduled_loop_time: int = 5
    """
    计划任务日志记录级别。当小于等于该级别的情况下，才会写入数据库。否则只是打印
    1: 必须要写入的日志
    2: 一些次要的信息。
    3：调试日志
    """
    scheduled_cron_log_level: int = 1

    """
    search spider 开启的最大线程数量
    实际上最大线程数可能要比该值大1
    """
    search_spider_max_thread = 20

    """
    搜索页最大允许的结果数量，超过数量的不在查询详情
    """
    search_spider_max_detail: int = 10

    """
    1: 必须要写入的日志
    2: 一些次要的信息。
    3：调试日志
    """
    search_spider_log_level: int = 3

    # 最大日志天数，超过会将之前的删除
    log_max_day = 30

    # 清除日志方式：1 删除文件夹 2 删除文件
    log_clear_mode = 1

    # 日志根目录
    log_root_path = env("LOG_ROOT_PATH", "./storage/logs")

    # 用于存储cookie文件的json文件
    cookie_file_path = env("LOG_ROOT_PATH", "./storage/data")
    cookie_file_name = env("LOG_ROOT_PATH", "cookie.json")

    # 日志命名方式：默认按日期天来命名 2023-09-01.log
    log_file_name_type = env("LOG_FILE_NAME_TYPE", "date-day")
