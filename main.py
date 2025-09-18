"""
命令格式：
python3 main.py [命令标记/类型] [其他参数...]
整个脚本采用单入口的方式管理。如果
"""
import sys
import os
import traceback

from proxy_check import start as check_start
from spider import query_start, server

mark = sys.argv[1]
if len(sys.argv) > 2:
    mode = sys.argv[2]
else:
    mode = None

def confirm_exec():
    RED_BOLD = '\033[1;31m'  # 红色加粗
    RESET = '\033[0m'  # 重置
    answer = input(f"您当前要操作的是：{RED_BOLD}{mark}{RESET}, \n你是否已经做好了相关配置文件（输入{mark}表示已经配置好，确认执行）：")
    if answer.lower() == mark:
        print("已确认，继续执行。")
        return True
    else:
        print("操作已取消。")
        exit(0)

if __name__ == "__main__":
    try:
        # 这里设置命令的标题
        current_cmd = f"{os.path.abspath(sys.argv[0])} {mark}"
        os.system(f"title {current_cmd}")
        if mark == "query":
            query_start(mode)

        if mark == "server":
            server()

        if mark == "check":
            check_start()

    except KeyboardInterrupt:
        print("捕获到 Ctrl+C，准备退出...")
    except:
        print(traceback.format_exc())
    finally:
        print("主线程退出")

