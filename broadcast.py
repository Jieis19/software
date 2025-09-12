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












from linebot import LineBotApi
from linebot.models import TextSendMessage

# 初始化 line_bot_api
line_bot_api = LineBotApi("你的 LINE CHANNEL ACCESS TOKEN")

def fetch_garbage_truck_info():
    url_location = "https://7966.hccg.gov.tw/WEB/_IMP/API/CleanWeb/getCarLocation"
    url_track = "https://7966.hccg.gov.tw/WEB/_IMP/API/CleanWeb/getRouteTrack"
    payload_location = 'rId=all'
    payload_track = 'rId=112'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    global lon1, lat1
    try:
        response = requests.post(url_location, headers=headers, data=payload_location, timeout=10, verify=False)
        if response.status_code != 200:
            return "請求失敗，HTTP 狀態碼：" + str(response.status_code)

        data = response.json()
        target_x = "120.954769"
        target_y = "24.819735"
        find_flag = True

        if data.get("statusCode") == 1 and "data" in data and "car" in data["data"]:
            output = ""
            for car in data["data"]["car"]:
                if car.get("routeName") in ["3-9海濱東大路(次、下午)", "3-5境福中正路(主、晚上)"]:
                    find_flag = False
                    lat1 = float(car['lat'])
                    lon1 = float(car['lon'])
                    lat2 = float(target_y)
                    lon2 = float(target_x)
                    send_plot()
                    distance, time_minutes = calculate_drive_time([lon1, lat1], [lon2, lat2])

                    output += f"找到符合條件的車輛：{car['carNo']}\n"
                    output += f"路線名稱：{car.get('routeName')}\n"
                    output += f"兩點之間距離：{distance:.3f} 公里\n"
                    output += f"預計行駛時間（30 km/h）：{time_minutes+1:.2f} 分鐘\n\n"

                    # 🔔 如果小於 2 分鐘就廣播通知
                    if time_minutes + 1 < 2:
                        msg = f"🚛 垃圾車即將抵達！（約 {time_minutes+1:.1f} 分鐘）\n路線：{car.get('routeName')}"
                        line_bot_api.broadcast(TextSendMessage(text=msg))

            if not output:
                output = "沒有發現符合條件名稱\n正在自動搜尋附近車輛...\n"

        else:
            output = "沒有發現符合條件名稱\n正在自動搜尋附近車輛...\n"

        if find_flag:
            track_response = requests.post(url_track, headers=headers, data=payload_track, timeout=10, verify=False)
            track_data = track_response.json()
            car_response = requests.post(url_location, headers=headers, data=payload_location, timeout=10, verify=False)
            car_data = car_response.json()
            tracks = track_data["data"]["track"]
            nearby_cars = []

            for car in car_data["data"]["car"]:
                lon = float(car["lon"])
                lat = float(car["lat"])
                if is_near_track(lon, lat, tracks):
                    nearby_cars.append(car)

            output = "在軌跡附近的車輛訊息：\n"
            for car in nearby_cars:
                lat1 = float(car['lat'])
                lon1 = float(car['lon'])
                lat2 = float(target_y)
                lon2 = float(target_x)
                send_plot()
                distance, time_minutes = calculate_drive_time([lon1, lat1], [lon2, lat2])
                output += f"車輛編號：{car['carNo']}\n"
                output += f"兩點之間距離：{distance:.3f} 公里\n"
                output += f"預計行駛時間（30 km/h）：{time_minutes:.2f} 分鐘\n\n"

                # 🔔 廣播條件
                if time_minutes < 2:
                    msg = f"🚛 垃圾車即將抵達！（約 {time_minutes:.1f} 分鐘）\n車輛編號：{car['carNo']}"
                    line_bot_api.broadcast(TextSendMessage(text=msg))

        return output

    except Exception as e:
        return "發生錯誤：" + str(e)
