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
