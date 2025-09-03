import os
import time
import hashlib
import statistics
import requests
import logging
from openpyxl import Workbook

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

# -------------------------------
# Logging 設定
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# -------------------------------
# LINE Bot 設定
# -------------------------------
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

# -------------------------------
# 建立 Selenium driver
# -------------------------------
def create_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    logging.info("Chrome driver 已啟動")
    return driver

# -------------------------------
# 爬蟲函式
# -------------------------------
def search_goods(keyword: str) -> str:
    logging.info(f"開始爬取商品: {keyword}")
    driver = create_driver()
    driver.get("https://www.goofish.com/")
    logging.info("已打開 Goofish 網站")
    time.sleep(15)

    cookies = driver.get_cookies()
    driver.quit()
    logging.info("Chrome driver 已關閉")

    if not cookies:
        logging.warning("無法取得 Cookie")
        return "⚠️ 無法取得 Cookie，請稍後再試"

    cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    cookie = cookie_string

    m_h5_tk_start = cookie.find("_m_h5_tk=") + len("_m_h5_tk=")
    m_h5_tk_end = cookie.find(";", m_h5_tk_start)
    m_h5_tk_value = cookie[m_h5_tk_start:m_h5_tk_end]
    token = m_h5_tk_value.split('_')[0]

    def GetSign(page):
        d_token = token
        j = int(time.time() * 1000)
        h = "34839810"
        c_data = f'{{"pageNumber":{page},"keyword":"{keyword}","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":"","customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"","userPositionJson":""}}'
        string = d_token + "&" + str(j) + "&" + h + "&" + c_data
        MD5 = hashlib.md5()
        MD5.update(string.encode("utf-8"))
        sign = MD5.hexdigest()
        return sign, j, c_data

    yeshu = 1
    wb = Workbook()
    ws = wb.active
    ws.append(["簡介", "連結", "價格", "地區"])

    for page in range(1, yeshu + 2):
        sign, j, c_data = GetSign(page)
        headers = {
            "cookie": cookie,
            "origin": "https://www.goofish.com",
            "referer": "https://www.goofish.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }
        url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
        data = {"data": c_data}
        params = {
            "jsv": "2.7.2",
            "appKey": "34839810",
            "t": j,
            "sign": sign,
            "v": "1.0",
            "type": "originaljson",
            "accountSite": "xianyu",
            "dataType": "json",
            "timeout": "20000",
            "api": "mtop.taobao.idlemtopsearch.pc.search",
            "sessionOption": "AutoLoginOnly"
        }

        logging.info(f"正在爬取第 {page} 頁")
        response = requests.post(url, headers=headers, params=params, data=data, verify=False)
        html_data = response.json()

        if "data" not in html_data or "resultList" not in html_data["data"]:
            logging.warning(f"第 {page} 頁無資料")
            continue

        for i in html_data["data"]["resultList"]:
            title = i["data"]["item"]["main"]["exContent"]["title"].strip()
            diqu = i["data"]["item"]["main"]["exContent"]["area"].strip()
            try:
                youfei = i["data"]["item"]["main"]["clickParam"]["args"]["tagname"]
            except:
                youfei = "不包郵"
            jianjie = str(youfei) + "+++++" + title
            id = i["data"]["item"]["main"]["exContent"]["itemId"]
            lianjie = f"https://www.goofish.com/item?id={id}"
            jiage = i["data"]["item"]["main"]["clickParam"]["args"]["price"]
            if float(jiage) > 1:
                ws.append([jianjie, lianjie, jiage, diqu])

    jiage_values = [float(row[2]) for row in ws.iter_rows(min_row=2, values_only=True) if row[2] is not None]

    if jiage_values:
        median_jiage = statistics.median(jiage_values) * 5
        if median_jiage < 1000:
            msg = f"『{keyword}』價格中位數: {median_jiage + median_jiage * 1:.2f} 元"
        else:
            msg = f"『{keyword}』價格中位數: {median_jiage + median_jiage * 0.6:.2f} 元"
    else:
        msg = f"『{keyword}』查無資料"

    logging.info(f"爬取完成: {msg}")
    return msg

# -------------------------------
# LINE Bot Webhook
# -------------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logging.info(f"收到 webhook: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid signature error")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    keyword = event.message.text
    logging.info(f"收到訊息: {keyword}")
    result = search_goods(keyword)
    logging.info(f"回覆訊息: {result}")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

# -------------------------------
# 本地測試
# -------------------------------
if __name__ == "__main__":
    logging.info("Flask 服務啟動")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
