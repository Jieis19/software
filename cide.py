from flask import Flask, send_file, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, FollowEvent
import io
import matplotlib.pyplot as plt
import requests
import math

# -----------------------------
# 初始化 Flask 與 LINE Bot
# -----------------------------
app = Flask(__name__)

line_bot_api = LineBotApi("YOUR_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("YOUR_CHANNEL_SECRET")

# -----------------------------
# 工具函數
# -----------------------------
def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # km
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def calculate_time(distance_km, speed_kmh=30):
    return (distance_km / speed_kmh) * 60  # 分鐘

# -----------------------------
# 生成地圖圖片函數
# -----------------------------
def generate_plot_image(lat2, lon2):
    lat1, lon1, label1 = 24.819735, 120.954769, "chayi"
    label2 = "car"
    lat3, lon3, label3 = 24.819032, 120.954563, 'park'

    distance = haversine(lon1, lat1, lon2, lat2)

    buf = io.BytesIO()
    plt.figure(figsize=(6,6))
    plt.scatter([lon1, lon2, lon3], [lat1, lat2, lat3], color="red")
    plt.plot([lon1, lon2, lon3], [lat1, lat2, lat3], "b--")
    plt.text(lon1, lat1, f" {label1}", color="red")
    plt.text(lon2, lat2, f" {label2}", color="red")
    plt.text(lon3, lat3, f" {label3}", color="red")
    plt.text((lon1+lon2)/2, (lat1+lat2)/2, f"{distance:.2f} km", color="blue", ha="center")
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

# -----------------------------
# Flask route /plot
# -----------------------------
@app.route("/plot")
def send_plot():
    lat2 = float(request.args.get("lat2", 22.627))  # 預設高雄
    lon2 = float(request.args.get("lon2", 120.301))
    buf = generate_plot_image(lat2, lon2)
    return send_file(buf, mimetype="image/png")

# -----------------------------
# 抓垃圾車資料並推播
# -----------------------------
def fetch_garbage_truck_info(user_id=None):
    url_location = "https://7966.hccg.gov.tw/WEB/_IMP/API/CleanWeb/getCarLocation"
    payload_location = 'rId=all'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(url_location, headers=headers, data=payload_location, timeout=10, verify=False)
        data = response.json()

        output = ""
        if data.get("statusCode") == 1 and "data" in data and "car" in data["data"]:
            for car in data["data"]["car"]:
                if car.get("routeName") in ["3-9海濱東大路(次、下午)", "3-5境福中正路(主、晚上)"]:
                    lat1 = float(car['lat'])
                    lon1 = float(car['lon'])
                    lat2 = 24.819735
                    lon2 = 120.954769
                    distance = haversine(lon1, lat1, lon2, lat2)
                    time_minutes = calculate_time(distance)

                    output += f"找到符合條件的車輛：{car['carNo']}\n"
                    output += f"路線名稱：{car.get('routeName')}\n"
                    output += f"兩點距離：{distance:.3f} 公里\n"
                    output += f"預計行駛時間（30 km/h）：{time_minutes:.2f} 分鐘\n\n"

                    # 用 /plot URL 推播圖片給 LINE
                    if user_id:
                        base_url = "https://你的網站域名/plot"  # <-- 改成你部署的 HTTPS 網址
                        image_url = f"{base_url}?lat2={lat1}&lon2={lon1}"
                        image_message = ImageSendMessage(
                            original_content_url=image_url,
                            preview_image_url=image_url
                        )
                        line_bot_api.push_message(user_id, image_message)
        else:
            output = "目前沒有符合條件的垃圾車"

        return output

    except Exception as e:
        return f"發生錯誤：{str(e)}"

# -----------------------------
# LINE Event
# -----------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "垃圾車":
        user_id = event.source.user_id
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="🔍 正在查詢垃圾車位置，請稍候...")
        )
        result = fetch_garbage_truck_info(user_id)
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=f"目前垃圾車資訊：\n{result}")
        )

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="謝謝你加我好友！\n輸入「垃圾車」即可查詢垃圾車位置")
    )

# -----------------------------
# Flask 主程式
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)