# -*- coding:utf-8 -*-
"""
支持浏览器管理 + 数据上报接口管理
"""
import time
import psutil
import json
import random
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import utils
import utils.common
from spider.browser import BrowserManager
import threading
from utils import log
from config.gpt import gptConf
from models import MProxyQueue

app = Flask(__name__, static_url_path='')
CORS(app, supports_credentials=True)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TEMPLATES_FOLDER'] = "templates"
app.config['STATIC_FOLDER'] = "static"

lock = threading.Lock()
report_ts = 0

def arg(rkey=None, default=None):
    jsonData = request.get_data()
    formData = request.values.to_dict()
    resData = {}
    if jsonData:
        jsonData = json.loads(jsonData.decode("utf-8"))
        resData = jsonData
    elif formData:
        resData = formData
    if not rkey and jsonData:
        return jsonData
    if not rkey and formData:
        return formData

    if rkey is not None:
        if rkey in resData:
            if not resData[rkey]:
                if default is None:
                    return None
                else:
                    return default
            return resData[rkey]
        else:
            if default is None:
                return None
            else:
                return default
    else:
        if not resData:
            if default is not None:
                return default
            else:
                return None
        return resData


@app.route('/', methods=['GET'])
def index():
    """
    数据统计
    """

    memory = psutil.virtual_memory()
    memory_use_percent = "%s %%" % memory.percent
    memory_total = "%s" % (int(memory.total) / (1024.0 ** 3))
    memory_available = "%s GB" % (int(memory.available) / (1024.0 ** 3))
    data = {
        "memory_use_percent": memory_use_percent,
        "memory_total": memory_total,
        "memory_available": memory_available
    }
    return render_template("index.html", **data)


@app.route('/proxy_issue_random', methods=['GET'])
def proxy_issue_random():
    """
    直接获取一个随机代理。无需关心代理的质量
    """
    data_list = MProxyQueue.get(condition={
        "status": "running"
    })
    data = None
    if data_list:
        data = random.choice(data_list)
        data['_id'] = str(data['_id'])
    response_data = {'msg': 'success', 'code': 200, 'data': data}
    return jsonify(response_data)



def start():
    # 检测本程序正在运行，则退出
    print("address: 127.0.0.1:8053")
    app.run(
        host="0.0.0.0",
        port=8053,
        debug=gptConf.debug
    )


# if __name__ == '__main__':
#     start()
