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
from argparse import Action
import inspect

from bs4 import BeautifulSoup

from spider.Action import pageAction

class PathwayPageAction(pageAction):
    def __init__(self, thread_lock, mark, task_name, soup: BeautifulSoup, url):
        super(PathwayPageAction, self).__init__(thread_lock, mark, task_name, soup, url)

    def get_current_lv(self):
        """
        检测当前页面的类别
        """
        path = self.get_url_path()
        path_obj = path.split("/")

        if "pathway" == path.lower():
            return 1

        if len(path_obj) == 2 and path_obj[0].lower() == "pathways":
            return 2

        if len(path_obj) == 3 and path_obj[0].lower() == "pathways":
            return 3

        if path_obj[0].lower() == "targets" and len(path_obj) == 2:
            return 4

        if path_obj[0].lower() == "targets" and (len(path_obj) == 3 or len(path_obj) == 4):
            return 5

        return None


    def parse_lv_1(self, catalog_name):
        # pathway 顶级 的写法
        div_soup = self.soup.find("div", class_="pathway_list")
        ul = div_soup.ul
        sub_catalog = []
        error = ""
        if ul:
            for a in ul.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)  # 去除空格和换行
                sub_catalog.append({
                    "title": text,
                    "link": href,
                    "type": "category",
                    "children": []
                })
        if not sub_catalog:
            error = "not_find_catalog"
        return self.std_data({
            "catalog":{
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": sub_catalog
            },
            "error": error,
        })


    def parse_lv_2(self, catalog_name):
        """
        二级分类获取
        target_list
        """
        queue_data = self.parse_target_list()
        if not queue_data:
            queue_data = self.parse_cls_target_h3_href_list()

        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": queue_data
            }
        })

    def parse_lv_3(self, catalog_name):
        """
        三级分类获取
        label-list
        https://www.medchemexpress.com/Targets/dengue-virus.html
        """
        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": self.parse_label_list()
            }
        })


    def parse_lv_4(self, catalog_name):
        """
        该层包含了：
        label div class = list-effect-main
        product
        """
        # 获取当前页分类
        catalog_category = self.parse_category__cls_isoform_list()

        print(catalog_category, "=================catalog_category=================")

        # 获取当前页labels
        catalog_label = self.parse_effect_list_cls_effect_main()

        # 分类聚合
        catalog_data = catalog_category + catalog_label

        # 获取当前页产品信息
        current_product = self.parse_product_list__cls_sub_ctg_list_con()

        # 这里要获取分页的复杂操作，最终由得生成lst 最大可能会上千。 如果检测到产品了，则其他页面起始页为2
        max_page = self.parse_ui_pager__product_page()
        product_queue_data = [2, max_page]

        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": catalog_data
            },
            "product": {
                "current_data": current_product,
                "queue_data": product_queue_data
            },
        })

    def parse_lv_5(self, catalog_name):
        current_product = self.parse_product_list__cls_sub_ctg_list_con()
        max_page = self.parse_ui_pager__product_page()
        product_queue_data = [2, max_page]
        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": []
            },
            "product": {
                "current_data": current_product,
                "queue_data": product_queue_data
            }
        })

    def parse(self):
        """
        pathway.html
        一级：只抓取一级分类。
        该页面虽然有二级分类，但是不可用。实际上这些二级页面是还有一层分类的。只能到第二级页面才能发现
        无产品

        二级页面：
        只有分类无产品

        三级级页面开始有标签 effect。
        三级页面
        关联的产品

        注意分类有三种：
        1. 有链接的分类。属于实体分类
        2. 无链接的分类 属于虚拟了一层归类。比如将多个分类归类的某个分类下
        3. effect 类分类。实际上不是分类，更像是标签类的（可以做数据帅选）

        产品爬取;
        xxx Related Products (26) 这个tab下 并且存在分页。需要获取分页的数，用于构建链接。

        关联属性：直接存储html。不解析
        关联抗体：
        Antibodies
        这个不能存储到产品中。关联抗体单独一张表

        除了关联抗体还有其他的 异构体比较啥的


        页面等级
        pathway.html 一级
        """
        # 根据url + 内容来检测当前页面等级
        current_lv = self.get_current_lv()
        catalog_name = self.get_current_catalog_name()
        self.sysLog.log(f"current LV {current_lv}")
        if not catalog_name:
            return self.std_data({
                "error": f"{inspect.currentframe().f_code.co_name}_{current_lv}__failed__not__find__catalog_name"
            })

        if current_lv == 1:
            return self.parse_lv_1(catalog_name)
        if current_lv == 2:
            return self.parse_lv_2(catalog_name)
        if current_lv == 3:
            return self.parse_lv_3(catalog_name)
        if current_lv == 4:
            return self.parse_lv_4(catalog_name)
        if current_lv == 5:
            return self.parse_lv_5(catalog_name)

        return None
