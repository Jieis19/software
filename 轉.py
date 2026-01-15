!pip install geopy -q

import IPython
from google.colab import output
from geopy.geocoders import Nominatim
import requests
import random

# --- 1. 設定區 ---
target = input("輸入地點 (例如: 竹科): ")
try:
    num_count = int(input("想要顯示幾間餐廳? (建議 6-12): "))
except:
    num_count = 8

# --- 2. 抓取資料函數 ---
def get_real_restaurants(location_query, radius=10000, count=10):
    try:
        geolocator = Nominatim(user_agent="dinner_wheel_app")
        location = geolocator.geocode(location_query)
        if not location: return ["找不到地點"] * count

        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        node["amenity"~"restaurant|fast_food|cafe"](around:{radius},{location.latitude},{location.longitude});
        out 50;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        places = list(set([element['tags'].get('name') for element in data['elements'] if 'name' in element['tags']]))
        
        if len(places) < count:
            # 如果抓到的店不夠，用預設補齊
            places += ["麥當勞", "肯德基", "便當店", "便利商店"]
            
        return random.sample(places, count)
    except:
        return ["連線失敗"] * count

restaurants = get_real_restaurants(target, count=num_count)
res_list_js = str(restaurants)

# --- 3. HTML/JS 轉盤介面 ---
html_code = f"""
<div style="text-align:center; font-family: 'Microsoft JhengHei', sans-serif; background: #fff; padding: 20px; border-radius: 20px; max-width: 500px; margin: auto;">
    <h1 id="result" style="color: #ff4757; margin-bottom: 20px; min-height: 1.5em;">今天吃什麼？</h1>
    
    <div style="position: relative; display: inline-block; width: 380px; height: 380px;">
        <canvas id="wheel" width="380" height="380"></canvas>
        
        <div style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid #ff4757; z-index: 10; filter: drop-shadow(0px 2px 2px rgba(0,0,0,0.3));"></div>
        
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: white; border-radius: 50%; z-index: 5; border: 4px solid #333;"></div>
    </div>
    
    <br><br>
    <button onclick="spin()" id="spinBtn" style="padding: 15px 60px; font-size: 22px; font-weight: bold; cursor: pointer; background: #333; color: white; border: none; border-radius: 50px; transition: 0.2s;">
        SPIN!
    </button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = {res_list_js};
const numOptions = options.length;
const arc = (2 * Math.PI) / numOptions;
let currentAngle = 0;
let isSpinning = false;

// 繪製轉盤
function drawWheel() {{
    ctx.clearRect(0, 0, 380, 380);
    options.forEach((opt, i) => {{
        const angle = currentAngle + i * arc;
        
        // 扇形顏色 (HSL 自動分配)
        ctx.fillStyle = `hsl(${{(i * 360 / numOptions)}}, 75%, 65%)`;
        ctx.beginPath();
        ctx.moveTo(190, 190);
        ctx.arc(190, 190, 180, angle, angle + arc);
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // 文字
        ctx.save();
        ctx.translate(190, 190);
        ctx.rotate(angle + arc / 2);
        ctx.fillStyle = "#333";
        ctx.font = "bold 14px Microsoft JhengHei";
        ctx.textAlign = "right";
        let displayTitle = opt.length > 8 ? opt.substring(0, 7) + '..' : opt;
        ctx.fillText(displayTitle, 165, 5);
        ctx.restore();
    }});
}}

function spin() {{
    if (isSpinning) return;
    isSpinning = true;
    document.getElementById('result').innerText = "旋轉中...";
    document.getElementById('spinBtn').style.opacity = "0.5";

    let speed = Math.random() * 0.4 + 0.6; // 隨機初始速度
    const friction = 0.985; // 摩擦力

    function animate() {{
        currentAngle += speed;
        speed *= friction;
        drawWheel();

        if (speed > 0.002) {{
            requestAnimationFrame(animate);
        }} else {{
            isSpinning = false;
            document.getElementById('spinBtn').style.opacity = "1";
            
            // --- 重點：計算結果 ---
            // 指針在正上方 (1.5 * PI)
            const totalArc = 2 * Math.PI;
            const pointerPos = 1.5 * Math.PI;
            
            // 計算目前轉盤 0 度位置距離指針的角度差
            let normalizedAngle = (pointerPos - (currentAngle % totalArc) + totalArc) % totalArc;
            let index = Math.floor(normalizedAngle / arc);
            
            // 顯示中獎名稱
            const winner = options[index];
            document.getElementById('result').innerText = "🎉 今天吃：" + winner;
        }}
    }}
    animate();
}}

drawWheel();
</script>
"""

display(IPython.display.HTML(html_code))
