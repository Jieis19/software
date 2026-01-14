import time
import random
import requests
import pandas as pd
from datetime import datetime
import os
class Job104Spider():
    def search(self, keyword, max_mun=10, filter_params=None, sort_type='符合度', is_sort_asc=False):
        """搜尋職缺"""
        jobs = []
        total_count = 0

        url = 'https://www.104.com.tw/jobs/search/list'
        query = f'ro=0&kwop=7&keyword={keyword}&expansionType=area,spec,com,job,wf,wktm&mode=s&jobsource=2018indexpoc'
        if filter_params:
            # 加上篩選參數，要先轉換為 URL 參數字串格式
            query += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/',
        }

        # 加上排序條件
        sort_dict = {
            '符合度': '1',
            '日期': '2',
            '經歷': '3',
            '學歷': '4',
            '應徵人數': '7',
            '待遇': '13',
        }
        sort_params = f"&order={sort_dict.get(sort_type, '1')}"
        sort_params += '&asc=1' if is_sort_asc else '&asc=0'
        query += sort_params

        page = 1
        while len(jobs) < max_mun:
            params = f'{query}&page={page}'
            r = requests.get(url, params=params, headers=headers)
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                data = r.json()
                print(data['status'], data['statusMsg'], data['errorMsg'])
                break

            data = r.json()
            total_count = data['data']['totalCount']
            jobs.extend(data['data']['list'])

            if (page == data['data']['totalPage']) or (data['data']['totalPage'] == 0):
                break
            page += 1
            time.sleep(random.uniform(3, 5))

        return total_count, jobs[:max_mun]

    def get_job(self, job_id):
        """取得職缺詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'Referer': f'https://www.104.com.tw/job/{job_id}'
        }

        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print('請求失敗', r.status_code)
            return

        data = r.json()
        return data['data']

    def search_job_transform(self, job_data):
        """將職缺資料轉換格式、補齊資料"""
        appear_date = job_data['appearDate']
        apply_num = int(job_data['applyCnt'])
        company_addr = f"{job_data['jobAddrNoDesc']} {job_data['jobAddress']}"

        job_url = f"https:{job_data['link']['job']}"
        job_company_url = f"https:{job_data['link']['cust']}"
        job_analyze_url = f"https:{job_data['link']['applyAnalyze']}"

        job_id = job_url.split('/job/')[-1]
        if '?' in job_id:
            job_id = job_id.split('?')[0]

        salary_high = int(job_data['salaryLow'])
        salary_low = int(job_data['salaryHigh'])

        job = {
            'job_id': job_id,
            'type': job_data['jobType'],
            'name': job_data['jobName'],  # 職缺名稱
            # 'desc': job_data['descSnippet'],  # 描述
            'appear_date': appear_date,  # 更新日期
            'apply_num': apply_num,
            'apply_text': job_data['applyDesc'],  # 應徵人數描述
            'company_name': job_data['custName'],  # 公司名稱
            'company_addr': company_addr,  # 工作地址
            'job_url': job_url,  # 職缺網頁
            'job_analyze_url': job_analyze_url,  # 應徵分析網頁
            'job_company_url': job_company_url,  # 公司介紹網頁
            'lon': job_data['lon'],  # 經度
            'lat': job_data['lat'],  # 緯度
            'education': job_data['optionEdu'],  # 學歷
            'period': job_data['periodDesc'],  # 經驗年份
            'salary': job_data['salaryDesc'],  # 薪資描述
            'salary_high': salary_high,  # 薪資最高
            'salary_low': salary_low,  # 薪資最低
            'tags': job_data['tags'],  # 標籤
        }
        return job


# --- 配置區 ---
TOKEN = "8528605252:AAFKh8Z_6cXKSylfDnnDWwF57KFQfe0qbbk"
CHAT_ID = "803300061"
HISTORY_FILE = "sent_jobs_history.xlsx"  # 記錄已發送過的職位
def send_tg_message(text):
    """傳送 HTML 格式的訊息到 Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    return requests.post(url, data=payload)


if __name__ == "__main__":
  while True:
    job104_spider = Job104Spider()

    filter_params = {
        # 'area': '6001001000,6001016000',  # (地區) 台北市,高雄市
        # 's9': '1,2,4,8',  # (上班時段) 日班,夜班,大夜班,假日班
        # 's5': '0',  # 0:不需輪班 256:輪班
        # 'wktm': '1',  # (休假制度) 週休二日
        # 'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        # 'jobexp': '1,3,5,10,99',  # (經歷要求) 1年以下,1-3年,3-5年,5-10年,10年以上
        'newZone': '1',  # (科技園區) 竹科,中科,南科,內湖,南港
        # 'newZone': '1,2,3,4,5',  # (科技園區) 竹科,中科,南科,內湖,南港
        # 'zone': '16',  # (公司類型) 16:上市上櫃 5:外商一般 4:外商資訊
        # 'wf': '1,2,3,4,5,6,7,8,9,10',  # (福利制度) 年終獎金,三節獎金,員工旅遊,分紅配股,設施福利,休假福利,津貼/補助,彈性上下班,健康檢查,團體保險
        # 'edu': '1,2,3,4,5,6',  # (學歷要求) 高中職以下,高中職,專科,大學,碩士,博士
        # 'remoteWork': '1',  # (上班型態) 1:完全遠端 2:部分遠端
        # 'excludeJobKeyword': '科技',  # 排除關鍵字
        # 'kwop': '1',  # 只搜尋職務名稱
    }
    total_count, sent_job_ids = job104_spider.search('python', max_mun=3000, filter_params=filter_params)
    jobs = [job104_spider.search_job_transform(job) for job in sent_job_ids]
    print('搜尋結果職缺總數：', total_count)
    # 1. 讀取歷史紀錄 (中斷後繼續執行的關鍵)
    if os.path.exists(HISTORY_FILE):
        df_history = pd.read_excel(HISTORY_FILE)
        # 轉成 set 提高比對速度，確保 job_id 是字串
        sent_job_ids = set(df_history['job_id'].astype(str).tolist())
        print(f"載入歷史紀錄：目前已發送過 {len(sent_job_ids)} 個職位")
    else:
        df_history = pd.DataFrame()
        sent_job_ids = set()
        print("未發現歷史紀錄，將建立新檔案")

    # 2. 轉成 DataFrame 並篩選「今天」且「未傳送過」的職缺
    df_all = pd.DataFrame(jobs)
    today_str = datetime.now().strftime('%Y%m%d')

    # 過濾條件：日期是今天 且 job_id 不在已傳送清單中
    today_new_jobs = df_all[
        (df_all['appear_date'] == today_str) & 
        (~df_all['job_id'].astype(str).isin(sent_job_ids))
    ]

    # 3. 格式化訊息並發送
    if not today_new_jobs.empty:
        msg = f"<b>?? 今日新職缺快報 ({today_str})</b>\n"
        msg += f"找到 {len(today_new_jobs)} 筆新更新：\n"
        msg += "—" * 10 + "\n\n"

        for _, row in today_new_jobs.iterrows():
            job_item = (
                f"?? <b>{row['name']}</b>\n"
                f"?? 公司：{row['company_name']}\n"
                f"?? 待遇：{row['salary']}\n"
                f"?? 學歷：{row['education']} / {row['period']}\n"
                f"?? 地點：{row['company_addr']}\n"
                f"?? <a href='{row['job_url']}'>點我查看職缺詳情</a>\n\n"
            )
            msg += job_item

        # 傳送訊息
        send_tg_message(msg)
        print(f"已發送 {len(today_new_jobs)} 筆新職缺至 Telegram！")

        # 4. 更新歷史紀錄檔案
        # 將這次新發送的職缺合併到舊紀錄中
        df_updated_history = pd.concat([df_history, today_new_jobs], ignore_index=True)
        # 移除重複項（保險起見）
        df_updated_history.drop_duplicates(subset=['job_id'], keep='first', inplace=True)
        # 存回 Excel
        df_updated_history.to_excel(HISTORY_FILE, index=False)
        print(f"歷史紀錄已更新至 {HISTORY_FILE}")

    else:
        print(f"?? {today_str} 沒有新的未傳送職缺。")






import os
import time
import threading
import pandas as pd
from flask import Flask, request

# --- 配置 ---
TOKEN = os.environ.get("TG_TOKEN")
USERS_FILE = "subscribers.csv"  # 記錄所有使用者的 ID

# 儲存使用者的函式
def save_user(chat_id):
    chat_id = str(chat_id)
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        if chat_id not in df['chat_id'].astype(str).values:
            new_df = pd.concat([df, pd.DataFrame({'chat_id': [chat_id]})])
            new_df.to_csv(USERS_FILE, index=False)
    else:
        pd.DataFrame({'chat_id': [chat_id]}).to_csv(USERS_FILE, index=False)

# 取得所有使用者
def get_all_users():
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        return df['chat_id'].astype(str).tolist()
    return [] # 如果沒檔案，回傳空清單（或填入你自己的 ID 當預設）

# --- 修改後的發送函式 ---
def broadcast_jobs(msg_text):
    users = get_all_users()
    if not users:
        print("目前沒有訂閱者。")
        return
    
    for chat_id in users:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": msg_text, "parse_mode": "HTML"}
        try:
            requests.post(url, data=payload)
            time.sleep(0.05) # 稍微延遲避免被 TG 判定為垃圾訊息
        except Exception as e:
            print(f"發送給 {chat_id} 失敗: {e}")

# --- 自動接收 /start 指令 ---
# 你需要設定 Webhook 或使用 GetUpdates 輪詢
def check_for_new_users():
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}"
            res = requests.get(url).json()
            if res.get("result"):
                for update in res["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "/start" in update["message"].get("text", ""):
                        chat_id = update["message"]["chat"]["id"]
                        save_user(chat_id)
                        # 回傳歡迎訊息
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                      data={"chat_id": chat_id, "text": "訂閱成功！有新職缺我會通知你。"})
        except:
            pass
        time.sleep(5)


