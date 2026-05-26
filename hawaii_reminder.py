import requests
import schedule
import time
from datetime import datetime

BOT_TOKEN = "8911228307:AAEHsL0kTfD6IUfgvY3OUvLbPU3WUqngA3w"
CHAT_ID = "8978889851"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ 發送成功：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"❌ 發送失敗：{response.text}")
    except Exception as e:
        print(f"❌ 錯誤：{e}")

def morning_reminder():
    message = """🌅 <b>早安！達人哥</b>

📋 <b>今日待辦清單</b>

🔴 最優先
☐ 查今日政府標案
☐ 回覆客戶詢問
☐ 確認現場人員工作狀況

🟡 重要
☐ 確認本週短影音進度
☐ 處理報價單或請款單

💪 今天也加油！"""
    send_telegram(message)

def monday_reminder():
    message = """📅 <b>週一提醒</b>

☐ 閱讀產業雷達報告
☐ 確認本週短影音主題
☐ 確認現場工作排程
☐ 回顧上週指標"""
    send_telegram(message)

schedule.every().day.at("08:30").do(morning_reminder)
schedule.every().monday.at("08:30").do(monday_reminder)

print("🚀 提醒機器人已啟動！")
send_telegram("✅ 夏威夷提醒機器人設定成功！\n每天早上 08:30 會自動提醒你。")

while True:
    schedule.run_pending()
    time.sleep(30)