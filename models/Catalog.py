from .MongoBase import BaseModel
import utils
from utils import env
from config import gpt_conf
from pymongo import ReturnDocument

class CatalogModel(BaseModel):
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
        self.table_name = "med_catalog"
        print("*** check current product_result tables :%s", self.table_name)

    def set_table_name(self, table_name):
        """
        重设置表名称
        用于一次提问完所有提纲
        """
        self.table_name = table_name


