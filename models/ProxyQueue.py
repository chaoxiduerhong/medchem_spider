from .MongoBase import BaseModel
from utils import env
from config import gpt_conf


class ProxyQueueModel(BaseModel):

    def __init__(self):
        super().__init__()
        # 要连接的数据库
        self.connection = "default"
        # 表名称
        self.table_name = "med_proxy_queue"

        print("*** Synonyms tables :%s", self.table_name)

    def set_proxy_login_success_num(self, indexId):
        data = self.first(condition={"indexId": indexId})
        if data:
            self.update_one(condition={"indexId": indexId}, data={
                "login_success_num": data["login_success_num"] + 1 if "login_success_num" in data else 1,
            })

    def set_proxy_login_failed_num(self, indexId):
        data = self.first(condition={"indexId": indexId})
        if data:
            self.update_one(condition={"indexId": indexId}, data={
                "login_failed_num": data["login_failed_num"] + 1 if "login_failed_num" in data else 1,
            })