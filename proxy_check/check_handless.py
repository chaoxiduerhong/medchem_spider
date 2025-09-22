# encoding=utf-8
"""
API key not valid  出现这个 认为账号无效，切换一个其他的来检测


Permission denied 账号权限不足或者被禁用，切换其他key检测


PERMISSION_DENIED
INVALID_ARGUMENT


"""

import threading
import time
import traceback
import requests
import json
import random
import cloudscraper
import utils.data
from config.gpt import gptConf
from models import MProxyQueue
from config.keys import keysConf

lock = threading.Lock()
proxy_server = "http://" + gptConf.proxy_host

class RequestThread(threading.Thread):
    def __init__(self, key):
        threading.Thread.__init__(self)
        self.thread_id = str(key)
        self.proxy_info = None
        self.running_list = None
        self.proxy_server = gptConf.proxy_server
        self.mark = ""
        self.report_ts = 0
        self.sleep_ts = 1800

    @staticmethod
    def get_indexID_list(data):
        result = []
        if data:
            for item in data:
                if isinstance(item, dict):
                    item_data = item
                else:
                    item_data = data[item]
                if "indexId" in item_data and item_data['indexId'] not in result:
                    result.append(item_data['indexId'])
        return result


    @staticmethod
    def check(current_proxy):
        """
        https://www.medchemexpress.com
        """
        if "port" not in current_proxy:
            return False
        port = current_proxy['port']
        proxy = f"{proxy_server}:{port}"
        print("check proxy server", proxy)
        try:
            proxies = {"http": proxy, "https": proxy}
            scraper = cloudscraper.create_scraper()  # returns a requests.Session object
            url = "https://www.medchemexpress.com"
            print("current proxies", proxies)
            response = scraper.get(url, proxies=proxies)
            # 排除中国的
            if response.status_code == 200 and "medchemexpress.cn" not in response.url:
                return True
            return False
        except:
            return False

    #
    def get_proxy_list(self):
        """
        获取当前线程的代理队列
        """
        result = []
        proxy_list = MProxyQueue.get()
        for current_proxy in proxy_list:
            indexId = current_proxy['indexId']
            indexId_end = str(indexId)[-1]
            if indexId_end == self.thread_id:
                result.append(current_proxy)
        return result

    def get_latest_proxy(self):
        """
        获取线上运行的最新队列
        """
        result = []
        url = f"{proxy_server}:8045/running_proxy"
        resp = requests.get(url)
        data = resp.content.decode("utf-8")
        proxy_dicts = json.loads(data)
        proxy_dicts = proxy_dicts['data']
        for indexID in proxy_dicts:
            proxy_dict = proxy_dicts[indexID]
            item = {
                "indexId": indexID,
                'remarks': proxy_dict['remarks'],
                'subid': proxy_dict['subid'],
                'source_type': proxy_dict['source_type'],
                'status': 'waiting',
                'pid': proxy_dict['pid'],
                'port': proxy_dict['proxy_http_port']
            }
            result.append(item)
        return result

    def get_local_proxy(self):
        """
        获取数据库中所有代理
        """
        return MProxyQueue.get()

    def save_proxy(self, data):
        """
        更新：只更新port。
        """
        condition ={
            'indexId': data['indexId']
        }
        if MProxyQueue.first(condition=condition):
            MProxyQueue.update_one(data={
                'port': data['port']
            }, condition=condition)
        else:
            MProxyQueue.add_one(data)

    def plog(self, info):
        mark = f"[Thread_%s][{utils.common.get_now_str()}]-%s" % (self.thread_id, self.mark)
        print("%s - %s" % (mark, info))

    def auto_merge_proxy(self):
        """
        合并后的数据，必须是启动的。
        """
        with lock:
            latest_data = self.get_latest_proxy()
            local_data = self.get_local_proxy()
            latest_data_ids = self.get_indexID_list(latest_data)
            local_data_ids = self.get_indexID_list(local_data)
            add_total = 0
            del_total = 0
            update_total = 0

            # 线上不存在，直接退出程序
            if not latest_data:
                self.plog("----error --- 代理检测出现了故障， 程序退出-----")
                exit()

            # 本地不存在，全部add
            if latest_data and not local_data:
                for item in latest_data:
                    self.save_proxy(item)
            elif latest_data and local_data:
                # 最新的不在本地 直接新增
                for latest_item in latest_data:
                    latest_id = latest_item['indexId']
                    # 更新或者新增
                    self.save_proxy(latest_item)
                    if latest_id not in local_data_ids:
                        add_total = add_total + 1
                    else:
                        update_total = update_total + 1

                for local_id in local_data_ids:
                    if local_id not in latest_data_ids:
                        MProxyQueue.delete(condition={
                            "indexId": local_id
                        })
                        del_total = del_total + 1
            self.plog("自动化合并代理结束, 共新增了代理%s, 更新了代理:%s， 移除了无效代理:%s" % (add_total, update_total, del_total))

    def run(self):
            while True:
                self.auto_merge_proxy()
                # 获取所有的队列
                proxy_list = self.get_proxy_list()
                proxy_total = len(proxy_list)
                if proxy_total == 0:
                    self.plog("proxy queue empty...")
                    time.sleep(1800)
                    continue
                self.plog(f"Found {proxy_total} proxy to be test, ")
                idx = 0
                try:
                    for current_proxy in proxy_list:
                        idx = idx + 1
                        indexId = current_proxy['indexId']
                        self.mark = "[%s/%s] - [remarks: %s, source_type:%s, indexId:%s]" % (idx, proxy_total,  current_proxy['remarks'], current_proxy['source_type'], indexId)
                        self.plog(f"---START---")

                        start_ts = utils.common.get_second_utime()
                        status = self.check(current_proxy)
                        end_ts = utils.common.get_second_utime()
                        if status:
                            MProxyQueue.update_one(data={
                                'status': "running",
                                'success_ts': utils.common.get_second_utime(),
                                'duration_ts': end_ts - start_ts,
                                'running_ts': 0
                            }, condition={
                                "indexId": current_proxy['indexId']
                            })
                            self.plog(f"check success!")
                        else:
                            MProxyQueue.update_one(data={
                                'status': "fault",
                                "api_fault_num": (current_proxy['api_fault_num'] + 1) if 'api_fault_num' in current_proxy else 1
                            }, condition={
                                "indexId": current_proxy['indexId']
                            })
                            self.plog(f"check failed!")
                        self.plog(f"---END NEXT...---")
                    self.plog("本次检测结束。sleep 1h continue")

                except Exception as e:
                    self.plog("匹配异常:%s" % e)

                # 每轮sleep 秒
                time.sleep(self.sleep_ts)


def start():
    print("---------START-----------")
    # Create 10 threads
    threads = []
    for key in range(0, 10):
        thread = RequestThread(key)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("---------END-----------")
