    response = requests.post(url, headers=headers, params=params, data=data, proxies=proxies, verify=False)
    html_data = response.json()
    # print(html_data)
    lis = html_data["data"]["resultList"]
    file_path=r'E:/tixcraft_b/json.txt'
    with open(file_path, "w", encoding="utf-8") as file:
            json.dump(lis, file, ensure_ascii=False, indent=4)  # 美化輸出 + 保留中文
            print(f"資料已成功寫入到 {file_path}！")
    for i in lis:
        title = i["data"]["item"]["main"]["exContent"]["title"].strip()
        diqu = i["data"]["item"]["main"]["exContent"]["area"].strip()
        #picUrl
        pic=i["data"]["item"]["main"]["exContent"]["picUrl"].strip()
        try:
            naem = i["data"]["item"]["main"]["exContent"]["userNickName"].strip()
        except:
            naem = "未知(新用户未命名名字)"
        try:
            youfei = i["data"]["item"]["main"]["clickParam"]["args"]["tagname"]
        except:
            youfei = "不包郵"
        jianjei = str(youfei) + "+" * 5 + title
        id = i["data"]["item"]["main"]["exContent"]["itemId"]
        lianjei = f"https://www.goofish.com/item?spm=a21ybx.search.searchFeedList.1.570344f71nqzll&id={id}&categoryId=126854525"
        jiage = i["data"]["item"]["main"]["clickParam"]["args"]["price"]
        if float(jiage) > 1:
          # print("-" * 60)
          # print("用户名字:", naem, "\n", "简介:", jianjei, "\n", "链接:", lianjei, "\n", "价格:", jiage, "\n", "地区:", diqu)
          # print("-" * 60)

          # 将数据写入 Excel 工作表
          print(pic)
          ws.append([jianjei, lianjei, jiage, diqu,pic])


jiage_values = [
    float(row[2]) for row in ws.iter_rows(min_row=2, values_only=True) if row[2] is not None
]
print(jiage_values)

# 計算中位數
if jiage_values:
    median_jiage = statistics.median(jiage_values)
    median_jiage=median_jiage*5
    max_jiage = max(jiage_values)
    max_jiage=max_jiage*5
    print(median_jiage)
    if median_jiage<1000:
        print(f"'jiage' 列的中位數: {median_jiage*2+90}")
        print(f"'jiage' 列的high數: {max_jiage*2+90}")
    else :
        print(f"'jiage' 列的中位數: {median_jiage*1.5+90}")
        print(f"'jiage' 列的high數: {max_jiage*1.5+90}")
else:
    print("無法計算中位數：'jiage' 列無資料。")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


import statistics

data_list = []  # 存放 [價格, pic]

for i in lis:
    title = i["data"]["item"]["main"]["exContent"]["title"].strip()
    diqu = i["data"]["item"]["main"]["exContent"]["area"].strip()
    pic = i["data"]["item"]["main"]["exContent"]["picUrl"].strip()
    try:
        naem = i["data"]["item"]["main"]["exContent"]["userNickName"].strip()
    except:
        naem = "未知(新用户未命名名字)"
    try:
        youfei = i["data"]["item"]["main"]["clickParam"]["args"]["tagname"]
    except:
        youfei = "不包郵"
    jianjei = str(youfei) + "+" * 5 + title
    id = i["data"]["item"]["main"]["exContent"]["itemId"]
    lianjei = f"https://www.goofish.com/item?spm=a21ybx.search.searchFeedList.1.570344f71nqzll&id={id}&categoryId=126854525"
    jiage = i["data"]["item"]["main"]["clickParam"]["args"]["price"]

    if float(jiage) > 1:
        ws.append([jianjei, lianjei, jiage, diqu, pic])
        data_list.append((float(jiage), pic, title))  # 存價格和 pic

# 取出價格
jiage_values = [x[0] for x in data_list]

if jiage_values:
    median_jiage = statistics.median(jiage_values)
    median_jiage *= 5
    max_jiage = max(jiage_values) * 5

    # 找到最接近中位數的商品
    median_item = min(data_list, key=lambda x: abs(x[0]*5 - median_jiage))
    max_item = max(data_list, key=lambda x: x[0])

    print(f"中位數: {median_jiage}")
    print(f"對應商品: {median_item[2]} (pic: {median_item[1]})")

    if median_jiage < 1000:
        print(f"'jiage' 列的中位數: {median_jiage*2+90}")
        print(f"'jiage' 列的high數: {max_jiage*2+90} (pic: {max_item[1]})")
    else:
        print(f"'jiage' 列的中位數: {median_jiage*1.5+90}")
        print(f"'jiage' 列的high數: {max_jiage*1.5+90} (pic: {max_item[1]})")
else:
    print("無法計算中位數：'jiage' 列無資料。")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage

line_bot_api = LineBotApi("你的 Channel Access Token")

# 假設這裡已經算好中位數與對應商品
median_jiage = 120.0
median_item = {
    "title": "XX商品",
    "pic": "https://example.com/image.jpg",
    "link": "https://www.goofish.com/item?id=123456"
}

# 要回覆的內容
messages = [
    TextSendMessage(
        text=f"📊 中位數價格: {median_jiage}\n商品: {median_item['title']}\n連結: {median_item['link']}"
    ),
    ImageSendMessage(
        original_content_url=median_item["pic"],   # 圖片原始網址 (必須是 HTTPS)
        preview_image_url=median_item["pic"]       # 縮圖網址 (可同原圖)
    )
]

# 推送給某個 user_id
line_bot_api.push_message("使用者的 userId", messages)