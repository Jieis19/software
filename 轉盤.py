!pip install pygame

import pygame
import random
import math

# --- 1. 初始化與設定 ---
pygame.init()
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("晚餐轉盤")
clock = pygame.time.Clock()

# 顏色定義
COLORS = [
    (255, 100, 100), (255, 150, 50), (255, 255, 100), 
    (100, 255, 100), (100, 100, 255), (150, 50, 250)
]

# 轉盤選項 (對應圖片中的地點)
OPTIONS = ["中正西路", "南寮", "新豐", "夜市", "湳雅", "其他"]
num_options = len(OPTIONS)
angle_per_option = 360 / num_options

# 字體設定 (請確保電腦有支援中文字體，例如微軟正黑體)
try:
    font = pygame.font.SysFont("microsoftjhenghei", 24, bold=True)
    title_font = pygame.font.SysFont("microsoftjhenghei", 36, bold=True)
except:
    font = pygame.font.SysFont("arial", 24)

# --- 2. 轉盤邏輯變數 ---
current_angle = 0
speed = 0
is_spinning = False

def draw_wheel(surface, center, radius, rotation):
    for i in range(num_options):
        # 計算每個扇形的起始與結束角度
        start_angle = rotation + (i * angle_per_option)
        end_angle = rotation + ((i + 1) * angle_per_option)
        
        # 畫扇形
        points = [center]
        for a in range(int(start_angle), int(end_angle) + 2):
            rad = math.radians(a)
            x = center[0] + radius * math.cos(rad)
            y = center[1] + radius * math.sin(rad)
            points.append((x, y))
        
        pygame.draw.polygon(surface, COLORS[i % len(COLORS)], points)
        pygame.draw.polygon(surface, (50, 50, 50), points, 2) # 邊框

        # 繪製文字
        text_angle = math.radians(start_angle + angle_per_option / 2)
        text_x = center[0] + (radius * 0.7) * math.cos(text_angle)
        text_y = center[1] + (radius * 0.7) * math.sin(text_angle)
        
        text_surface = font.render(OPTIONS[i], True, (0, 0, 0))
        # 旋轉文字使其放射狀排列
        text_surface = pygame.transform.rotate(text_surface, -math.degrees(text_angle))
        text_rect = text_surface.get_rect(center=(text_x, text_y))
        surface.blit(text_surface, text_rect)

# --- 3. 主迴圈 ---
running = True
result_text = "按下 [空白鍵] 開始決定晚餐"

while running:
    screen.fill((255, 255, 255))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_spinning:
                speed = random.uniform(15, 25) # 隨機初始速度
                is_spinning = True
                result_text = "旋轉中..."

    # 旋轉物理邏輯
    if is_spinning:
        current_angle += speed
        speed *= 0.98  # 模擬摩擦力減速
        
        if speed < 0.1:
            speed = 0
            is_spinning = False
            # 計算指針指向哪裡 (假設指針在右側 0 度位置)
            # 因為轉盤是順時針轉，角度要倒過來算
            normalized_angle = (360 - (current_angle % 360)) % 360
            winner_idx = int(normalized_angle // angle_per_option)
            result_text = f"今晚就吃：{OPTIONS[winner_idx]}！"

    # 繪製轉盤
    wheel_center = (WIDTH // 2, HEIGHT // 2)
    draw_wheel(screen, wheel_center, 250, current_angle)
    
    # 畫出指針 (右側固定三角形)
    pygame.draw.polygon(screen, (255, 0, 0), [(WIDTH-20, HEIGHT//2), (WIDTH-60, HEIGHT//2-20), (WIDTH-60, HEIGHT//2+20)])
    
    # 顯示結果文字
    res_surf = title_font.render(result_text, True, (50, 50, 50))
    screen.blit(res_surf, (WIDTH // 2 - res_surf.get_width() // 2, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()





import IPython
from google.colab import output

# 使用 HTML5 Canvas 製作轉盤
html_code = """
<div style="text-align:center; font-family: sans-serif;">
    <h2 id="result">今晚吃什麼？</h2>
    <canvas id="wheel" width="400" height="400"></canvas><br>
    <button onclick="spin()" style="padding:10px 20px; font-size:18px; cursor:pointer; background:#ff4757; color:white; border:none; border-radius:5px;">點我旋轉</button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = ["中正西路", "南寮", "新豐", "夜市", "湳雅", "其他"];
const colors = ["#ff4757", "#ffa502", "#eccc68", "#2ed573", "#1e90ff", "#a29bfe"];
let currentAngle = 0;

function drawWheel() {
    const arc = Math.PI / (options.length / 2);
    options.forEach((opt, i) => {
        const angle = currentAngle + i * arc;
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.moveTo(200, 200);
        ctx.arc(200, 200, 180, angle, angle + arc);
        ctx.fill();
        ctx.stroke();
        
        // 畫文字
        ctx.save();
        ctx.translate(200 + Math.cos(angle + arc/2) * 120, 200 + Math.sin(angle + arc/2) * 120);
        ctx.rotate(angle + arc/2 + Math.PI/2);
        ctx.fillStyle = "black";
        ctx.fillText(opt, -ctx.measureText(opt).width/2, 0);
        ctx.restore();
    });
}

function spin() {
    let speed = Math.random() * 0.4 + 0.4;
    let friction = 0.98;
    function animate() {
        currentAngle += speed;
        speed *= friction;
        drawWheel();
        if (speed > 0.001) {
            requestAnimationFrame(animate);
        } else {
            // 計算結果
            const degrees = (currentAngle * 180 / Math.PI) % 360;
            const index = Math.floor((360 - degrees) % 360 / (360 / options.length));
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

# 使用 HTML5 Canvas 製作轉盤 + 增加指針
html_code = """
<div style="text-align:center; font-family: 'Microsoft JhengHei', sans-serif; background-color: #f7f7f7; padding: 20px; border-radius: 15px;">
    <h2 id="result" style="color: #333;">👇 點擊按鈕決定晚餐 👇</h2>
    <div style="position: relative; display: inline-block;">
        <canvas id="wheel" width="400" height="400" style="filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.1));"></canvas>
        
        <div id="pointer" style="
            position: absolute;
            right: -10px;
            top: 50%;
            transform: translateY(-50%);
            width: 0; 
            height: 0; 
            border-top: 20px solid transparent;
            border-bottom: 20px solid transparent;
            border-right: 40px solid #ff4757;
            filter: drop-shadow(-2px 2px 2px rgba(0,0,0,0.2));
            z-index: 10;
        "></div>
    </div>
    <br><br>
    <button onclick="spin()" style="
        padding: 12px 30px; 
        font-size: 20px; 
        font-weight: bold;
        cursor: pointer; 
        background: linear-gradient(135deg, #ff4757, #ff6b81); 
        color: white; 
        border: none; 
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
        transition: 0.2s;
    " onmousedown="this.style.transform='scale(0.95)'" onmouseup="this.style.transform='scale(1)'">
        SPIN! 旋轉
    </button>
</div>

<script>
const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const options = ["中正西路", "南寮", "新豐", "夜市", "湳雅", "竹北"];
const colors = ["#ff4757", "#ffa502", "#eccc68", "#7bed9f", "#70a1ff", "#a29bfe"];
let currentAngle = 0;
let isSpinning = false;

function drawWheel() {
    const arc = (2 * Math.PI) / options.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    options.forEach((opt, i) => {
        const angle = currentAngle + i * arc;
        
        // 繪製扇區
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.moveTo(200, 200);
        ctx.arc(200, 200, 190, angle, angle + arc);
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // 繪製文字
        ctx.save();
        ctx.translate(200, 200);
        ctx.rotate(angle + arc / 2);
        ctx.fillStyle = "white";
        ctx.font = "bold 18px Microsoft JhengHei";
        ctx.shadowColor = "rgba(0,0,0,0.2)";
        ctx.shadowBlur = 4;
        ctx.fillText(opt, 80, 10); // 文字距離中心的距離
        ctx.restore();
    });

    // 繪製中心圓鈕
    ctx.beginPath();
    ctx.arc(200, 200, 30, 0, 2 * Math.PI);
    ctx.fillStyle = "white";
    ctx.fill();
    ctx.strokeStyle = "#ddd";
    ctx.stroke();
}

function spin() {
    if (isSpinning) return;
    isSpinning = true;
    
    let speed = Math.random() * 0.5 + 0.5; // 隨機初始速度
    const friction = 0.985; // 摩擦力
    
    function animate() {
        currentAngle += speed;
        speed *= friction;
        drawWheel();
        
        if (speed > 0.002) {
            requestAnimationFrame(animate);
        } else {
            isSpinning = false;
            // 計算結果：指針在右側 (0 弧度)，所以要找哪個扇區落在 0 弧度位置
            // 轉盤公式：(2*PI - (總旋轉角度 % 2*PI))
            const totalArc = 2 * Math.PI;
            const normalizedAngle = (totalArc - (currentAngle % totalArc)) % totalArc;
            const index = Math.floor(normalizedAngle / (totalArc / options.length));
            document.getElementById('result').innerText = "🎉 今晚就吃：" + options[index] + "！";
        }
    }
    animate();
}

drawWheel();
</script>

