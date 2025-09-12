from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import schedule
import time
import threading

line_bot_api = LineBotApi("你的 LINE CHANNEL ACCESS TOKEN")
handler = WebhookHandler("你的 LINE CHANNEL SECRET")

# 你的垃圾車查詢函數
def fetch_garbage_truck_info():
    # ... 你之前的程式 ...
    return "垃圾車查詢結果 (這裡會放結果)"

# ---- LINE 關鍵字觸發 ----
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text.strip() == "垃圾車":
        result = fetch_garbage_truck_info()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )

# ---- 排程每天 14:00 自動廣播 ----
def job():
    result = fetch_garbage_truck_info()
    line_bot_api.broadcast(TextSendMessage(text="📢 每日14:00垃圾車提醒\n\n" + result))

def run_schedule():
    schedule.every().day.at("14:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(30)

# 開新 thread 執行排程，不會卡住主程式
t = threading.Thread(target=run_schedule, daemon=True)
t.start()