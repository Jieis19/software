import requests
from bs4 import BeautifulSoup
import json, warnings

# 忽略 SSL/HTTPS 警告
warnings.filterwarnings('ignore')

# 目標 URL
base_url = "https://www.hc.mmh.org.tw/child/"
department_url = f"{base_url}department.php"

headers = {
    'Cookie': 'PHPSESSID=v38seoisac8bdv17bj1k8iajnb'
}

proxies = {
    'https': '172.17.22.161:8080'  # 可選，如無可刪掉
}

# Step1: 取得科別頁面的 href
response = requests.get(department_url, headers=headers, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')
ul_element = soup.find('ul', class_='department-list clr')
hrefs = [a['href'] for a in ul_element.find_all('a', href=True)]

# Step2: 逐科別抓醫生
doctor_list = []
partment_list = []

for list_ in hrefs[1:]:
    if 'php?id' in list_ and '184' not in list_:
        url = f"{base_url}{list_}"
        response = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 取得科別名稱
        h2_tag = soup.find('h6')
        if not h2_tag:
            continue
        dept_name = h2_tag.get_text(strip=True)

        # 取得醫生名字
        h3_links = soup.find_all('h3')
        for h3 in h3_links:
            a_tag = h3.find('a')
            if a_tag:
                doc_name = a_tag.get_text(strip=True)
                doctor_list.append(doc_name)
                partment_list.append(dept_name)

# Step3: 生成 JSON 結構
hospital_id = 'h001'
hospital_name = '新竹馬偕兒童醫院'
city_name = '新竹市'

# 整理科別與醫生
clinic_dict = {}
doctor_counter = 1
for dept, doc in zip(partment_list, doctor_list):
    if dept not in clinic_dict:
        clinic_dict[dept] = []
    clinic_dict[dept].append({'id': f'd{doctor_counter:03}', 'name': doc})
    doctor_counter += 1

clinics_list = []
for cid, (dept, docs) in enumerate(clinic_dict.items(), start=1):
    clinics_list.append({
        'id': f'c{cid:03}',
        'name': dept,
        'doctors': docs
    })

hospital_json = {
    'id': hospital_id,
    'name': hospital_name,
    'city': city_name,
    'clinics': clinics_list
}

# Step4: 寫入 hospitals.json
with open('hospitals.json', 'w', encoding='utf-8') as f:
    json.dump([hospital_json], f, ensure_ascii=False, indent=2)

print("✅ hospitals.json 已生成完成！")