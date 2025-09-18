import requests
import time
from datetime import datetime

url = "http://192.168.0.183:8053/proxy_issue_random"
output_file = "index_ids.txt"

idx = 0

while True:
    if idx > 500:
        break
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ret") == 1 and "data" in data:
                index_id = data["data"].get("indexId")
                if index_id:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    record = f"【{now_str}】{index_id}"
                    with open(output_file, "a", encoding="utf-8") as f:
                        f.write(record + "\n")
                    print(f"写入记录: {record}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求错误: {e}")

    time.sleep(1)  # 根据实际情况调整频率
