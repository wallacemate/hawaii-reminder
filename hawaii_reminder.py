import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
APPS_SCRIPT_URL = os.environ.get("APPS_SCRIPT_URL")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ 發送成功")
        else:
            print(f"❌ 發送失敗：{response.text}")
    except Exception as e:
        print(f"❌ 錯誤：{e}")

def get_memo():
    """從試算表讀取備忘錄內容"""
    try:
        url = f"{APPS_SCRIPT_URL}?action=getMemo"
        res = requests.get(url, timeout=15)
        data = res.json()
        if data.get("success") and data.get("memo"):
            return data["memo"].strip()
        return ""
    except Exception as e:
        print(f"備忘錄讀取失敗：{e}")
        return ""

def get_weather():
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": os.environ.get("CWA_API_KEY"),
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

def get_pest_alert():
    month = datetime.now().month
    alerts = {
        1:  "❄️ 低溫月份，老鼠活動仍頻繁，注意室內防鼠",
        2:  "🌱 春節前後食物增多，蟑螂、老鼠活躍，提醒客戶預防",
        3:  "🌸 春季來臨，螞蟻開始建巢，馬陸陸續出現",
        4:  "🌧️ 梅雨前期，馬陸、螞蟻高峰期，蟑螂開始活躍",
        5:  "☔ 梅雨季！蟑螂繁殖速度加快，蚊蟲孳生，最佳防治時機",
        6:  "🔥 高溫多濕，蟑螂、蚊子、蒼蠅全面爆發，業務旺季",
        7:  "🌪️ 颱風季，積水造成蚊子暴增，颱風後是最佳消毒時機",
        8:  "🌊 颱風後積水，登革熱風險高，主動聯繫客戶消毒",
        9:  "🍂 老鼠開始準備過冬糧食，入侵室內機率大增",
        10: "🍁 秋季老鼠最活躍，白蟻也開始活動，馬陸再次出現",
        11: "🌬️ 氣溫下降，蟲害減少，但老鼠仍需注意",
        12: "❄️ 冬季蟲害低峰，老鼠防治持續，為明年春季預防做準備",
    }
    return alerts.get(month, "注意當季病蟲害")

def search_tenders():
    keywords = ["病媒防治", "消毒", "環境維護", "登革熱"]
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for keyword in keywords:
        try:
            url = f"https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?firstSearch=true&searchType=basic&keyword={keyword}&tenderStatus=TENDER_DECLARATION"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200 and keyword in res.text:
                results.append(f"• 發現「{keyword}」相關標案，建議登入採購網確認")
                break
        except:
            continue
    if not results:
        return "今日暫無符合條件的新標案\n建議至 taiwanbuying.com.tw 手動確認"
    return "\n".join(results)

def get_monthly_report():
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = """你是一位專業的商業顧問，請針對台灣病媒防治與清潔服務產業，
從以下三個面向提供本月最新的產業洞察報告，每個面向100字以內，使用繁體中文：
1. 經營者視野：目前經營者面臨的最大挑戰與機會
2. 消費者視野：消費者行為與需求的最新變化
3. 同業視野：競爭對手的動向與市場趨勢
最後提供一句本月最重要的行動建議。"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 600}
        }
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"產業報告暫時無法生成：{e}"

def build_memo_block(memo):
    """把備忘錄內容格式化成待辦清單區塊"""
    if not memo:
        return ""
    lines = [line.strip() for line in memo.splitlines() if line.strip()]
    formatted = "\n".join(f"☐ {line}" for line in lines)
    return f"\n📝 <b>今日待辦（工具箱備忘錄）</b>\n{formatted}\n"

def build_message():
    now = datetime.now()
    today_str = now.strftime("%Y/%m/%d")
    is_monday = now.weekday() == 0
    is_first_day = now.day == 1
    weather = get_weather()
    pest_alert = get_pest_alert()
    tenders = search_tenders()
    memo = get_memo()
    memo_block = build_memo_block(memo)

    if is_first_day:
        report = get_monthly_report()
        message = f"""🗓 <b>每月第一天｜{today_str}</b>

🌤 <b>屏東今日天氣</b>
{weather}

🐛 <b>本月病蟲害提醒</b>
{pest_alert}
{memo_block}
🏛 <b>標案搜尋結果</b>
{tenders}

📊 <b>本月產業AI分析報告</b>
{report}

💪 新的一個月，加油！"""

    elif is_monday:
        message = f"""📅 <b>週一早安｜{today_str}</b>

🌤 <b>屏東今日天氣</b>
{weather}

🐛 <b>本週病蟲害提醒</b>
{pest_alert}
{memo_block}
🏛 <b>標案搜尋結果</b>
{tenders}

💪 新的一週，加油！"""

    else:
        message = f"""🌅 <b>早安！達人哥｜{today_str}</b>

🌤 <b>屏東今日天氣</b>
{weather}

🐛 <b>本月病蟲害提醒</b>
{pest_alert}
{memo_block}
🏛 <b>標案搜尋結果</b>
{tenders}

💪 今天也加油！"""

    return message

print("程式開始執行")
print(f"BOT_TOKEN: {'有設定' if BOT_TOKEN else '沒有設定！'}")
print(f"CHAT_ID: {'有設定' if CHAT_ID else '沒有設定！'}")
print(f"APPS_SCRIPT_URL: {'有設定' if APPS_SCRIPT_URL else '沒有設定！'}")
message = build_message()
print("訊息建立完成，準備發送...")
send_telegram(message)
print("程式執行完畢")
