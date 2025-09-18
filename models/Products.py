from .MongoBase import BaseModel
import utils
from utils import env
from config import gpt_conf
from pymongo import ReturnDocument

class ProductsModel(BaseModel):
    """
    任务状态status：
    start： 待开始，提交询单过来后的状态
    running： 任务正在运行，可以设置为stop
    stop： 已经停止，认为停止，可以更改为start
    failure： 因程序异常，任务无法执行被跳过。这种状态说明有可能任务只执行了一半。当任务设置为start的时候，可以继续
    complete： 任务完成。无法该更状态
    当运行为stop，failure的时候，重新设置为start，该任务已经爬取的结果将被清空，然后重新爬取
    """

    def __init__(self):
        super().__init__()
        # 要连接的数据库
        self.connection = "products"

        # 表名称，子类必须重写该表名称
        self.table_name = "med_product"
        self.primary_key = "bid"
        print("*** check current product_result tables :%s", self.table_name)

    def set_table_name(self, table_name):
        """
        重设置表名称
        用于一次提问完所有提纲
        """
        self.table_name = table_name

    def getFirstProduct(self):
        """
        获取第一个产品
        """
        result = self.get(
            start=0,
            length=1,
            order_by={"bid": 1}
        )
        return None if not result else result[0]


    def getFirstProductByAsync(self, bid=None):
        """
        异步出队列
        "processing": "answer_success",
        创建时间必须大于半个小时。不能取创建半个小时以内的数据
        """

        current_ts = utils.common.get_second_utime() - 1800
        current_time_str = utils.common.formatTime(current_ts)
        result = None
        if bid:
            result = self.lock_find_one_and_update(
                {
                    "bid": bid
                },
                {
                    "$set": {
                        "processing": "answer_waiting"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)

        # print("------product1----")
        if not result:
            result = self.lock_find_one_and_update(
                {
                        "processing": "ask_success",
                        "created_at": {"$lte": current_time_str},
                },
                {
                    "$set": {
                        "processing": "answer_waiting"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)
        # print("------product2----")
        if not result:
            result = self.lock_find_one_and_update(
                {
                    "processing": {"$exists": False},
                    "account": {"$exists": True},
                    "created_at": {"$lte": current_time_str},
                },
                {
                    "$set": {
                        "processing": "answer_waiting"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)
        return result

    def getFirstProductByFetchLink(self, link_version, bid=None, end_time=None,start_time=None, ext_condition=None):
        """
        异步出队列
        "link_processing": 不存在，waiting， running，success
        当不存在或者waiting的时候，获取它
        获取到后将值修改为 running

        1. link_processing 这个字段不存在的
        2. 这个字段为 waiting
        """

        result = None
        if not ext_condition:
            ext_condition = {}

        # 存在测试id
        if bid:
            # 当存在bid的时候，直接获取该值
            if isinstance(bid, list):
                condition = {self.primary_key: {"$in": bid}}
            else:
                condition = {self.primary_key: {"$eq": bid}}
            return self.first(
                condition=condition
            )

        if not result:
            condition1 = {'time': {"$lt": end_time,"$gte": start_time}, 'link_processing': "waiting"}
            condition = {**condition1, **ext_condition}
            print(condition)
            result = self.first(
                condition=condition
            )

        if not result:
            # TODO end_time 重新定义。获取当前时间
            condition1 = {'time': {"$lt": end_time,"$gte": start_time}, 'link_version': {"$lt": link_version}}
            condition = {**condition1, **ext_condition}
            print(condition)
            result = self.first(
                condition=condition
            )

        if not result:
            condition1 = {'time': {"$lt": end_time, "$gte": start_time}, 'link_version': {"$ne": link_version}}
            condition = {**condition1, **ext_condition}
            print(condition)
            result = self.first(
                condition=condition
            )

        # 如果没有数据了，将running的再次设置为waiting。避免遗漏数据
        if not result:
            self.update_many(condition={
                "link_processing": "running"
            }, data={'link_processing': "waiting"})

        # 将获取到的数据状态更新
        if result:
            self.update_one(condition={
                "bid": result["bid"],
            }, data={
                'link_processing': "running",
                "link_version": link_version
            })
        return result

    def getLastProduct(self):
        """
        获取最后一个产品
        """
        result = self.get(
            start=0,
            length=1,
            order_by={"bid": -1}
        )
        return None if not result else result[0]

    def day_total(self):
        # 根据日期统计数据
        week_ts = utils.common.get_second_utime() - 86400 * 7
        week_day = utils.common.formatTime(week_ts)
        query = [
            {
                "$match": {
                    "created_at": {
                        "$gt": week_day,
                        "$lte": utils.get_now_str(),
                    }
                }
            },
            {
                "$addFields": {
                    "date": {
                        "$dateFromString": {
                            "dateString": "$created_at",
                            # "format": "%Y-%m-%d",
                            "format": "%Y-%m-%d %H:%M:%S"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                        "day": {"$dayOfMonth": "$date"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }

        ]
        data = self.query(query)
        result = {}
        for item in data:
            ts = "%s-%s-%s" % (item["_id"]['year'], item["_id"]['month'], item["_id"]['day'])
            result[ts] = item["count"]
        return result


    def update_start_std(self, result, std_version):
        if result:
            for item in result:
                self.update_std_status(
                    bid=item['bid'],
                    std_version=std_version,
                    std_status="processing",
                    tags=[]
                )

    def update_std_status(self, bid, std_version, std_status, tags):
        self.update_many(data={
            "std_version": std_version,
            "std_status": std_status,
            "std_tags": tags
        }, condition={
            "bid": bid
        })

    def byBidGetFirstProductForTrans(self, bid, client_max_bid):
        """
        获取第一个产品
        """
        result = self.get(
            start=0,
            length=1,
            order_by={"bid": 1},
            condition={
                "bid": {"$gt": bid, "$lte": client_max_bid},
                "std_status": {"$eq": "success"}
            }
        )
        return None if not result else result[0]

    def byHostnameAndBrowserPortGet(self, browser_port):
        """
        获取该浏览器在30分钟前产出的数据
        """
        current_ts = utils.common.get_second_utime() - 1800
        current_time_str = utils.common.formatTime(current_ts)
        ret = self.get(condition={
            "created_at": {"$lte": current_time_str},
            "processing": "ask_success",
            "browser_port": browser_port,
            "hostname": utils.common.get_sys_uname()
        })
        return ret
