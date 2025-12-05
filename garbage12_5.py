import os, math, io
import schedule, threading, time
import base64
import requests
from datetime import datetime
from flask import Flask, request, abort, send_file
import matplotlib.pyplot as plt
from matplotlib import font_manager
# 使用 v3 SDK 的模块
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from linebot.models.events import FollowEvent
import urllib.request
import logging
import urllib3 # 1. 引入 urllib3

app = Flask(__name__)

# 2. 關閉 SSL 警告 (讓 Log 乾淨一點)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# -------------------------------
# LINE & API 設定
# -------------------------------
HANNEL_SECRET = "ea78c4c59c384e5ce230ddba0d"
CHANNEL_ACCESS_TOKEN = "eBut4gjXhGsshJZJfMoVDFE1fsytjfo5m74mnbRVJX0DoAiQlAQ5XF3319Ak4sSIFIkI9mTk1QF1q1hJirKXIsAgXShHLqTfcl60h9sMgRq68zpnWe7bSmHALH6UVxdX+dV1Sg/1LlqU8HQdB04t89/1O/w1cDnyilFU="
API_KEY = "jJGxn6qJ3pOBtEvc_U71uuJmOn-1_YK7zZ6GiVFhtcg" 

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(HANNEL_SECRET)

# 全域變數控制通知狀態
alert_flag = True
lon1 = 0
lat1 = 0

# -------------------------------
# 字型設定 (保持不變)
# -------------------------------
font_folder = "./fonts"
font_filename = "NotoSansCJK-Regular.ttc"
font_file_path = os.path.join(font_folder, font_filename)

if not os.path.exists(font_folder):
    os.makedirs(font_folder)

if not os.path.exists(font_file_path):
    print("正在下載思源黑體字型...")
    try:
        url = "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf"
        urllib.request.urlretrieve(url, font_file_path)
    except Exception as e:
        print(f"字型下載失敗: {e}")
else:
    print(f"字型已存在：{font_file_path}")

prop = font_manager.FontProperties(fname=font_file_path)

# -------------------------------
# 計算與工具函式 (保持不變)
# -------------------------------
def haversine(lon1, lat1, lon2, lat2):
    R = 6371 
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def calculate_drive_time(origin, destination):
    url = "https://router.hereapi.com/v8/routes"
    params = {
        "apiKey": API_KEY,
        "transportMode": "car",
        "origin": f"{origin[1]},{origin[0]}",
        "destination": f"{destination[1]},{destination[0]}",
        "return": "summary",
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]["sections"][0]["summary"]
            distance_km = route["length"] / 1000 
            duration_min = route["duration"] / 60 
            return distance_km, duration_min
        else:
            dist = haversine(origin[0], origin[1], destination[0], destination[1])
            return dist, (dist/30)*60 
    except Exception as e:
        logging.error(f"Here Maps API Error: {e}")
        dist = haversine(origin[0], origin[1], destination[0], destination[1])
        return dist, (dist/30)*60

def is_near_track(lon, lat, track, threshold=3):
    for path in track:
        for point in path:
            track_lon = float(point["X"])
            track_lat = float(point["Y"])
            if haversine(lon, lat, track_lon, track_lat) < threshold:
                return True
    return False

# -------------------------------
# 核心邏輯：抓取垃圾車資訊
# -------------------------------
def fetch_garbage_truck_info(is_auto_check=False):
    url_location = "https://7966.hccg.gov.tw/WEB/_IMP/API/CleanWeb/getCarLocation"
    url_track = "https://7966.hccg.gov.tw/WEB/_IMP/API/CleanWeb/getRouteTrack"
    payload_location = 'rId=all'
    payload_track = 'rId=112'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    global lon1, lat1, alert_flag
    
    try:
        response = requests.post(url_location, headers=headers, data=payload_location, timeout=10, verify=False)
        if response.status_code != 200:
            return f"請求失敗，HTTP 狀態碼：{response.status_code}"

        data = response.json()
        target_x = "120.954769" # 家的經度
        target_y = "24.819735" # 家的緯度
        
        found_cars = [] 

        if data.get("statusCode") == 1 and "data" in data and "car" in data["data"]:
            for car in data["data"]["car"]:
                if car.get("routeName") in ["3-9海濱東大路(次、下午)", "3-5境福中正路(主、晚上)"]:
                    found_cars.append(car)

        if not found_cars:
            track_response = requests.post(url_track, headers=headers, data=payload_track, timeout=10, verify=False)
            track_data = track_response.json()
            if "data" in track_data and "track" in track_data["data"]:
                tracks = track_data["data"]["track"]
                for car in data["data"]["car"]:
                    if is_near_track(float(car["lon"]), float(car["lat"]), tracks):
                        found_cars.append(car)

        output = ""
        if found_cars:
            for car in found_cars:
                lat1 = float(car['lat'])
                lon1 = float(car['lon'])
                lat2 = float(target_y)
                lon2 = float(target_x)
                
                # 3. [修正重點] 移除這裡的 send_plot()
                # 這裡不需要呼叫 send_plot()，因為我們已經更新了上面的 lat1, lon1。
                # 等使用者或 LINE 伺服器請求 /plot 時，才會用到那些變數。
                # send_plot() # <--- 刪除這行
                
                distance, time_minutes = calculate_drive_time([lon1, lat1], [lon2, lat2])
                final_time = time_minutes + 1

                car_info = f"車號：{car['carNo']}\n路線：{car.get('routeName', '未知')}\n距離：{distance:.2f} km\n預估時間：{final_time:.1f} 分鐘\n"
                output += car_info + "\n"

                if is_auto_check:
                    # 邏輯: 時間小於 4 分鐘 且 警報開啟
                    if final_time < 4:
                        if alert_flag:
                            msg = f"🚛 垃圾車來囉！\n{car_info}\n快準備出門！"
                            line_bot_api.broadcast(TextSendMessage(text=msg))
                            # 發送圖片
                            image_url = "https://garbage-xcnc.onrender.com/plot"
                            line_bot_api.broadcast(ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
                            
                            alert_flag = False
                            logging.info("已發送通知，關閉 Alert Flag")
                    else:
                        alert_flag = True
                        logging.info("垃圾車尚遠，重置 Alert Flag 為 True")
        else:
            output = "目前附近沒有發現垃圾車。"
            if is_auto_check:
                alert_flag = True

        return output

    except Exception as e:
        logging.error(f"Error in fetch_garbage_truck_info: {e}")
        return f"發生錯誤：{str(e)}"

# -------------------------------
# 排程工作
# -------------------------------
def job():
    """每分鐘執行一次，檢查是否在指定時段"""
    
    # 4. [修正重點] 加入 app_context
    # 雖然移除 send_plot 後可能不會報錯，但加上這個是最佳實踐，
    # 確保在這個區塊內如果用到 Flask 的功能（如 config）不會崩潰。
    with app.app_context():
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        is_target_time = False

        if current_hour == 6:
            is_target_time = True
        
        elif current_hour == 9 and current_minute >= 30:
            is_target_time = True
        elif current_hour == 10 and current_minute <= 30:
            is_target_time = True
        elif current_hour == 17 and current_minute >= 30: # 修正：你的 log 是 17 點，這裡補上邏輯
            is_target_time = True
        elif current_hour == 18 and current_minute <= 30:
             is_target_time = True

        # 為了測試，你可以暫時把時段判斷拿掉，直接執行看看
        # is_target_time = True 
        
        if is_target_time:
            logging.info(f"進入監控時段 ({now.strftime('%H:%M')})，開始檢查垃圾車...")
            fetch_garbage_truck_info(is_auto_check=True)
        else:
            global alert_flag
            alert_flag = True

def run_schedule():
    schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(10)

t = threading.Thread(target=run_schedule, daemon=True)
t.start()

# -------------------------------
# Flask Routes (保持不變)
# -------------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/ping", methods=['GET'])
def ping():
    return "OK", 200

@app.route("/plot")
def send_plot():
    global lon1, lat1
    lat2, lon2, label2 = 24.819735, 120.954769, "家益大舜"
    label1 = "Car"
    
    lat3, lon3, label3 = 24.819032, 120.954563, '飛機公園'
    lat4, lon4, label4 = 24.817515, 120.957245, 'hsinchu活動中心'
    
    distance = haversine(lon1, lat1, lon2, lat2)

    buf = io.BytesIO()
    plt.figure(figsize=(6,6))
    plt.scatter([lon1, lon2, lon3, lon4], [lat1, lat2, lat3, lat4], color="red")
    plt.plot([lon1, lon2], [lat1, lat2], "b--")
    
    plt.text(lon1, lat1, f" {label1}", color="red", fontproperties=prop)
    plt.text(lon2, lat2, f" {label2}", color="red", fontproperties=prop)
    plt.text(lon3, lat3, f" {label3}", color="red", fontproperties=prop)
    plt.text(lon4, lat4, f" {label4}", color="red", fontproperties=prop)
    
    mid_lon = (lon1 + lon2) / 2
    mid_lat = (lat1 + lat2) / 2
    plt.text(mid_lon, mid_lat, f"{distance:.2f} km", color="blue", ha="center", fontsize=12)
    
    plt.grid(True)
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

def send_loading_animation(user_id):
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "chatId": user_id,
        "loadingSeconds": 20
    }
    requests.post(url, headers=headers, json=data)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "垃圾車":
        user_id = event.source.user_id
        send_loading_animation(user_id)

        result = fetch_garbage_truck_info(is_auto_check=False) 
        image_url = "https://garbage-xcnc.onrender.com/plot"

        try:
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=f"目前資訊：\n{result}"),
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                ]
            )
        except Exception as e:
            logging.error(f"Reply failed (timeout?), trying push: {e}")
            line_bot_api.push_message(
                user_id,
                [
                    TextSendMessage(text=f"目前資訊：\n{result}"),
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                ]
            )

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="歡迎！輸入「垃圾車」可查詢即時位置。\n我會在 14:00~15:00 與 17:30~18:30 自動幫你監控垃圾車喔！")
    )

if __name__ == "__main__":
    app.run()
