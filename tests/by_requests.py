import traceback
from fake_useragent import UserAgent
import requests

proxies = {"http": "192.168.0.109:10809", "https": "192.168.0.109:10809"}


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
        print(e)
        print(traceback.format_exc())
        return None
url = """https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6T0A77qZKS1JGaHN72vzU1ZANNKKdKZ4JSBC11FV5kWGpt4LF-KCf33eqLx0FWZ3qPZBiuRdLR9fMug_qedfEMlNpoUD6OM6JsMDEi4LZbT9ox3E3R_xt6pa1EYUc5t0RLQTk4j3kYXb2Ew8vhxWYXtllgRIhHfRkVLGo5zw659QfLJh5rJw1fx3DxnnJkpkA_FZ_eX2ZJ-jbPMiWJs3o9vrkkM106g=="""

ret = req(url)
print(ret)