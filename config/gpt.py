# -*- coding:utf-8 -*-
# Desc: project app configuration
"""
"""
from utils import env, template
import subprocess,re

class gptConf:

    # --------------------- -*- 基础配置 -*- ---------------------
    debug: bool = bool(int(env("DEBUG", 0)))

    # 项目名称
    project_name = env("project_name", "medchemexpress")

    # 日志文件存储路径
    log_file_path = env("log_file_path", project_name)

    error_log_file_path = env("error_log_file_path", f"{project_name}_error")

    log_root = env("log_root", f"./storage/logs/{project_name}")

    start_bid_file = env("start_bid_file", project_name)

    browser_config_path = env("browser_config_path", "browser")

    proxy_config_path = env("proxy_config_path", "proxy")

    browser_status_file_path = env("browser_status_file_path", "browser_status")

    proxy_stop_queue_file = env("proxy_stop_queue_file", "stop_proxy_queue")



    # 入口
    url = "https://www.medchemexpress.com/"

    proxy_source_type = env("proxy_source_type", "")
    proxy_countries = env("proxy_countries", "")

    # 禁用的，多个用逗号隔开
    dis_source_type = env("dis_source_type", "")
    clear_cache = env("clear_cache", True)

    is_save_log= bool(int(env("is_save_log", 0)))

    @staticmethod
    def get_proxy_server_ipv4():
        ipv4 = None
        try: # 使用 ping -4 命令，并捕获输出
            process = subprocess.Popen(['ping', '-4', 'dell-mini-1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # 将输出转换为字符串，并使用正则表达式提取 IPv4 地址
            stdout_str = stdout.decode('gbk')  # 注意编码，windows中文系统一般为gbk
            ipv4_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', stdout_str)

            if ipv4_match:
                ipv4 = ipv4_match.group(1)
                print(f"成功获取 proxy-server IPv4 地址: {ipv4}")
        except Exception as e:
            print(f"获取 proxy-server IPv4 地址时发生错误：{e}")
        if not ipv4:
            ipv4 = env("proxy_server", "127.0.0.1")

        return ipv4

    # proxy_server = get_proxy_server_ipv4()
    # 代理 server 服务器
    proxy_server = env("proxy_server", "127.0.0.1")

    proxy_server_for_login = env("proxy_server_for_login", f"{proxy_server}")

    # 代理主机ip地址
    proxy_host = env("proxy_host", proxy_server)

    # 远程服务器地址：
    remote_server = env("remote_server", f"http://{proxy_server}:8053")

    # 异常数据回补充。将爬取失败的回补
    fetch_failed_fill = bool(int(env("fetch_failed_fill", 0)))

    # 入口 不同的入口代表不同的线程 - 分多线程去爬。暂时不考虑那个快 那个慢的问题
    entry_urls = [
        "https://www.medchemexpress.com/pathway.html",
        # "https://www.medchemexpress.com/NaturalProducts/Natural%20Products.html",
        # "https://www.medchemexpress.com/oligonucleotides.html",
        # "https://www.medchemexpress.com/isotope-compound/isotope-compound.html",
        # "https://www.medchemexpress.com/dyereagents/dye-reagents.html",
        # "https://www.medchemexpress.com/inhibitory-antibodies.html",
        # "https://www.medchemexpress.com/biochemical-assay-reagents.html",
        # # "https://www.medchemexpress.com/antibodies.html", # 抗体不用爬
        # "https://www.medchemexpress.com/enzyme.html",
        # "https://www.medchemexpress.com/standards.html",
        # "https://www.medchemexpress.com/peptides.html",
        # "https://www.medchemexpress.com/induced-disease-model.html",
        # "https://www.medchemexpress.com/gmp-small-molecules.html"
    ]

    # 以最后一个为url节点作为匹配。该分类创建的页面后续分类还是这个
    page_group = {
        "pathway": ['pathway'],
        "natural": ['natural-products', 'oligonucleotides', 'isotope-compound', 'dye-reagents', 'inhibitory-antibodies', 'biochemical-assay-reagents', 'antibodies', 'enzyme'],
        "standards": ['standards'],
        'peptides': ['peptides', 'induced-disease-model'],
        'gmp': ['gmp-small-molecules']
    }
