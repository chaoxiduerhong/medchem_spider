# coding: utf-8
# Desc: Commonly used functions

import datetime
import random
import string
import hashlib
import time
import os
import re
import nltk
import platform

def get_rand_str(len=6):
    return ''.join(random.sample(string.digits + string.ascii_letters, len))


def get_now_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_now_str(f='%Y-%m-%d %H:%M:%S'):
    return str(datetime.datetime.now().strftime(f))


def formatTime(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def timeToStr(ts):
    return str(ts.strftime("%Y-%m-%d %H:%M:%S"))


def microsecond():
    return int(time.time() * 1000)


def ts():
    return int(time.time() * 1000000)


def get_second_utime():
    # unix 秒级时间戳
    return int(round(time.time()))


def md5(text):
    if not text:
        return text
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()


def runcmd(command, checkStr=None):
    try:
        import subprocess
        time.sleep(1)
        ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1200)
        if ret.returncode == 0:
            if checkStr:
                if checkStr.lower() in str(ret.stdout).lower():
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
    except:
        return False


# 检测本程序是否执行
def checkRunning(checkStr):
    import sys
    import subprocess
    if "win" in sys.platform:
        return False
    ret = subprocess.run("ps aux|grep python3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=1200)
    if str(ret.stdout).count(checkStr) > 1:
        return True
    return False


def checkMultiRunning(checkStr, count=1):
    """
    该函数不对win系统进行判断，只针对linux判断
    检查组合命令运行状态。组合命令往往会生成多个相同的命令,包含其中一条 bin/sh -c + 完整命令。
    过滤方案：|grep -v /bin/sh
    :param checkStr:
    :param count:
    :return:
    """
    import sys
    import subprocess
    if "win" in sys.platform:
        return False
    ret = subprocess.run("ps aux|grep python3|grep -v /bin/sh", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=1200)
    if str(ret.stdout).count(checkStr) > count:
        return True
    return False


# 检测其他程序是否执行
def checkOtherRunning(checkStr):
    import sys
    import subprocess
    if "win" in sys.platform:
        return False
    ret = subprocess.run("ps aux|grep python3", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=1200)
    if str(ret.stdout).count(checkStr) > 0:
        return True
    return False


def listSplit(items, n):
    """
    站点分组
    """
    k, m = divmod(len(items), n)
    return [items[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def get_similarity(str1, str2):
    if str1 and str2:
        str1 = str1.lower()
        str2 = str2.lower()
        lev_distance = nltk.edit_distance(str1, str2)
        return 1 - (lev_distance / max(len(str1), len(str2)))
    else:
        return 0


def get_cid():
    return "%s-%s-%s" % (get_now_str('%Y%m%d%H%M%S'), get_rand_str(4), get_rand_str(4))


def is_float_str(val):
    reg = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
    retFloat = reg.match(str(val))
    if retFloat:
        return True
    return False


def env(key, default=None):
    path = "./env"
    if not os.path.exists(path):
        return default
    with open(path) as file_obj:
        for line in file_obj:
            lineStr = str(line)
            if "=" in str(lineStr):
                lineArr = lineStr.split('=')
                filed = lineArr[0].strip()
                value = lineArr[1].strip()
                value = value.strip('"')
                if value == "True" or value == "true":
                    value = True
                elif value == "False" or value == "false":
                    value = False
                elif value == "None" or value == "none":
                    value = None
                # 整数返回
                elif value.isdigit():
                    value = int(value)
                # 小数返回
                elif is_float_str(value):
                    value = float(value)
                if key == filed:
                    return value
    return default


def template(template_name,default=None):
    path = "./%s" % template_name
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding="utf-8") as file:
        return file.read().strip()


def sleep_ms(ms):
    seconds = ms / 1000.0
    time.sleep(seconds)


def get_sys_uname():
    try:
        hostname = platform.uname().node
        return hostname
    except:
        return "unknown"

def action_wait(mints=500, maxts=1000):
    milliseconds = random.randint(mints, maxts)
    sleep_ms(milliseconds)