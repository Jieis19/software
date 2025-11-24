import os
import logging
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

# --- 建議將敏感資訊放在環境變數，這裡先示範變數位置 ---
# 請務必去重新產生這些 Key，因為舊的已經曝光
LINE_CHANNEL_ACCESS_TOKEN = "你的_LINE_ACCESS_TOKEN"
LINE_CHANNEL_SECRET = "你的_LINE_CHANNEL_SECRET"
GEMINI_API_KEY = "你的_GEMINI_API_KEY"

app = Flask(__name__)

# 設定 Log，確保能印出 INFO等級以上的訊息
logging.basicConfig(level=logging.INFO)

# 初始化 LINE Bot
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# === 1. 解決 404 錯誤：加入健康檢查首頁 ===
@app.route("/", methods=['GET'])
def home():
    return 'Hello World! The bot is active.', 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    # 印出收到的內容，確認 LINE 有傳資料過來
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature.")
        abort(400)

    return 'OK'

# === 2. 處理訊息邏輯：修正重複回覆問題 ===
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    logging.info(f"收到使用者訊息: {user_message}") # 清楚印出 Log

    keyword = "小g"
    reply_text = "" # 準備要回傳的文字變數

    # 邏輯判斷：
    # 如果有關鍵字 -> 問 Gemini
    # 如果沒有關鍵字 -> 什麼都不做 (或是你可以改成 echo)
    
    if keyword in user_message.lower():
        try:
            # 這裡可以選擇是否要把 "小g" 去掉，目前保留
            logging.info("觸發關鍵字，呼叫 Gemini...")
            
            response = model.generate_content(user_message)
            reply_text = response.text
            
            logging.info("Gemini 回覆生成成功")

        except Exception as e:
            reply_text = "抱歉，小g現在有點累，請稍後再試。"
            logging.error(f"Gemini Error: {e}")
    else:
        # 如果沒有關鍵字，這裡選擇「不回覆」任何東西
        # 這樣就不會跟上面的邏輯衝突
        # 如果你想做「回聲蟲」，可以在這裡設定 reply_text = user_message
        logging.info("未觸發關鍵字，忽略訊息")
        return # 直接結束函式，不回覆

    # === 統一在這裡回覆 ===
    # 只有當 reply_text 有內容時才回覆
    if reply_text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
