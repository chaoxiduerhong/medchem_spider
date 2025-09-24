# -*- coding:utf-8 -*-
"""
所有的动作封装
soup分装
reques封装
"""
import json
import traceback
import time
import os
import json
import re
import math
from urllib.parse import urlparse


from bs4 import BeautifulSoup

from spider.logs.syslog import SysLog


class pageAction:
    def __init__(self, thread_lock, mark, task_name, soup: BeautifulSoup, url):
        self.mark = None
        self.lock = thread_lock
        self.sysLog = SysLog(thread_lock=self.lock, browser_port=task_name, mark=self.mark)
        self.lock = thread_lock
        self.mark = mark
        self.soup = soup
        self.url = url

    def waiting(self, ts):
        self.sysLog.log(f"Will SLEEP FOR {ts} seconds")
        time.sleep(ts)


    def get_current_catalog_name(self):
        """
        获取当前分类页的名称
        """
        try:
            return self.soup.select_one("div#category_tit > h1").get_text(strip=True)
        except Exception as e:
            print(traceback.format_exc())
            return None

    def get_url_path(self, url=None):
        if not url:
            url = self.url
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")  # 去掉开头的斜杠
        return path.strip().replace(".html", "")

    def parse_target_list(self):
        """
        获取id=target_list 的分类数据
        """
        try:
            ul = self.soup.find("ul", id="target_list")
            links = ul.find_all("a")
            result = [{"link": a.get("href"), "title": a.get_text(strip=True), "type": "category", "children": []} for a in links]
        except Exception as e:
            result = []
        return result

    def parse_cls_target_h3_href_list(self):
        """
        获取div class=target_list 下h3 的超链接包含的分类信息
        """
        result = []
        try:
            items = self.soup.find("div", class_="target_list").find_all("h3")
            for item in items:
                link = item.find("a").get("href")
                title = item.get_text(strip=True)
                result.append({"link": link, "title": title, "type": "group", "children": []})
        except Exception as e:
            pass
        return result

    def parse_label_list(self):
        """
        ul id = "label-list"
        """
        try:
            ul = self.soup.find("ul", id="label-list")
            links = ul.find_all("a")
            result = [{"link": a.get("href"), "title": a.get_text(strip=True), "type": "category", "children": []} for a in links]
        except Exception as e:
            result = []
        return result

    def parse_category__cls_isoform_list(self):
        """
        ul clss = isoform-list
        lambda tag: tag.has_attr("class") and tag["class"] == ["ddd"]
        """
        try:
            # ul = self.soup.find("ul", class_=lambda tag: tag.has_attr("class") and tag["class"] == ["isoform-list"])
            ul = self.soup.find(lambda tag: tag.name == "ul" and tag.get("class") == ["isoform-list"])
            links = ul.find_all("a")
            result = [{"link": a.get("href"), "title": a.get_text(strip=True), "type": "category", "children": []} for a in links]
        except Exception as e:
            print(traceback.format_exc())
            result = []
        return result

    def parse_effect_list_cls_effect_main(self):
        """
        div class = list-effect-main
        """
        try:
            ul = self.soup.find("div", class_="list-effect-main").find("ul")
            links = ul.find_all("a")
            result = [{"link": a.get("href"), "title": a.get_text(strip=True), "type": "effect", "children": []} for a in
                      links]
        except Exception as e:
            result = []
        return result

    def parse_product_list__cls_sub_ctg_list_con(self):
        """
        解析产品列表
        产品必须要的字段:
        cas_no
        cat_no
        product_name
        purity
        """
        result = []
        ul = self.soup.find("ul", class_="sub_ctg_list_con")
        if ul:
            li_soups = ul.find_all("li")
            try:
                for li_soup in li_soups:
                    cat_no = ""
                    product_name = ""
                    shor_url=""
                    cas_no=""
                    effect=""
                    purity=""
                    cat_no_soup = li_soup.select_one('dt[class*="pro_list_cat"]')
                    if cat_no_soup:
                        cat_no = cat_no_soup.get_text(strip=True)

                    product_info_soup = li_soup.select_one('dd[class*="pro_list_info"]')
                    if product_info_soup:
                        product_name_soup = li_soup.select_one('th[class*="pro_list_name"]')
                        if product_name_soup:
                            product_name = product_name_soup.get_text(strip=True)

                            product_link_soup = product_name_soup.a
                            if product_link_soup:
                                shor_url = self.get_url_path(product_link_soup.get('href'))

                        # cas_no 不同板块下面可能不一样
                        product_cas_soup = li_soup.select_one('th[class*="pro_list_cas"]')
                        if product_cas_soup:
                            cas_no = product_cas_soup.get_text(strip=True)
                        if not cas_no:
                            product_cas_soup = li_soup.select_one('th[class*="pro_list_type"]')
                            if product_cas_soup:
                                cas_no = product_cas_soup.get_text(strip=True)

                        product_purity_soup = li_soup.select_one('th[class*="pro_list_purity"]')
                        if product_purity_soup:
                            purity = product_purity_soup.get_text(strip=True)

                        product_effect_soup = li_soup.select_one('th[class*="pro_list_effect"]')
                        if product_effect_soup:
                            effect = product_effect_soup.get_text(strip=True)

                    result.append({
                        "cat_no": cat_no,
                        "product_name": product_name,
                        "shor_url": shor_url,
                        "cas_no": cas_no,
                        "effect": effect,
                        "purity": purity
                    })
            except Exception as e:
                result = []
        return result


    def parse_ui_pager__product_page(self):
        """
        解析产品分页
        input id=id="pageMaxNum"

        如果不存在 则 ui-pager这个方案
        """
        max_page = 0
        try:
            input_soup = self.soup.find("input", {"id": "pageMaxNum"})
            if input_soup and input_soup.get("value"):
                max_page = int(input_soup.get("value"))

            if not max_page:
                page_li = self.soup.find_all("li", class_="ui-pager")
                if page_li:
                    end_page_li = page_li[-1]
                    if end_page_li and end_page_li.get_text(strip=True):
                        max_page = int(end_page_li.get_text(strip=True))
            if not max_page:
                h2_s = self.soup.find("h2", class_="fl")
                match = re.search(r"\((\d+)\)", h2_s.get_text(strip=True))
                if match:
                    number = int(match.group(1))
                    if number:
                        max_page = math.ceil(int(number)/20)

        except Exception as e:
            pass
        return max_page

    def parse_list__cls_hot_list(self):
        """
        解析包含组的分类
        """
        try:
            item_soups = self.soup.find_all("div", class_="hot-list")[1:]
            sub_catalog = []
            for item_soup in item_soups:
                title = item_soup.find("h2").get_text(strip=True)
                link = ""
                list_main_soup = item_soup.find("div", class_="list-main")
                if list_main_soup:
                    children_soups = list_main_soup.find_all("a")
                    child_data = []
                    for child in children_soups:
                        sub_link = child.get("href")
                        sub_title = child.get_text(strip=True)
                        child_data.append({
                            "title": sub_title,
                            "link": sub_link,
                            "type": "category",
                            "children": []
                        })
                    sub_catalog.append({
                        "title": title,
                        "link": link,
                        "type": "group",
                        "children": child_data
                    })
            return sub_catalog

        except Exception as e:
            print(traceback.format_exc())
            self.sysLog.log(f"by NaturalProducts top get failed")


    def get_catalog(self):
        """
        获取页面数据。对页面进行数据爬取

        返回类型：分类 or 产品

        分两个集合：当前分类数，子页面链接

        当前下的子分类

        子级的写法

        {
            "title": "xxx",
            "link": "xxx"，
            "children": []
        }


        注意：
        link为空：代表当前可能有子节点 children
        children为空：代表当前页面不怕去其子节点
        """
        # 获取标题。标题获取不到 直接认为错误。返回空集合
        catalog_name = self.get_current_catalog_name()
        if not catalog_name:
            return  {
                "type": None,
                "data": None,
                "catalog": None,
                "status": "failed",
                "error": "page not find catalog_name",
                "product": None,
            }

        try:
            ul = self.soup.select_one("div.pathway_list ul")
            sub_catalog = []
            if ul:
                for a in ul.find_all("a", href=True):
                    href = a["href"]
                    text = a.get_text(strip=True)  # 去除空格和换行
                    sub_catalog.append({
                        "title": text,
                        "link": href,
                        "children": []
                    })
            return {
                "type": "catalog",
                "data": {
                    "title": catalog_name,
                },
                "catalog": sub_catalog,
                "product": None,
            }
        except:
            self.sysLog.log(f"by pathway top get failed")



        # NaturalProducts 顶级的写法
        # 特点 多级分类。但是注意第一个分类不是真正的分类
        try:
            item_soups = self.soup.find_all("div", class_="hot-list")[1:]
            sub_catalog = []
            for item_soup in item_soups:
                title = item_soup.find("h2").get_text(strip=True)
                link = ""
                list_main_soup = item_soup.find("div", class_="list-main")
                children_soups = list_main_soup.find_all("a")
                child_data = []
                for child in children_soups:
                    sub_link = child.get("href")
                    sub_title = child.get_text(strip=True)
                    child_data.append({
                        "title": sub_title,
                        "link": sub_link,
                        "children": []
                    })
                sub_catalog.append({
                    "title": title,
                    "link": link,
                    "children": child_data
                })

            return {
                "type": "catalog",
                "data": {
                    "title": catalog_name,
                },
                "catalog": sub_catalog
            }
        except Exception as e:
            self.sysLog.log(f"by NaturalProducts top get failed")

        # standards 顶级类型 跟 NaturalProducts 一样 SKIP

        # peptides 顶级类型：
        # 特点：第一个可以点进去。所以不直接获取下面的子链接
        try:
            main_soup = self.soup.find("div", id="main")
            item_soups = main_soup.find("div", class_="target_list")
            h3_soups = item_soups.find_all("h3")
            child_data = []
            for h3_soup in h3_soups:
                title = h3_soup.find("h3").get_text(strip=True)
                link = h3_soup.find("a").get("href")
                child_data.append({
                    "title": title,
                    "link": link,
                    "children": []
                })

            return {
                "type": "catalog",
                "data": {
                    "title": catalog_name,
                },
                "catalog": child_data
            }
        except Exception as e:
            self.sysLog.log(f"by NaturalProducts top get failed")

        # gmp 顶级 当前不做方案。 直接返回
        # 如果是：gmp-small-molecules.html  则认为是终极方案  附赠两个入口链接和目录。直接认定为终极页面。  但是pathways 的又和这个不一样。他的就是列表


    def std_data(self, data):
        """
        标准化输出
        输出结构：
        {
            catalog: {
                current_data: {
                    "title": ""
                },
                queue_data: [
                    {
                        "title": sub_title,
                        "link": sub_link,
                        "type": ""
                        "children": []
                    }
                ]
            },
            product: {
                "current_data": [
                ],
                "queue_data": [
                    start_id,
                    end_id
                ]

            }
        }


        数据说明：
        catalog: 当前分类信息


        catalog.current_data: 当前数据
        catalog.current_data.type 类型：包括 category | effect | group
        catalog.queue_data: 要爬取分类的页面数据

        product
        """
        if "catalog" not in data:
            data['catalog'] = {
                "current_data": [],
                "queue_data": []
            }
        if "product" not in data:
            data['product'] = {
                "current_data": [],
                "queue_data": []
            }

        if "current_data" not in data['catalog']:
            data['catalog']['current_data'] = []

        if "queue_data" not in data['catalog']:
            data['catalog']['queue_data'] = []


        if "current_data" not in data['product']:
            data['product']['current_data'] = []

        if "queue_data" not in data['product']:
            data['product']['queue_data'] = []

        if "error" not in data:
            data['error'] = ""

        return data









