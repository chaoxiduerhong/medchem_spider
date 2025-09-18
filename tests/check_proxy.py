import traceback
from fake_useragent import UserAgent
import requests

proxies = {"http": "192.168.0.113:11395", "https": "192.168.0.113:11395"}


def req(url):
    """
    通过requests的方式
    """

    ua = UserAgent()
    try:
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;"
                      "q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        print(headers)
        response = requests.get(url, allow_redirects=True, headers=headers, proxies=proxies, timeout=10)
        final_url = response.url
        return final_url
    except Exception as e:
        print(traceback.format_exc())
        print(e)
        return None
url = """https://www.google.com"""
ret = req(url)
print(ret)