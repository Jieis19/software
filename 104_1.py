import time
import random
import requests
import pandas as pd
from datetime import datetime
import os
import threading
from flask import Flask
import logging
import urllib3

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

app = Flask(__name__)

# --- 配置區 ---
TOKEN = os.environ.get("TG_TOKEN", "你的TOKEN")
# 你的原始 ID，作為保底，避免 Render 重啟後清單消失
ADMIN_CHAT_ID = os.environ.get("TG_CHAT_ID", "你的ID")
HISTORY_FILE = "/tmp/sent_jobs_history.csv" 
USERS_FILE = "/tmp/subscribers.csv" # 記錄所有點擊 start 的使用者

# --- Web 伺服器設定 (防止 Render 休眠) ---
@app.route('/')
def health_check():
    return f"Bot is running. Active users: {len(get_all_users())}. Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 200

# --- 使用者管理邏輯 ---
def get_all_users():
    """取得所有訂閱者 ID"""
    users = {ADMIN_CHAT_ID} # 使用 set 避免重複，並加入保底 ID
    if os.path.exists(USERS_FILE):
        try:
            df = pd.read_csv(USERS_FILE)
            file_users = df['chat_id'].astype(str).tolist()
            users.update(file_users)
        except:
            pass
    return list(users)

def save_new_user(chat_id):
    """存入新使用者"""
    chat_id = str(chat_id)
    users = get_all_users()
    if chat_id not in users:
        df = pd.DataFrame({'chat_id': [chat_id]})
        header = not os.path.exists(USERS_FILE)
        df.to_csv(USERS_FILE, mode='a', index=False, header=header)
        logging.info(f"新使用者訂閱: {chat_id}")
        return True
    return False

def check_for_updates():
    """輪詢 Telegram API 檢查是否有新使用者傳送 /start"""
    last_update_id = 0
    logging.info("使用者監測執行緒啟動...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            r = requests.get(url, timeout=35).json()
            if r.get("result"):
                for update in r["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        chat_id = str(msg["chat"]["id"])
                        text = msg["text"]
                        
                        if text == "/start":
                            if save_new_user(chat_id):
                                welcome_text = "🎉 歡迎使用 104 職缺追蹤機器人！當有符合 Python 的新職缺時，我會立即通知您。"
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                              data={"chat_id": chat_id, "text": welcome_text})
        except Exception as e:
            logging.error(f"監測更新失敗: {e}")
        time.sleep(5)

# --- 職缺發送邏輯 ---
def send_tg_broadcast(text):
    """將訊息發送給所有訂閱者"""
    users = get_all_users()
    for user_id in users:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": user_id, "text": text, "parse_mode": "HTML"}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            logging.error(f"發送給 {user_id} 失敗: {e}")
    time.sleep(1) # 廣播完畢小休

# --- 104 爬蟲類別 ---
class Job104Spider():
    def search(self, keyword, max_mun=10, filter_params=None, sort_type='符合度', is_sort_asc=False):
        jobs = []
        total_count = 0
        url = 'https://www.104.com.tw/jobs/search/list'
        query = f'ro=0&kwop=7&keyword={keyword}&expansionType=area,spec,com,job,wf,wktm&mode=s&jobsource=2018indexpoc'
        if filter_params:
            query += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/',
        }
        sort_dict = {'符合度': '1', '日期': '2', '經歷': '3', '學歷': '4', '應徵人數': '7', '待遇': '13'}
        sort_params = f"&order={sort_dict.get(sort_type, '1')}" + ('&asc=1' if is_sort_asc else '&asc=0')
        query += sort_params

        page = 1
        while len(jobs) < max_mun:
            params = f'{query}&page={page}'
            r = requests.get(url, params=params, headers=headers)
            if r.status_code != requests.codes.ok:
                break
            data = r.json()
            total_count = data['data']['totalCount']
            jobs.extend(data['data']['list'])
            if (page == data['data']['totalPage']) or (data['data']['totalPage'] == 0):
                break
            page += 1
            time.sleep(random.uniform(3, 5))
        return total_count, jobs[:max_mun]

    def search_job_transform(self, job_data):
        job_url = f"https:{job_data['link']['job']}"
        job_id = job_url.split('/job/')[-1].split('?')[0]
        return {
            'job_id': job_id,
            'name': job_data['jobName'],
            'appear_date': job_data['appearDate'],
            'company_name': job_data['custName'],
            'company_addr': f"{job_data['jobAddrNoDesc']} {job_data['jobAddress']}",
            'job_url': job_url,
            'education': job_data['optionEdu'],
            'period': job_data['periodDesc'],
            'salary': job_data['salaryDesc'],
        }

# --- 爬蟲主迴圈 ---
def run_spider_loop():
    logging.info("爬蟲執行緒啟動...")
    while True:
        try:
            logging.info("開始掃描 104 職缺...")
            spider = Job104Spider()
            filter_params = {'newZone': '1'}
            _, raw_jobs = spider.search('python', max_mun=50, filter_params=filter_params)
            jobs = [spider.search_job_transform(j) for j in raw_jobs]
            
            sent_job_ids = set()
            if os.path.exists(HISTORY_FILE):
                df_h = pd.read_csv(HISTORY_FILE)
                sent_job_ids = set(df_h['job_id'].astype(str).tolist())

            df_all = pd.DataFrame(jobs)
            today_str = datetime.now().strftime('%Y%m%d')
            new_jobs = df_all[(df_all['appear_date'] == today_str) & (~df_all['job_id'].astype(str).isin(sent_job_ids))]

            if not new_jobs.empty:
                for _, row in new_jobs.iterrows():
                    msg = f"🔹 <b>{row['name']}</b>\n🏢 公司：{row['company_name']}\n💰 待遇：{row['salary']}\n🎓 學歷：{row['education']} / {row['period']}\n📍 地點：{row['company_addr']}\n🔗 <a href='{row['job_url']}'>查看詳情</a>"
                    send_tg_broadcast(msg)
                    time.sleep(1)

                new_ids_df = pd.DataFrame({'job_id': new_jobs['job_id'].astype(str)})
                new_ids_df.to_csv(HISTORY_FILE, mode='a', header=not os.path.exists(HISTORY_FILE), index=False)
            
            logging.info(f"掃描結束。新增: {len(new_jobs)} 筆。")
        except Exception as e:
            logging.error(f"爬蟲迴圈出錯: {e}")
        
        time.sleep(1200) # 20分鐘抓一次

if __name__ == "__main__":
    # 啟動爬蟲執行緒
    threading.Thread(target=run_spider_loop, daemon=True).start()
    # 啟動使用者監測執行緒
    threading.Thread(target=check_for_updates, daemon=True).start()
    
    # 啟動 Web 服務
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
