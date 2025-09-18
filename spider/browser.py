"""
浏览器管理

启动浏览器
关闭浏览器
关闭单个浏览器
页面浏览器管理

批量启动
批量关闭

提供server相关功能

初始化目录如果不存在，则创建


"""

import traceback
import socket
import psutil

import re
import json
import time
import os, inspect
import math

import requests

import utils
import copy
from threading import Thread
from config import gpt_conf
from config import browser_conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import subprocess


def async_call(fn):
    """
    异步调用
    """

    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class BrowserManager:
    def __init__(self):
        self.browser_config_path = gpt_conf.browser_config_path
        self.proxy_config_path = gpt_conf.proxy_config_path
        self.bit_url = "http://127.0.0.1:54345"
        self.headers = {'Content-Type': 'application/json'}
        self.chrome_executable = gpt_conf.chrome_executable_path
        self.browser_data_path = gpt_conf.browser_data_path
        # gs 走的是 vmess ,v2ray 是 shadowsocks 协议
        self.proxy_mode = "vmess"
        # v2ray base_template.json
        self.proxy_template = "base_template_vmess.json"
        self.mode = "local"

    def get_proxy_list(self):
        """
        获取线上运行的最新队列
        """
        result = []
        url = f"http://{gpt_conf.proxy_host}:8045/running_proxy"
        resp = requests.get(url)
        data = resp.content.decode("utf-8")
        proxy_dicts = json.loads(data)
        proxy_dicts = proxy_dicts['data']
        return proxy_dicts

    def runcmd(self, port=None, data_dir="", proxy_name=None):
        """
        执行系统命令，并且获取其pid
        浏览器启动，需要加上代理服务器地址
        """
        try:
            cmd = [
                self.chrome_executable,
                '--remote-debugging-port=' + str(port),
                '--user-data-dir=' + data_dir,
                '--hide-crash-restore-bubble',
                '--disable-default-browser-check',
                '--disable-popup-blocking',
                '--no-default-browser-check',
                '--no-first-run',
                '--disable-features=PrivacySandboxSettings3',
                "--disable-features=TranslateUI", # 屏蔽 翻译
                '--force-device-scale-factor=%s' % gpt_conf.window_rate
            ]
            if proxy_name:
                proxy_list = self.get_proxy_list()
                if proxy_name in proxy_list and "proxy_http_port" in proxy_list[proxy_name]:
                    proxy_port = proxy_list[proxy_name]['proxy_http_port']
                    proxy_type = proxy_list[proxy_name]['source_type']
                    protocol = "http"
                    cmd.append('--proxy-server=%s://%s:%s' % (protocol, gpt_conf.proxy_host, int(proxy_port)))
            cmd.append("about:blank")
            utils.log("RUNCMD start browser： proxy_name:%s, cmd:%s, " % (proxy_name, cmd))
            process = subprocess.Popen(cmd)
            return process.pid
        except Exception as e:
            utils.log("runcmd start browser err: %s" % e)
            return None


    def save_bat(self, port, cmd, user_path):
        with open("%s/%s.bat" % (user_path, port), "w") as f:
            f.write(cmd)

    @staticmethod
    def check_port_used(port):
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False

    def fill_conf_data(self, uid, config):
        """
        补充config信息
        格式：key:value
        """
        caller_name = inspect.currentframe().f_back.f_code.co_name

        # utils.log(f"[tricky] {caller_name} -> browser.py.fill_conf_data() - gonna get_setting() - uid(type)={uid}({type(uid)})") # for debug
        data = utils.get_setting(self.browser_config_path, uid)

        if not data:
            data = {}
            # utils.log(f"[tricky] {caller_name} -> browser.py.fill_conf_data() - getting NO DATA. uid(type)={uid}({type(uid)})")
        if config:
            for conf in config:
                data[conf] = config[conf]
        
        # Jun 19 尝试捕捉 proxy_name 被置空的场景. 是 start_all_browser 时, 获取到的 proxy_name 为空。
        if "proxy_name" not in data or not data["proxy_name"]:
            pass
            # utils.log(f"[tricky]in_fill_conf_data - Invoked by {caller_name} - uid(type)={uid}({type(uid)}), data lenth {len(data)}. ")

        return utils.set_setting(self.browser_config_path, uid, data)

    def start_browser(self, browser, proxy_name=None):
        """
        检测浏览器端口是否启动。如果未启动则启动，并且更新pid。
        如果已经去启动，则跳过。
        """

        port = browser['port']

        if not os.path.exists(self.browser_data_path):
            os.makedirs(self.browser_data_path)
        user_path = "%s/data_%s" % (self.browser_data_path, port)

        pid = self.runcmd(port, user_path, proxy_name)
        return pid

    def open_browser(self, uid, proxy_name=None):
        """
        检测浏览器端口是否启动。如果未启动则启动，并且更新pid。
        如果已经去启动，则跳过。
        """
        browser_data = browser_conf.browser_user
        browser = browser_data[uid]
        if proxy_name:
            browser['proxy_name'] = proxy_name
        else:
            browser_data = utils.get_setting(self.browser_config_path, uid)
            if browser_data and "proxy_name" in browser_data and browser_data['proxy_name']:
                proxy_name = browser_data['proxy_name']
                browser['proxy_name'] = proxy_name
        ret = self.start_browser(browser, proxy_name)
        browser['pid'] = ret
        self.fill_conf_data(browser['name'], browser) # Jun 13 fix: 已经存在于browser.json文件里的，用 'name' 才能取到，用 'port' 取不到．

    @staticmethod
    def std_browser_user(item, data):
        if "port" not in data:
            return None
        if not data['status']:
            return None
        if data['status'] != "actived":
            return None
        if "host" not in data or not data['host']:
            data['host'] = "127.0.0.1"
        if "proxy" not in data or not data['proxy']:
            data['proxy'] = None
        if "proxy_name" not in data or not data['proxy_name']:
            data['proxy_name'] = None
        if "name" not in data or not data['name']:
            data['name'] = item
        return data

    @staticmethod
    def force_close(parent_pid):
        """
        强制杀死某个进程以及其子进程
        """
        import os, signal, psutil
        if not parent_pid:
            return
        parent_pid = int(parent_pid)

        try:
            # 获取父进程
            parent = psutil.Process(parent_pid)
            # 获取父进程的所有子进程（包括孙子进程等）
            children = parent.children(recursive=True)
            # 创建一个包含父进程PID的列表
            pids_to_kill = [parent_pid]
            # 将所有子进程的PID添加到列表中
            pids_to_kill.extend(child.pid for child in children)
            # 遍历列表，对每个PID发送SIGKILL信号
            for pid in pids_to_kill:
                try:
                    os.kill(pid, signal.SIGILL)
                except PermissionError:
                    # 忽略权限错误，可能我们没有权限杀死某个进程
                    print("close browser PermissionError")
                    pass
                except ProcessLookupError:
                    # 忽略进程查找错误，进程可能已经自然死亡
                    print("close browser ProcessLookupError")
                    pass
        except (psutil.NoSuchProcess, PermissionError):
            # 忽略错误，如果进程不存在或者没有权限
            print("close browser PermissionError1")
            pass
        return True

    def init_browser(self):
        """
        初始化：启动所有浏览器-》关闭所有浏览器-》修改配置文件
        """

    def load_conf(self):
        """
        读取配置文件内容 storage/data/browser.json 
        """
        return utils.get_setting(self.browser_config_path)

    def get_list(self, all_browser_on_host=False):
        """
        启动浏览器：获取启动的pid，更新配置文件
        """
        # 配置文件中的
        browser_data = browser_conf.browser_user

        # browser.json 中的
        local_list = self.load_conf()
        number_of_local_conf = len(local_list)
        caller_name = inspect.currentframe().f_back.f_code.co_name
        # utils.log(f"[tricky] caller[{caller_name}] -> current[browser.py.get_list().load_conf()] - number_of_local_conf {number_of_local_conf}")

        browser_list = browser_data.copy()

        # 补充pid
        for key_in_browser_json in local_list:
            # if bitem in browser_list and "pid" in local_list[bitem]:
            #     browser_data[bitem]['pid'] = local_list[bitem]['pid']
            # elif bitem in browser_list:
            #     browser_data[bitem]['pid'] = ""
            # 过滤掉config配置文件中 disabled的数据
            
            # Jun 22 try 雪藏这个逻辑，不再做判断
            if key_in_browser_json in browser_data and browser_data[key_in_browser_json]['status'] == "actived" and key_in_browser_json in browser_list:
                browser_data[key_in_browser_json] = local_list[key_in_browser_json]

            # Jun 22 加log. 并且 无脑将 browser.json 中的数据，全部更新到 browser_data 中. 防止浏览器换班的时候丢失 proxy name
            # browser_data[bitem] = local_list[bitem] # 无脑将 browser.json 中的数据，全部更新到 browser_data 中.
            # utils.log(f"[tricky]{caller_name} -> browser.get_list() - processing browser.json.port {browser_data[bitem]['port']}, new proxy_name {browser_data[bitem]['proxy_name']}")
            
        result = []
        for item in browser_data:
            browser = self.std_browser_user(item, browser_data[item])
            if browser:
                browser['running_status'] = "未知"
                browser['running_time'] = "未知"
                browser_status = utils.get_setting(gpt_conf.browser_status_file_path, item)
                if browser_status:
                    if "running_status" in browser_status:
                        browser['running_status'] = browser_status['running_status']
                    if "running_time" in browser_status:
                        browser['running_time'] = browser_status['running_time']
                if "pid" in browser and browser['pid'] and psutil.pid_exists(int(browser['pid'])):
                    browser['process_status'] = "已打开"
                else:
                    browser['process_status'] = "已关闭"
                result.append(browser)
        return result

    def get_faulty_list(self):
        """
        获取代理异常的窗口 + 代理
        """
        lists = self.get_list()
        result = []
        for item in lists:
            if "running_status" not in item or item['running_status'] != "actived":
                result.append(item)
        return result

    def get_browser(self, port):
        """
        根据端口获取浏览器
        """
        all_data = self.get_list()
        for item in all_data:
            if item['port'] == int(port):
                return item
        return {}

    @staticmethod
    def get_local_ip():
        try:
            # 获取主机名
            hostname = socket.gethostname()
            # 获取 IP 地址
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception as e:
            print("Error:", e)

    def get_other_host_running(self):
        """
        pass
        """
        return utils.get_setting("all_running_proxy", "*")

    def set_all_proxy_status_waiting(self):
        """
        将所有代理状态设置为异常，用于重新匹配所有
        """
        all_browser = self.get_list()
        result = {}
        for browser in all_browser:
            result[browser['name']] = {
                "running_status": "waiting",
                "running_time": utils.get_now_str(),
                "running_proxy": browser['proxy_name'] if "proxy_name" in browser else ""
            }
        utils.save_setting(gpt_conf.browser_status_file_path, result)

    def get_ssr_item(self, id):
        proxy_json_path_for_ssr = "./storage/proxy/ssr"
        proxy_root_path_for_ssr = "%s/gui-config.json" % proxy_json_path_for_ssr
        with open(proxy_root_path_for_ssr, 'r', encoding="utf-8") as ssrfile:
            ssr_proxy_content = ssrfile.read()
            ssr_proxy_data = json.loads(ssr_proxy_content)
            ssr_proxy_data = ssr_proxy_data["configs"]
            for item in ssr_proxy_data:
                if item['id'] == id:
                    return item
        return None

    def ssr_to_v2ray(self, data):
        """
        将ssr数据转化为v2ray支持格式
        """
        return {
            "indexId": data['index_id'],
            "configType": 3,
            "configVersion": 2,
            "sort": 10,
            # ssr无需设置这个地址
            "address": None,
            "port": int(data['server_port']),
            "id": None,
            "alterId": 0,
            "security": None,
            "network": None,
            "remarks": data['remarks'],
            "headerType": "http",
            "requestHost": None,
            "path": "",
            "streamSecurity": "",
            "allowInsecure": "False",
            "testResult": "",
            # 5039806936299000000 ID 为自定义id
            "subid": "5039806936299000000",
            "flow": "",
            "sni": None,
            "alpn": None,
            "groupId": "",
            "coreType": None,
            "preSocksPort": 0,
            "process_status": False,
            "process_info": "stop",
            "pid": "",
            "proxy_http_port": int(data['local_port']),
            "proxy_socket_port": None
        }

    def get_running_proxy_list(self):
        proxy_list = self.get_proxy_list()
        proxy_list2 = copy.deepcopy(proxy_list)
        for item in proxy_list2:
            if proxy_list[item]['process_info'] != "running":
                del proxy_list[item]
        return proxy_list

    def get_stop_proxy_list(self):
        """
        TODO 理论上应该排除所有异常的节点。包括：需要登录的 + 无chat的
        """
        proxy_list = self.get_proxy_list()
        proxy_list2 = copy.deepcopy(proxy_list)
        for item in proxy_list2:
            if proxy_list[item]['process_info'] == "running":
                del proxy_list[item]
        return proxy_list

    def get_proxy_for_http_port(self):
        start_port = 11000
        while True:
            if start_port >= 12000:
                return None
            start_port = start_port + 1
            is_port_used = self.check_port_used(start_port)
            is_exist_proxy_port = self.check_exist_proxy_port(start_port)
            # if is_port_used:
            #     print(f"http port {start_port} is in used")
            # else:
            #     print(f"http port {start_port} is AVAILABLE!")
            if not is_port_used and not is_exist_proxy_port:
                return start_port

    def get_proxy_for_socket_port(self):
        start_port = 12000
        while True:
            if start_port >= 13000:
                return None
            start_port = start_port + 1
            if not self.check_port_used(start_port) and not self.check_exist_proxy_port(start_port):
                return start_port

    def check_exist_proxy_port(self, port):
        local_proxy_port = utils.get_setting("proxy_port")
        find_times = 0
        for item in local_proxy_port:
            if port == local_proxy_port[item]['http'] or port == local_proxy_port[item]['socket']:
                # 出现次数大于1，是因为排除当前已经有的
                find_times = find_times + 1
                if find_times > 1:
                    return True
        return False

    def kill_process_by_port(self, port):
        # 获取所有进程列表
        for proc in psutil.process_iter():
            try:
                # 获取进程绑定的所有端口
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == port:
                        # 杀死进程
                        print(f"Killing process {proc.pid} on port {port}")
                        os.kill(proc.pid, 9)
                        return
            except psutil.AccessDenied:
                # 忽略没有权限的进程
                pass

    def close_proxy(self, name):
        """
        关闭代理
        关闭代理后，将原来代理pid置空
        """
        local_proxy_port = utils.get_setting("proxy_port")
        proxy_list = self.get_proxy_list()
        if name in proxy_list and proxy_list[name]:
            current_proxy = proxy_list[name]
            if "pid" in current_proxy and current_proxy['pid'] and psutil.pid_exists(int(current_proxy['pid'])):
                self.force_close(current_proxy['pid'])
                # 将代理pid设置为空，避免后续和其他程序进程id混淆
                current_proxy['pid'] = ""
                current_proxy['proxy_http_port'] = ""
                current_proxy['proxy_socket_port'] = ""
                utils.set_setting(self.proxy_config_path, name, current_proxy)

    def start_all_browser(self, specify_port=None, proxy_name=None):
        """
        启动浏览器：获取启动的pid，更新配置文件
        """
        browser_data = self.get_list()
        for item in browser_data:
            browser = self.std_browser_user(item['name'], item)

            # 指定打开某个 port 
            if specify_port:
                if int(specify_port) != browser['port']:
                    continue
            else:
                pass

            if browser and browser['status'] == "actived":
                if "pid" in browser and browser['pid'] and psutil.pid_exists(int(browser['pid'])):
                    print("进程存在", browser['pid'])
                    continue
                elif "pid" in browser:
                    print("进程不存在, 但是还是会强制尝试关闭相关线程")
                    self.force_close(browser['pid'])

                proxy_name = None
                if "proxy_name" in browser and browser['proxy_name']:
                    proxy_name = browser['proxy_name']
                else: # Jun 25 2024 - 临时特殊处理: 当浏览器换批次会丢失路线, 这里曲线救国 临时填充个路线
                    latest_browser_conf = self.pick_random_route_for_browser(browser['port'])
                    if latest_browser_conf and 'proxy_name' in latest_browser_conf:
                        proxy_name = latest_browser_conf['proxy_name']

                ret = self.start_browser(browser, proxy_name)
                if not ret:
                    # 如果浏览器已经启动，则跳过
                    continue
                browser['pid'] = ret
                
                self.fill_conf_data(item['name'], browser)
                # utils.log(f"[tricky]START_ALL_BROWSER.fill_conf_data - port {browser['name']}, proxy {browser['proxy_name']}")
                time.sleep(0.33)

    def stop_browser(self, uid):
        local_list = self.load_conf()
        for item in local_list:
            browser = local_list[item]
            if uid == str(browser['port']):
                if "pid" in browser and browser['pid']:
                    self.force_close(browser['pid'])
                    browser['pid'] = ""
                    self.fill_conf_data(item, browser)
                    # utils.log(f"[tricky]STOP_Browser.fill_conf_data - port {browser['name']}, proxy {browser['proxy_name']}")


    def stop_all_browser(self):
        local_list = self.load_conf()
        for item in local_list:
            if "pid" in local_list[item]:
                browser_info = local_list[item]
                self.force_close(browser_info['pid'])
                # pid 为空代表关闭状态
                browser_info['pid'] = ""
                self.fill_conf_data(item, browser_info)

    @async_call
    def browser_resize(self, port, xid=0, yid=1):
        # 初始化页面
        window_width = gpt_conf.window_width
        window_height = gpt_conf.window_height
        chrome_options = Options()
        chrome_options.ignore_local_proxy_environment_variables()
        chrome_options.add_experimental_option("debuggerAddress", "%s:%s" % ("127.0.0.1", port))
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-default-browser-check")  # 禁止 检查默认浏览器
        chrome_options.add_argument("--no-default-browser-check")  # 禁止 检查默认浏览器
        chrome_options.add_argument("--no-first-run") # 不展示 首次运行告知
        chrome_options.add_argument("--disable-features=PrivacySandboxSettings3") # 屏蔽 隐私权功能
        
        
        driver = webdriver.Chrome(options=chrome_options)

        driver.set_window_size(window_width, window_height)
        offset_x = (xid - 1) * window_width
        offset_y = (yid - 1) * window_height
        driver.set_window_position(offset_x, offset_y)

    def restart_browser(self, port, proxy_name=None):
        """
        重启单个浏览器窗口
        """
        print("1启动浏览器参数：port:%s, proxy_name:%s" % (port, proxy_name))
        self.stop_browser(port)
        time.sleep(3)
        # 查询是否有代理
        self.open_browser(port, proxy_name)

    def set_proxy(self, port, proxy_name):
        """
        设置代理信息
        关闭浏览器，不用关闭代理服务
        打开浏览器的时候，如果未配置，则强制关闭代理
        """
        browser = self.get_browser(port)
        if proxy_name:
            browser['proxy_name'] = proxy_name
            self.fill_conf_data(port, browser)

    def browser_port_update(self):
        """
        更新浏览器端口
        更新浏览器端口，需要关闭当前浏览器。更新完毕后再次启动浏览器
        """
        self.stop_all_browser()
        browser_data_path = self.browser_data_path
        if os.path.exists(browser_data_path):
            for item in os.listdir(browser_data_path):
                # 检查是否是文件夹
                if os.path.isdir(os.path.join(browser_data_path, item)):
                    port = item[5:]
                    # 更改文件1
                    file_path = "%s/%s/Default/Preferences" % (browser_data_path, item)
                    browser_config = None
                    with open(file_path, 'r', encoding="utf-8") as file:
                        browser_config_content = file.read()
                        browser_config = json.loads(browser_config_content)

                    if browser_config and "profile" in browser_config and "name" in browser_config['profile']:
                        browser_config['profile']['name'] = port

                        browser_config_json = json.dumps(browser_config, ensure_ascii=False)
                        if os.path.exists(file_path):
                            with open(file_path, 'w', encoding="utf-8") as file:
                                file.write(browser_config_json)

                    # 更改文件2
                    file_path = "%s/%s/Local State" % (browser_data_path, item)
                    browser_config = None
                    with open(file_path, 'r', encoding="utf-8") as file:
                        browser_config_content = file.read()
                        browser_config = json.loads(browser_config_content)

                    if browser_config and "profile" in browser_config \
                            and "info_cache" in browser_config['profile'] \
                            and "Default" in browser_config['profile']['info_cache'] \
                            and "name" in browser_config['profile']['info_cache']['Default']:
                        browser_config['profile']['info_cache']['Default']['name'] = port
                        browser_config_json = json.dumps(browser_config, ensure_ascii=False)
                        if os.path.exists(file_path):
                            with open(file_path, 'w', encoding="utf-8") as file:
                                file.write(browser_config_json)
        self.start_all_browser()

    @staticmethod
    def get_shadowsocksr_status():
        '''
        检查是否有与正则表达式模式匹配的进程正在运行
        '''
        process_name_pattern = re.escape("ShadowsocksR")  # 转义正则表达式中的特殊字符
        process_name_regex = re.compile(process_name_pattern, re.IGNORECASE)  # 编译正则表达式，忽略大小写

        for proc in psutil.process_iter(['name']):
            try:
                if process_name_regex.match(proc.info['name']):
                    return "running"
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return "stop"

    def reorder(self):
        """
        排序方案：
        异步进行排序
        """
        # 默认从0开始。因为左上角为0的坐标
        idx = gpt_conf.position_start_id
        # 默认从1开始
        yid = gpt_conf.position_y
        xid = gpt_conf.position_x
        max_x_id = gpt_conf.max_x_id

        local_list = self.get_list()
        for item in local_list:
            xid = xid + 1
            idx = idx + 1
            self.browser_resize(item['port'], xid, yid)
            if idx == max_x_id:
                yid = yid + 1
                idx = 0
                xid = 0

    def proxy_to_browser(self, mode="1v1"):
        """
        一键自动化将代理部署到浏览器窗口
        mode: 1v1 一个代理对应一个窗口
        mode: 1v3 将一个代理设置到 三批窗口

        注意：自动化重置会将原来的也重置掉
        """
        
        # 获取所有代理：running状态
        proxy_running_list = self.get_running_proxy_list()

        if mode == "1v1":
            browser_list = self.get_list() # 获取 当前批次 浏览器 
            # 匹配
            idx = -1
            for browser in browser_list:
                idx = idx + 1
                if proxy_running_list:
                    for proxy_key in proxy_running_list:
                        browser['proxy_name'] = proxy_key

                        # utils.log(f"PROXY_TO_BROWSER - pick proxy_key={proxy_key}. fill_conf_data.uid={browser['port']}")
                        self.fill_conf_data(browser['port'], browser)
                        # print(f"proxy-to-browser, current port is {browser['port']}")

                        del proxy_running_list[proxy_key]
                        break
                else:
                    browser['proxy_name'] = ""
                    self.fill_conf_data(browser['port'], browser)
        elif mode == "1v3":
            browser_list_all_batches = self.get_list(all_browser_on_host=True) # 获取所有三批浏览器 

            count_browser = len(browser_list_all_batches)
            count_running_proxy = len(proxy_running_list)
            each_proxy_vs_how_many_browser = math.ceil(count_browser / count_running_proxy)

            print(f"Count browser list {count_browser}, Count running proxy {count_running_proxy} ")
            print(f"each proxy vs {each_proxy_vs_how_many_browser} ports")

            dispatch_proxy_pool = copy.deepcopy(proxy_running_list) # 用 proxy pool 进行派发，pool 空了就用 deepcopy 填满

            printed_info = []
            for browser in browser_list_all_batches:
                if dispatch_proxy_pool:
                    for proxy_key in dispatch_proxy_pool:
                        if browser['proxy_name']:
                            line = f"PROXY_TO_BROWSER - port {browser['port']} has proxy {browser['proxy_name']}"
                            if line not in printed_info:
                                print(line)
                                printed_info.append(line)
                            continue
                            
                        browser['proxy_name'] = proxy_key

                        print(f"PROXY_TO_BROWSER - pick proxy_key={proxy_key}. fill_conf_data.uid={browser['port']}")
                        self.fill_conf_data(browser['port'], browser)
                        # print(f"proxy-to-browser, current port is {browser['port']}")

                        del dispatch_proxy_pool[proxy_key]
                        break
                else:
                    dispatch_proxy_pool = copy.deepcopy(proxy_running_list)
                    
                    ''' # Jun 22 注释掉一下两行。因为程序默认, proxy 永远是充足的
                    browser['proxy_name'] = ""
                    self.fill_conf_data(browser['port'], browser)
                    '''
            print(f"mode 1v3 done.")

    def pick_random_route_for_browser(self, browser_port):
        import random
        proxy_running_list = self.get_running_proxy_list()
        tmp_proxy = list(proxy_running_list.items())
        random.shuffle(tmp_proxy)
        proxy_running_list = dict(tmp_proxy)
        browser_list = self.get_list() # 获取 当前批次 浏览器 
        for browser in browser_list:
            if str(browser['port']) != str(browser_port): # 跳过当前 port
                continue
            if proxy_running_list:
                for proxy_key in proxy_running_list:
                    browser['proxy_name'] = proxy_key
                    # utils.log(f"PICK_RANDOM_ROUTE_FOR_BROWSER - pick proxy_key={proxy_key}. fill_conf_data.uid={browser['port']}")
                    self.fill_conf_data(browser['port'], browser)
                    return browser


    def actived_proxy_to_browser(self):
        """
        同步 actived_proxy_list 代理到浏览器。
        这里的代理是真正活跃的代理
        """
        proxy_running_list = utils.get_setting("actived_proxy_list", "*")

        # 打乱顺序 Aug 27 2024
        import random
        tmp_proxy = list(proxy_running_list.items())
        random.shuffle(tmp_proxy)
        proxy_running_list = dict(tmp_proxy)

        # 获取所有浏览器
        browser_list = self.get_list()
        # 匹配
        idx = -1
        for browser in browser_list:

            idx = idx + 1
            if proxy_running_list:
                for proxy_key in proxy_running_list:
                    browser['proxy_name'] = proxy_key
                    self.fill_conf_data(browser['port'], browser)
                    del proxy_running_list[proxy_key]
                    break
            else:
                browser['proxy_name'] = ""
                self.fill_conf_data(browser['port'], browser)
