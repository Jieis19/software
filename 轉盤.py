import IPython
from google.colab import output

# 確保這段程式碼從最左側開始，不要有額外空格
html_code = """
<div style="text-align:center; font-family: 'Microsoft JhengHei', sans-serif; background-color: #ffffff; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 450px; margin: auto;">
    <h2 id="result" style="color: #333; margin-bottom: 20px;">晚餐好困難_地點</h2>
    
    <div style="position: relative; display: inline-block; width: 350px; height: 350px;">
        <canvas id="wheel" width="350" height="350"></canvas>
        
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 50px; height: 50px; background: white; border-radius: 50%; box-shadow: 0 0 10px rgba(0,0,0,0.2); z-index: 5; border: 4px solid #f0f0f0;"></div>
        
        <div id="pointer" style="
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0; 
            height: 0; 
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-top: 30px solid #ff4757;
            z-index: 10;
            filter: drop-shadow(0px 2px 2px rgba(0,0,0,0.3));
        "></div>
    </div>
    
    <br><br>
    <button onclick="spin()" style="
        padding: 15px 40px; 
        font-size: 22px; 
        font-weight: bold;
        cursor: pointer; 
        background: #333; 
        color: white; 
        border: none; 
        border-radius: 10px;
        transition: 0.2s;
    " onmousedown="this.style.transform='scale(0.9)'" onmouseup="this.style.transform='scale(1)'">
        START
    </button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = ["中正西路", "南寮", "新豐", "夜市", "湳雅", "竹北"];
const colors = ["#ff4d4d", "#ffaf40", "#fffa65", "#32ff7e", "#7efff5", "#18dcff", "#7d5fff"];
let currentAngle = 0;
let isSpinning = false;

function drawWheel() {
    const arc = (2 * Math.PI) / options.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    options.forEach((opt, i) => {
        const angle = currentAngle + i * arc;
        
        // 畫扇形
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.moveTo(175, 175);
        ctx.arc(175, 175, 170, angle, angle + arc);
        ctx.fill();
        ctx.strokeStyle = "rgba(0,0,0,0.1)";
        ctx.stroke();
        
        // 畫文字
        ctx.save();
        ctx.translate(175, 175);
        ctx.rotate(angle + arc / 2);
        ctx.fillStyle = "#333";
        ctx.font = "bold 16px Microsoft JhengHei";
        ctx.textAlign = "right";
        ctx.fillText(opt, 150, 6);
        ctx.restore();
    });
}

function spin() {
    if (isSpinning) return;
    isSpinning = true;
    
    let speed = Math.random() * 0.4 + 0.6; // 初始速度
    const friction = 0.985; 
    
    function animate() {
        currentAngle += speed;
        speed *= friction;
        drawWheel();
        
        if (speed > 0.002) {
            requestAnimationFrame(animate);
        } else {
            isSpinning = false;
            // 決定結果 (指針在正上方，即 -90度 或 1.5*PI 位置)
            const totalArc = 2 * Math.PI;
            const pointerAngle = 1.5 * Math.PI;
            const normalizedAngle = (pointerAngle - (currentAngle % totalArc) + totalArc) % totalArc;
            const index = Math.floor(normalizedAngle / (totalArc / options.length));
            document.getElementById('result').innerText = "結果：" + options[index];
        }
    }
    animate();
}

drawWheel();
</script>
"""

display(IPython.display.HTML(html_code))







import IPython
from google.colab import output
import requests

# --- 第一步：定義獲取餐廳名稱的函數 ---
# 這裡使用一個模擬搜尋，你可以手動輸入，或者未來串接真實 API
def get_nearby_restaurants(location_name):
    # 模擬從特定地點抓取的熱門餐廳 (以竹科為例)
    if "竹科" in location_name or "新竹科學園區" in location_name:
        return ["老爺酒店", "金山街義大利麵", "段純貞牛肉麵", "曉江山", "築間火鍋", "壽司郎"]
    elif "板橋" in location_name:
        return ["六必居砂鍋粥", "油庫口麵線", "薄多義", "鼎泰豐", "聚火鍋", "布娜飛"]
    else:
        # 預設通用選項
        return ["麥當勞", "肯德基", "必勝客", "星巴克", "便利商店", "隨便吃"]

# 讓使用者輸入地點
target_location = input("請輸入想搜尋的地點（例如：竹科）：")
restaurants = get_nearby_restaurants(target_location)
res_list_js = str(restaurants) # 轉換為 JS 陣列格式

# --- 第二步：帶入 HTML 轉盤 ---
html_code = f"""
<div style="text-align:center; font-family: 'Microsoft JhengHei', sans-serif; background: #fff; padding: 20px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); max-width: 450px; margin: auto;">
    <h3 style="color: #666; margin: 0;">目前定位：{target_location}</h3>
    <h2 id="result" style="color: #333; margin: 10px 0 20px 0;">按下 START 決定晚餐</h2>
    
    <div style="position: relative; display: inline-block; width: 350px; height: 350px;">
        <canvas id="wheel" width="350" height="350"></canvas>
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: white; border-radius: 50%; z-index: 5; border: 3px solid #eee;"></div>
        <div id="pointer" style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid #ff4757; z-index: 10;"></div>
    </div>
    
    <br><br>
    <button onclick="spin()" style="padding: 15px 50px; font-size: 20px; font-weight: bold; cursor: pointer; background: #333; color: white; border: none; border-radius: 50px; transition: 0.2s;">START</button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = {res_list_js}; // 這裡會自動填入 Python 抓到的餐廳
const colors = ["#ff4d4d", "#ffaf40", "#fffa65", "#32ff7e", "#7efff5", "#18dcff", "#7d5fff", "#ff9ff3"];
let currentAngle = 0;
let isSpinning = false;

function drawWheel() {{
    const arc = (2 * Math.PI) / options.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    options.forEach((opt, i) => {{
        const angle = currentAngle + i * arc;
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.moveTo(175, 175);
        ctx.arc(175, 175, 170, angle, angle + arc);
        ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.5)";
        ctx.stroke();
        
        ctx.save();
        ctx.translate(175, 175);
        ctx.rotate(angle + arc / 2);
        ctx.fillStyle = "#333";
        ctx.font = "bold 14px Microsoft JhengHei";
        ctx.textAlign = "right";
        ctx.fillText(opt, 155, 5);
        ctx.restore();
    }});
}}

function spin() {{
    if (isSpinning) return;
    isSpinning = true;
    let speed = Math.random() * 0.3 + 0.5;
    const friction = 0.985; 
    
    function animate() {{
        currentAngle += speed;
        speed *= friction;
        drawWheel();
        if (speed > 0.002) {{
            requestAnimationFrame(animate);
        }} else {{
            isSpinning = false;
            const totalArc = 2 * Math.PI;
            const pointerAngle = 1.5 * Math.PI;
            const normalizedAngle = (pointerAngle - (currentAngle % totalArc) + totalArc) % totalArc;
            const index = Math.floor(normalizedAngle / (totalArc / options.length));
            document.getElementById('result').innerText = "🎉 抽到了：" + options[index];
        }}
    }}
    animate();
}}
drawWheel();
</script>
"""

display(IPython.display.HTML(html_code))



# 1. 安裝必要套件
!pip install geopy -q

import IPython
from google.colab import output
from geopy.geocoders import Nominatim
import requests
import random

# --- 設定搜尋功能 ---
def get_real_restaurants(location_query, radius=10000):
    try:
        # 定位座標
        geolocator = Nominatim(user_agent="dinner_wheel_app")
        location = geolocator.geocode(location_query)
        
        if not location:
            return ["找不到地點", "請重新輸入", "麥當勞", "肯德基"]

        # Overpass API 查詢 (搜尋方圓 radius 公尺內的餐廳)
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        node["amenity"~"restaurant|fast_food|cafe"](around:{radius},{location.latitude},{location.longitude});
        out 50;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        
        # 提取店家名稱並去除重複或無名的
        places = list(set([element['tags'].get('name') for element in data['elements'] if 'name' in element['tags']]))
        
        if len(places) < 2:
            return ["附近店家不足", "手動輸入吧", "麥當勞", "巷口麵攤"]
        
        # 隨機挑選 10 間以內，避免轉盤太擠
        return random.sample(places, min(len(places), 10))
    except Exception as e:
        print(f"搜尋出錯: {e}")
        return ["搜尋失敗", "請檢查網路", "便利商店", "泡麵"]

# --- 互動部分 ---
target = input("輸入想搜尋的地點 (例如: 竹科, 板橋車站): ")
print(f"正在搜尋 {target} 附近 10km 的餐廳...")
restaurants = get_real_restaurants(target)
res_list_js = str(restaurants)

# --- HTML/JS 轉盤介面 ---
html_code = f"""
<div style="text-align:center; font-family: 'Microsoft JhengHei', sans-serif; background: #ffffff; padding: 20px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); max-width: 500px; margin: auto;">
    <div style="margin-bottom: 10px;">
        <span style="background: #e1f5fe; color: #0288d1; padding: 5px 12px; border-radius: 20px; font-size: 14px; font-weight: bold;">
            📍 {target} 附近 10km 直選
        </span>
    </div>
    <h2 id="result" style="color: #333; margin: 15px 0;">準備好決定了嗎？</h2>
    
    <div style="position: relative; display: inline-block; width: 380px; height: 380px;">
        <canvas id="wheel" width="380" height="380"></canvas>
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 50px; height: 50px; background: white; border-radius: 50%; z-index: 5; border: 5px solid #333; box-shadow: 0 0 10px rgba(0,0,0,0.2);"></div>
        <div id="pointer" style="position: absolute; top: -15px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 18px solid transparent; border-right: 18px solid transparent; border-top: 35px solid #ff4757; z-index: 10; filter: drop-shadow(0px 3px 2px rgba(0,0,0,0.2));"></div>
    </div>
    
    <br><br>
    <button onclick="spin()" style="padding: 18px 60px; font-size: 24px; font-weight: 1000; cursor: pointer; background: #333; color: white; border: none; border-radius: 15px; letter-spacing: 2px; box-shadow: 0 5px 0 #000; transition: 0.1s;" onmousedown="this.style.transform='translateY(4px)'; this.style.boxShadow='none'" onmouseup="this.style.transform='translateY(0px)'; this.style.boxShadow='0 5px 0 #000'">
        SPIN!
    </button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = {res_list_js};
const colors = ["#ff5e57", "#ffdd59", "#ffc048", "#0be881", "#05c46b", "#00d8d6", "#0fbcf9", "#575fcf", "#ef5777", "#f53b57"];
let currentAngle = 0;
let isSpinning = false;

function drawWheel() {{
    const arc = (2 * Math.PI) / options.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    options.forEach((opt, i) => {{
        const angle = currentAngle + i * arc;
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.moveTo(190, 190);
        ctx.arc(190, 190, 185, angle, angle + arc);
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.save();
        ctx.translate(190, 190);
        ctx.rotate(angle + arc / 2);
        ctx.fillStyle = "#333";
        ctx.font = "bold 15px Microsoft JhengHei";
        ctx.textAlign = "right";
        // 處理過長文字
        let displayOpt = opt.length > 8 ? opt.substring(0, 7) + ".." : opt;
        ctx.fillText(displayOpt, 170, 5);
        ctx.restore();
    }});
}}

function spin() {{
    if (isSpinning) return;
    isSpinning = true;
    let speed = Math.random() * 0.4 + 0.6;
    const friction = 0.988; 
    
    function animate() {{
        currentAngle += speed;
        speed *= friction;
        drawWheel();
        if (speed > 0.002) {{
            requestAnimationFrame(animate);
        }} else {{
            isSpinning = false;
            const totalArc = 2 * Math.PI;
            const pointerAngle = 1.5 * Math.PI;
            const normalizedAngle = (pointerAngle - (currentAngle % totalArc) + totalArc) % totalArc;
            const index = Math.floor(normalizedAngle / (totalArc / options.length));
            document.getElementById('result').innerText = "🎉 今天吃：" + options[index];
            document.getElementById('result').style.color = "#ff4757";
        }}
    }}
    animate();
}}
drawWheel();
</script>
"""

display(IPython.display.HTML(html_code))



