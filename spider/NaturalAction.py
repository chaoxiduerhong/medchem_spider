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

class NaturalPageAction(pageAction):
    def __init__(self, thread_lock, mark, task_name, soup: BeautifulSoup, url):
        super(NaturalPageAction, self).__init__(thread_lock, mark, task_name, soup, url)

    def get_current_lv(self):
        """
        检测当前页面的类别
        """
        bread_soup = self.soup.find("div", id="bread")
        ol_lis = bread_soup.find_all("li")

        if len(ol_lis) == 2:
            return 1

        if len(ol_lis) == 3:
            return 2

        if len(ol_lis) == 4:
            return 3

        if len(ol_lis) == 5:
            return 4

        return None


    def parse_lv_1(self, catalog_name):
        # pathway 顶级 的写法
        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": self.parse_list__cls_hot_list()
            }
        })


    def parse_lv_2(self, catalog_name):
        """
        二级分类获取
        第二级已经开始有产品和分类了

        """
        queue_data = self.parse_target_list()
        current_product = self.parse_product_list__cls_sub_ctg_list_con()
        max_page = self.parse_ui_pager__product_page()
        product_queue_data = [2, max_page]

        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": queue_data
            },
            "product": {
                "current_data": current_product,
                "queue_data": product_queue_data
            },
        })

    def parse_lv_3(self, catalog_name):
        """
        三级分类获取
        部分有分类 部分没有分类
        有分类的：https://www.medchemexpress.com/dyereagents/chemical-stain-analysis.html
        """
        queue_data = self.parse_target_list()
        current_product = self.parse_product_list__cls_sub_ctg_list_con()
        max_page = self.parse_ui_pager__product_page()
        product_queue_data = [2, max_page]

        return self.std_data({
            "catalog": {
                "current_data": {
                    "title": catalog_name,
                },
                "queue_data": queue_data
            },
            "product": {
                "current_data": current_product,
                "queue_data": product_queue_data
            },
        })


    def parse_lv_4(self, catalog_name):
        """
        当前没发现该分类下有子分类的情况
        """
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
            },
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

        return None
