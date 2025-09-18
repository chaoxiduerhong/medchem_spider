"""
获取和更新配置文件
"""
import os
import json
import sys


def get_setting(filename, key="*", value=""):
    file_path = "./storage/data/%s.json" % filename
    # print(f"DATA.py -> get_setting() -> file_path {file_path}, key(type)={key}({type(key)})")

    if not os.path.isfile(file_path):
        # if filename == "browser":
        #     print(f"not isfile {file_path}")
        return value
    with open(file_path) as f:
        try:
            data = json.load(f)
        except Exception as e:
            # if filename == "browser":
            #     print(f"json load file ERR: {e}")
            return value
        if key == "*":
            # if filename == "browser":
            #     print(f"key == * return whole data  {data}")
            return data
        if key in data:
            # if filename == "browser":
            #     print(f"return key {key} only => {data[key]}")
            return data[key]
    return value


# 设置配置
def set_setting(filename, key, value):
    file_path = "./storage/data/%s.json" % filename
    data = get_setting(filename, "*")
    if not data:
        data = {}
    data[key] = value
    with open(file_path, "w", encoding="utf-8") as f:
        if "win" not in sys.platform:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(json.dumps(data, indent=4))


def clear_setting(filename):
    file_path = "./storage/data/%s.json" % filename
    with open(file_path, "w", encoding="utf-8") as f:
        if "win" not in sys.platform:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write("")

def save_setting(filename, data):
    file_path = "./storage/data/%s.json" % filename
    with open(file_path, "w", encoding="utf-8") as f:
        if "win" not in sys.platform:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.write(json.dumps(data, indent=4))

def save_data(filename, value):
    file_path = "./storage/data/%s" % filename
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{value}\n")

def clear_data(filename):
    file_path = "./storage/data/%s" % filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")