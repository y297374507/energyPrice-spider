import json
import os
import time
from datetime import datetime
from urllib.parse import quote
import requests

# 当前时间
time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# GBK urlencode
def gbk_quote(s):
    return quote(s.encode("gbk"))


# 当前时间戳
timestamp = int(time.time() * 1000)

# time 参数
time_param = quote(
    " where  DATE_FORMAT(END_DATE,'%Y-%m-%d') >= '-0002-11-30'"
)

# CCTD接口
cctd_url = (
    "https://www.cctd.com.cn/datasql.php?"
    f"data={gbk_quote('CCTD秦皇岛动力煤价格')}"
    f"&name={gbk_quote('CCTD秦皇岛动力煤价格')}"
    f"&time={time_param}"
    "&draw=1"
    "&start=0"
    "&length=10"
    "&search[value]="
    "&search[regex]=false"
    "&extra_search="
    f"&_={timestamp}"
)

# 配置接口
urls = [
    {
        "type": "中国LNG出厂价格（全国）",
        "url": "https://www.shpgx.com/marketzhishu/list/3/22",
    },
    {"type": "中国汽柴油批发价格", "url": "https://www.shpgx.com/marketzhishu/list2"},
    {"type": "CCTD秦皇岛动力煤价格", "url": cctd_url},
]

# 存储读取到的历史数据
history_data = []
json_filename = "data.json"

# 如果存在 data.json 则读取历史
if os.path.exists(json_filename):
    try:
        with open(json_filename, "r", encoding="utf-8") as f:
            history_data = json.load(f)
    except Exception as e:
        print(f"读取旧 {json_filename} 失败，将重新创建: {e}")
        history_data = []

# 建立本次抓取的数据结构
current_entry = {"timestamp": time_str, "items": {}}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

for item in urls:
    try:
        response = requests.get(item["url"], headers=headers, timeout=30)
        response.raise_for_status()
        raw_json = response.json()

        print(f"{item['type']} 获取成功")
        current_entry["items"][item["type"]] = raw_json

    except Exception as e:
        print(f"{item['type']} 获取失败: {e}")
        current_entry["items"][item["type"]] = None

# 追加本次抓取结果
history_data.append(current_entry)

# 数量控制：保持最新 100 条历史记录
if len(history_data) > 100:
    history_data = history_data[-100:]

# 写入 JSON 文件
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(history_data, f, ensure_ascii=False, indent=2)

print(f"数据已成功更新并保存至 {json_filename}（共 {len(history_data)} 条历史快照）")
