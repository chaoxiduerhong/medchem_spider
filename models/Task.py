import utils.common
from .MongoBase import BaseModel
from utils import env
from config import gpt_conf
from pymongo import ReturnDocument

class TaskModel(BaseModel):
    """
    任务状态status：
    start： 待开始，提交询单过来后的状态
    running： 任务正在运行，可以设置为stop
    stop： 已经停止，认为停止，可以更改为start
    failure： 因程序异常，任务无法执行被跳过。这种状态说明有可能任务只执行了一半。当任务设置为start的时候，可以继续
    complete： 任务完成。无法该更状态
    当运行为stop，failure的时候，重新设置为start，该任务已经爬取的结果将被清空，然后重新爬取

    name 根据线程名称生成（非url生成）
    group_name 根据线程名称+组生成 相同的组运行的流程基本一致

    spider_url 待爬取的链接
    processing: 该页面完成在状态
    page_processing:
    product_processing

    c_name: 当前分类名称
    c_key: 分类唯一key（多个任务可能一个key）
    p_c_key: 上一级分类 的c_key
    """

    def __init__(self):
        super().__init__()
        # 要连接的数据库
        self.connection = "products"
        # 表名称，子类必须重写该表名称
        self.table_name = "med_tasks"
        self.primary_key = "bid"
        print("*** check current products tables :%s", self.table_name)

    def init_task(self, spider_url, task_name, group_name, c_key, c_name, uid):
        """
        检测任务是否存在，如果任务不存在，则根据 spider_url 创建第一条记录
        """
        exists = self.first(condition={
            "name": task_name
        })
        if not exists:
            self.add_one(data={
                "processing": "waiting",
                "catalog_processing": "waiting",
                "product_processing": "waiting",

                'type': "category",
                "group_name":group_name,
                "name": task_name,
                "title": task_name,
                "spider_url": spider_url,

                'uid': uid,

                'c_name': c_name,
                # 分类唯一key
                "c_key": c_key,
                # 上一级的 c_key
                "c_p_key": utils.common.md5("00000000000000-0000-0000"),
            })

    def getFirstData(self, task_name, test_cid):
        """
        获取第一个产品
        """
        result = None
        if test_cid:
            result = self.lock_find_one_and_update(
                {
                    "cid": test_cid
                },
                {
                    "$set": {
                        "processing": "running"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)

        if not result:
            result = self.lock_find_one_and_update(
                {
                    "processing": "waiting",
                    "name": task_name
                },
                {
                    "$set": {
                        "processing": "running"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)

        if not result:
            result = self.lock_find_one_and_update(
                {
                    "processing": {"$exists": False},
                    "name": task_name
                },
                {
                    "$set": {
                        "processing": "running"
                    }
                },
                sort=None,
                return_document=ReturnDocument.AFTER)

        # 如果没有数据了，将running的再次设置为waiting。避免遗漏数据
        if not result:
            self.update_many(condition={
                "processing": "running",
                "name": task_name
            }, data={'processing': "waiting"})

        # TODO 修复数据模式. 一般不开启除非存在了大量失败的
        if not result and gpt_conf.fetch_failed_fill:
            self.update_many(condition={
                "processing": "failed",
                "name": task_name
            }, data={'processing': "waiting"})

        return result

