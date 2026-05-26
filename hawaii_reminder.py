import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ===== 天氣預報 =====
def get_weather():
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": "CWA-OPEN-DATA",
            "locationName": "屏東縣",
            "elementName": "Wx,MinT,MaxT,PoP"
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        location = data["records"]["location"][0]
        elements = {e["elementName"]: e["time"][0]["parameter"] for e in location["weatherElement"]}
        wx = elements["Wx"]["parameterName"]
        min_t = elements["MinT"]["parameterName"]
        max_t = elements["MaxT"]["parameterName"]
        pop = elements["PoP"]["parameterName"]
        return f"{wx}　{min_t}°C - {max_t}°C　降雨機率 {pop}%"
    except:
        return "天氣資料暫時無法取得"

# ===== 病蟲害好發提醒 =====
def get_pest_alert():
    month = datetime.now().month
    alerts
