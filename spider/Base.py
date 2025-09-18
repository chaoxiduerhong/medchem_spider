# -*- coding:utf-8 -*-
import requests
import traceback
import cloudscraper
import time
import os
import re
import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import utils.common
from config import gpt_conf
from spider.NaturalAction import NaturalPageAction
from spider.PathwayAction import PathwayPageAction
from spider.logs.syslog import SysLog

from models import MProduct, MCatalog, MTask, MProductsCategory


class Base:
    """
    瓶子图处理
    源中添加一个字段：processing_img:
    """
    def __init__(self, thread_lock, entry_url):
        self.mark = None
        self.lock = thread_lock
        self.entry_url = entry_url
        self.thread_name = self.get_thread_name(self.entry_url)
        self.lock = thread_lock
        self.proxies = None
        self.sysLog = SysLog(thread_lock=self.lock, browser_port=self.thread_name, mark=self.mark)

        # 测试bid
        self.test_cid = "20250918153332-ID8M-RTkJ"

    def get_thread_name(self, url:str):
        """
        返回一个标准的线程名称。
        """
        url = url.replace(".html", "")
        url = url.replace(" ", "-")
        url = url.replace("%20", "-")
        url = url.split("/")
        url = url[-1]
        url = url.lower().strip()
        return url

    def get_url_path(self, url):
        parsed = urlparse(url)
        path = parsed.path.strip("/")  # 去掉开头的斜杠
        path = path.strip().replace(".html", "")
        return path

    def get_query_url(self, url):
        """
        保留路径部分和参数
        移除最前面的/ 全部转小写
        """
        parsed = urlparse(url)

        # 只保留路径 + 参数（含 query）
        result = parsed.path
        if parsed.query:
            result += "?" + parsed.query

        return result.strip("/").lower()

    def get_catalog_name_by_url(self, url:str):
        """
        获取不带html的path，全部转小写。
        将空格转化为横线，将/转化为__
        该方案兼容 /Targets/GPR119/effect/agonist.html?page=2 这种地址
        """
        path = self.get_url_path(url)
        path = path.lower().strip()
        path_obj = path.split("/")
        new_path = ""
        for item in path_obj:
            item = item.replace("%20", " ")
            item = item.strip()
            item = item.replace(" ", "-")
            new_path = f"{new_path}__{item}"
        return new_path.strip("_").lower()

    def waiting(self, ts):
        self.sysLog.log(f"Will SLEEP FOR {ts} seconds")
        time.sleep(ts)

    def save(self, data, bid=None):
        pass


    def proxy_issue(self):
        """
        下发代理
        """
        def check_proxy_status():
            """
            访问接口文档：接口文档请求状态200 认为是成功的。否则认为是失败的
            """
            try:
                scraper = cloudscraper.create_scraper()  # returns a requests.Session object
                url = "https://www.medchemexpress.com"
                proxies = self.proxies
                print("current proxies", proxies)
                response = scraper.get(url, proxies=proxies)
                if response.status_code == 200:
                    return True
                return False
            except:
                print(traceback.format_exc())
                return False

        with self.lock:
            idx = 0
            while True:
                idx = idx + 1
                if idx > 5:
                    print("proxy_issue Failed!")
                    break

                try:

                    req_url = f"{gpt_conf.remote_server}/proxy_issue_random"
                    print(f"proxy_issue_random: {req_url}")
                    resp = requests.get(url=req_url, timeout=3)
                    resp_json = json.loads(resp.content)
                    proxy_data = resp_json['data']
                    proxy_address = "http://%s:%s" % (gpt_conf.proxy_host, proxy_data['port'])
                    self.proxies = {"http": proxy_address, "https": proxy_address}

                    if check_proxy_status():
                        print("***********-> proxy success!, source_type:%s, remarks:%s" % (proxy_data['source_type'], proxy_data['remarks']))
                        return True

                    print(f"############->proxy failed!, retry {idx}/5")
                except Exception as e:
                    print("proxy retry ...")
                    # print(traceback.format_exc())
        return False

    def get_page_content(self, url):
        # 5次尝试机会
        self.sysLog.log(f"get_page_content URL: {url}")
        idx = 0
        while True:
            idx = idx + 1
            if idx > 5:
                return None
            try:
                scraper = cloudscraper.create_scraper()  # returns a requests.Session object
                response = scraper.get(url)
                if response.status_code == 200:
                    return response.content
                else:
                    time.sleep(4)
                    continue
            except Exception as e:
                # 重新切换代理尝试
                self.proxy_issue()
                time.sleep(3)
        return None


    def handle(self, task):
        """
        开始爬取

        解析数据：
        当前页为url中page存在并且大于1，则不爬取分类

        """
        # 下发一个可用的代理
        self.proxy_issue()
        if not task['spider_url'].startswith("https://"):
            task['spider_url'] = f"https://www.medchemexpress.com/{task['spider_url'].strip('/')}"
        self.sysLog.log("下发代理成功，准备请求页面：%s" % task['spider_url'])


        # 获取当前任务下未执行爬取的页面
        content = self.get_page_content(task['spider_url'])
        if not content:
            # TODO 详细的处理
            return {
                "status": "failed"
            }

        soup = BeautifulSoup(content, 'html.parser')

        # 检测页面类型
        group_name = self.get_group_name()
        if group_name == "pathway":
            Action = PathwayPageAction(thread_lock=self.lock, mark=self.mark, task_name=self.thread_name, soup=soup, url=task['spider_url'])
            resp_data = Action.parse()
        elif group_name == "natural":
            Action = NaturalPageAction(thread_lock=self.lock, mark=self.mark, task_name=self.thread_name,
                                                soup=soup, url=task['spider_url'])
            resp_data = Action.parse()

            pass
        else:
            return None

        # print(json.dumps(resp_data, ensure_ascii=False, indent=4))
        print(resp_data)

        # 数据解析
        if resp_data:
            # 分类处理
            if "catalog" in resp_data and (task['catalog_processing'] != "completed" or self.test_cid):
                # 存储当前分类
                if "current_data" in resp_data['catalog'] and resp_data['catalog']['current_data']:
                    current_catalog = resp_data['catalog']['current_data']
                    catalog_title = current_catalog['title']
                    # 上一级
                    origin_url = task['spider_url']
                    url_path = self.get_url_path(task['spider_url'])
                    shor_url = url_path.split("/")[-1]

                    # 存储， 检测是否存在
                    exists = MCatalog.first(condition={
                        "c_key": task['c_key']
                    })
                    if not exists:
                        MCatalog.add_one(data={
                            "type": task['type'],
                            # c_key 是唯一的。不同分页获取的c_key 是一致的。 c_key 是 c_name md5后的结果
                            "c_key": task['c_key'],
                            "c_p_key": task['c_p_key'],
                            "c_name": task['c_name'],
                            "name": catalog_title,
                            "origin_url": origin_url,
                            "url_path": url_path,
                            "shor_url": shor_url,
                            # 包含了统计的名称
                            'name_with_count': task['title'],
                        })
                # 创建分类的任务
                if "queue_data" in resp_data['catalog'] and resp_data['catalog']['queue_data']:
                    queue_data = resp_data['catalog']['queue_data']



                    for item_data in queue_data:
                        catalog_name = self.get_catalog_name_by_url(item_data['link'])
                        catalog_key = utils.common.md5(catalog_name)
                        item_uid = utils.common.md5(self.get_query_url(item_data['link']))
                        if not MTask.first(condition={
                            "uid": item_uid
                        }):
                            MTask.add_one(data={
                                # 将完整url md5后的值
                                "type": item_data['type'],

                                "processing": "waiting",
                                "catalog_processing": "waiting",
                                "product_processing": "waiting",

                                # 组名称
                                "group_name": group_name,
                                # 任务名-当前任务队列的名称 也是线程名称
                                "name": self.thread_name,
                                "title": item_data['title'],
                                "spider_url": item_data['link'],

                                # url唯一性
                                'uid': item_uid,

                                "c_key": catalog_key,
                                "c_p_key": task['c_key'],
                                "c_name": catalog_name,
                            })

                        if "children" in item_data and item_data['children']:
                            for child_item in item_data['children']:
                                sub_catalog_name = self.get_catalog_name_by_url(child_item['link'])
                                sub_item_uid = utils.common.md5(self.get_query_url(child_item['link']))
                                if not MTask.first(condition={
                                    "uid": item_uid
                                }):
                                    MTask.add_one(data={
                                        "type": item_data['type'],
                                        "processing": "waiting",
                                        "catalog_processing": "waiting",
                                        "product_processing": "waiting",

                                        # 组名称
                                        "group_name": group_name,
                                        # 任务名-当前任务队列的名称 也是线程名称
                                        "name": self.thread_name,
                                        "title": child_item['title'],
                                        "spider_url": child_item['link'],

                                        # url 唯一性
                                        'uid': sub_item_uid,

                                        "c_name": sub_catalog_name,
                                        "c_key": utils.common.md5(sub_catalog_name),
                                        "c_p_key": catalog_key,
                                    })

            # 将原来的状态更新 cid 是任务的唯一值，必须根据该cid来更新 而不是ckey
            MTask.update_one(data={
                "catalog_processing": "completed"
            }, condition={
                "cid": task['cid']
            })


            # 产品处理
            if "product" in resp_data and (task['product_processing'] != "completed" or self.test_cid):
                # 保存当前产品
                if "current_data" in resp_data['product'] and resp_data['product']['current_data']:
                    current_product = resp_data['product']['current_data']
                    for item_data in current_product:

                        cat_no = item_data['cat_no']
                        if cat_no:
                            # 保存产品
                            exists = MProduct.first(condition={
                                "cat_no": cat_no
                            })
                            if not exists:
                                MProduct.add_one(data={
                                    "cat_no": cat_no,
                                    'product_name': item_data['product_name'],
                                    'shor_url': item_data['shor_url'],
                                    'cas_no': item_data['cas_no'],
                                    'effect': item_data['effect'],
                                    'purity': item_data['purity'],
                                })
                            # 保存产品关联
                            exists = MProductsCategory.first(condition={
                                "cat_no": cat_no,
                                'c_key': task['c_key']
                            })
                            if not exists:
                                MProductsCategory.add_one(data={
                                    "cat_no": cat_no,
                                    'c_key': task['c_key'],
                                    'c_name': task['c_name'], # 方便展示数据
                                })

                # 保存当前产品任务
                if "queue_data" in resp_data['product'] and resp_data['product']['queue_data']:
                    queue_data = resp_data['product']['queue_data']
                    if queue_data:
                        # queue_data ： [2, max]
                        # 检测是否存在：检测最大页面是否存在，最大页面存在认为整个都存在。则无需创建
                        # 如果最大页面不存在则创建
                        start_page = queue_data[0]
                        end_page = queue_data[1]
                        if end_page > 1:
                            base_url = task['spider_url'].split('?', 1)[0]
                            end_full_url = f"{base_url}?page={end_page}"
                            # 检测是否存在：检测最大页面是否存在，最大页面存在认为整个都存在。则无需创建
                            exists = MTask.first(condition={
                                "uid": utils.common.md5(self.get_query_url(end_full_url))
                            })
                            if not exists:
                                for current_page in range(queue_data[0], queue_data[1]+1):
                                    full_url = f"{base_url}?page={current_page}"
                                    uid = utils.common.md5(self.get_query_url(full_url))
                                    sub_exists = MTask.first(condition={
                                        "uid": uid
                                    })
                                    if not sub_exists:
                                        product_c_name = self.get_catalog_name_by_url(full_url)
                                        MTask.add_one(data={
                                            "type": task['type'],

                                            "processing": "waiting",
                                            "catalog_processing": "completed",
                                            "product_processing": "waiting",

                                            # 组名称
                                            "group_name": group_name,
                                            # 任务名-当前任务队列的名称 也是线程名称
                                            "name": self.thread_name,
                                            "title": task['title'],
                                            "spider_url": full_url,
                                            "uid": uid,

                                            "c_name": product_c_name,
                                            "c_key": utils.common.md5(product_c_name),
                                            # 注意：多个分页属于同一级。
                                            "c_p_key": task['c_p_key'] if task['c_key'] == utils.common.md5(product_c_name) else task['c_key'],
                                        })
            # 将原来的状态更新
            MTask.update_one(data={
                "product_processing": "completed"
            }, condition={
                "cid": task['cid']
            })

            # 更新任务状态：如果分类和产品都爬取完成，则更新为完成
            MTask.update_one(data={
                "processing": "completed"
            }, condition={
                "cid": task['cid']
            })
        return True


    def get_task(self):

        return MTask.getFirstData(self.thread_name, self.test_cid)




    def get_group_name(self):
        """
        获取分组名称
        """
        groups = gpt_conf.page_group
        for group_name in groups:
            if self.thread_name in groups[group_name]:
                return group_name
        return None


    def init_task(self):
        group_name = self.get_group_name()
        c_name = self.get_catalog_name_by_url(self.entry_url)
        c_key = utils.common.md5(c_name)
        uid = utils.common.md5(self.get_query_url(self.entry_url))
        MTask.init_task(spider_url=self.entry_url, task_name=self.thread_name, group_name=group_name, c_name=c_name, c_key=c_key, uid=uid)

    def query(self):
        """
        检测任务页面是否存在
        如果任务页面不存在，则以入口为创建任务
        """
        is_first = True
        while True:
            try:
                # 首次运行尝试初始化。
                if is_first:
                    self.init_task()
                    is_first = False
                # 获取一个任务
                task = self.get_task()
                if not task:
                    self.sysLog.log("not find task")
                    time.sleep(50)
                    continue
                # TODO 检测任务关键字段

                # 先切换代理，并且检测代理的可用性。如果代理可用则直接用该代理

                # 处理这个任务
                self.sysLog.log("current task %s" % task['spider_url'])
                self.handle(task)
                self.sysLog.log("current task complete！next task...")
                # # TODO 调试模式。
                if self.test_cid:
                    break

            except:
                print(traceback.format_exc())
                self.sysLog.err_log(f"未知异常原因，程序等待10分钟再次运行。Error:%s" % traceback.format_exc())
                time.sleep(600)