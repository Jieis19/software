from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()

    # Helper function to add a slide with title and bullet points
    def add_slide(title_text, content_list):
        slide_layout = prs.slide_layouts[1] # Title and Content layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Set Title
        title = slide.shapes.title
        title.text = title_text
        
        # Set Content
        tf = slide.placeholders[1].text_frame
        tf.clear() # Clear default empty paragraph
        
        for item in content_list:
            p = tf.add_paragraph()
            p.text = item
            p.level = 0
            p.font.size = Pt(20)
            # Check if it's a sub-point (simple heuristic: starts with space or -)
            if item.startswith("  -"):
                p.text = item.replace("  -", "")
                p.level = 1

    # Slide 1: Title Slide
    slide_layout = prs.slide_layouts[0] # Title Slide layout
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "QueueTogether 順便帶"
    subtitle.text = "讓排隊更有價值，實現最後 100 公尺的互助共享\n\n[您的名字/團隊]"

    # Slide 2: 痛點分析
    add_slide("痛點分析：為什麼我們需要這個？", [
        "時間成本高昂：熱門店排隊動輒 30-60 分鐘。",
        "資源浪費：多人分別排隊，不如一人代買。",
        "外送限制：許多名店無外送或溢價過高。",
        "資訊不透明：到了現場才發現人山人海。"
    ])

    # Slide 3: 解決方案
    add_slide("解決方案：共享排隊經濟", [
        "即時媒合：連結「排隊者 (Host)」與「需求者 (Guest)」。",
        "互助共利：Host 賺取跑腿費；Guest 節省時間。",
        "資訊同步：現場實況即時回報。",
        "核心概念：把一個人的等待，轉化為一群人的便利。"
    ])

    # Slide 4: 為什麼選擇 LINE Bot？
    add_slide("產品形式：LINE Bot + LIFF", [
        "最低門檻：無需下載 App，掃碼即用。",
        "原生社交：利用 LINE 群組信任關係，解決面交疑慮。",
        "高滲透率：台灣使用率最高的通訊軟體。",
        "即時通知：Push Message 確保訂單狀態不漏接。"
    ])

    # Slide 5: 使用情境 (User Journey)
    add_slide("使用流程演示", [
        "【Host 發起】：",
        "  - 透過 LIFF 填寫店家與等待時間。",
        "  - 系統生成 Flex Message 卡片傳至群組。",
        "【Guest 跟團】：",
        "  - 點擊卡片直接 +1 下單。",
        "  - 收到 Host「已買到」、「回程中」通知。"
    ])

    # Slide 6: 獨家功能亮點
    add_slide("功能亮點", [
        "智慧截單：設定數量上限或是倒數計時。",
        "實況看板：上傳現場照片，系統預估等待時間。",
        "面交導航：整合 Location Message 精準定位。",
        "信任評分：累積勳章 (如：準時達人)。"
    ])

    # Slide 7: 技術架構
    add_slide("技術架構 (Tech Stack)", [
        "前端：LINE Messaging API + LIFF (HTML/JS)",
        "後端：Python (Flask/FastAPI) on Render",
        "資料庫：PostgreSQL (儲存訂單與狀態)",
        "優勢：輕量開發、快速部署、成本低廉"
    ])

    # Slide 8: 商業模式
    add_slide("商業模式與展望", [
        "初期 (MVP)：累積用戶，建立互助習慣。",
        "中期：小額跑腿費機制、店家導流合作。",
        "願景：成為區域性的「超短距物流」平台。"
    ])

    # Slide 9: 結語
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "感謝聆聽"
    subtitle.text = "讓我們一起把時間花在更美好的事物上\n\n[QR Code 預留區]"

    # Save
    filename = "QueueTogether_Pitch.pptx"
    prs.save(filename)
    print(f"成功生成檔案：{filename}")

if __name__ == "__main__":
    create_presentation()
