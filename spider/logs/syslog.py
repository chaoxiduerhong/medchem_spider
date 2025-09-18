import datetime
from config import gpt_conf
from utils import log, get_setting, set_setting
import utils

class SysLog:
    def __init__(self, thread_lock=None, browser_port=None, mark=None):
        self.thread_lock = thread_lock
        self.browser_port = browser_port
        self.mark = mark

    def set_mark(self, mark):
        if mark:
            self.mark = mark

    # region Helper Functions
    def log(self, msg):
        if gpt_conf.is_save_log:
            log_save_path = f"{gpt_conf.log_file_path}/{self.browser_port}"
            log(f"[{self.browser_port}]{self.mark} [{utils.common.get_now_str(f='%H:%M:%S')}] - {msg}", level=2,
                sub_path=log_save_path)
        else:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("[%s] [%s]%s - %s" % (now, self.browser_port, self.mark, msg))

    def err_log(self, msg):
        if gpt_conf.is_save_log:
            log_save_path = f"{gpt_conf.log_file_path}/{self.browser_port}"
            log("[%s]%s - %s" % (self.browser_port, self.mark, msg), level=2,
                sub_path=log_save_path, is_print=False)
        else:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("[%s] [%s]%s - %s" % (now, self.browser_port, self.mark, msg))