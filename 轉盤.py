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
