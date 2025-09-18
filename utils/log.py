"""
日志记录
日志回滚
设置日志回滚
"""
import os
import sys
import datetime

def log_rollback(path, mode=1):
    """
    日志会馆暂时忽略
    :param path:
    :param mode:
    :return:
    """
    pass


def log(info, level=1, sub_path="sys", is_print=True):
    """
    文件日志： storage/logs/sys/2023-12-12.log
    :param level: 等级
    :param info:
    :param sub_path:
    :param is_print
    :return:
    """
    path = "./storage/logs"
    full_path = "%s/%s" % (path, str(sub_path).strip("/"))
    # 不存在则创建
    if not os.path.exists(full_path):
        for i in range(3):
            try:
                os.makedirs(full_path)
            except Exception as e:
                pass

    log_full_path = "%s/%s.log" % (full_path, str(datetime.datetime.now().strftime('%Y-%m-%d')))
    if level == 1:
        mark = '-'
    if level == 2:
        mark = '*'
    if level == 3:
        mark = '**'
    if level == 4:
        mark = '***'
    else:
        mark = "-"

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = "[%s]%s%s\n" % (now, mark, info)
    if is_print:
        print(msg)

    with open(log_full_path, 'a+', encoding="utf-8") as f:
        f.writelines(msg)


def error_log(info, level=2):
    log(info, level=level, sub_path="error")
