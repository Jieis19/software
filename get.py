import requests,re,warnings
from bs4 import BeautifulSoup

# 禁用所有類型的警告
warnings.filterwarnings('ignore')

# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child# mmh/child
url = "https://www.hc.mmh.org.tw/child/department.php"

payload = {}
headers = {
  'Cookie': 'PHPSESSID=v38seoisac8bdv17bj1k8iajnb'
}

response = requests.request("GET", url, headers=headers, data=payload, timeout=100)
html_content=response.text
# 正則表達式來匹配 href 的值
# 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 找到特定的 ul
ul_element = soup.find('ul', class_='department-list clr')  # 根據 class 找到 ul

# 從 ul 中抓取所有的 <a> 標籤並提取 href 屬性
hrefs = [a['href'] for a in ul_element.find_all('a', href=True)]

# 印出所有 href
# print(hrefs)




i=0
doctor=[]
partment=[]
for list_ in hrefs[1:]:
    if 'php?id' in list_ and '184' not in list_:
        # print(list_)
        url=f'https://www.hc.mmh.org.tw/child/{list_}'
        # https://www.hc.mmh.org.tw/child/departmain.php?id=14
        # print(url)
        payload = {}
        headers = {
          'Cookie': 'PHPSESSID=v38seoisac8bdv17bj1k8iajnb'
        }
        proxies={
        'https': '172.17.22.161:8080'
            }
        response = requests.request("GET", url, headers=headers, proxies=proxies, verify=False, data=payload, timeout=100)
        html_content=response.text
        # 正則表達式來匹配 href 的值
        # 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 抓取 5520（h2 的內容，忽略註解和 span）
        title_h2 = soup.find('h6')
        
        
        
        title_h2 = soup.find('h6').get_text(strip=True)  # 去除多餘空格
        
        
        # 抓取所有的 <h3> 裡的文字與 href 屬性
        h3_links = soup.find_all('h3')  # 找到所有 h3 標籤
        
        results = []
        for h3 in h3_links:
            link_tag = h3.find('a')  # 找到 h3 裡面的 <a>
            # print('link_tag',link_tag)
            if (link_tag):
                text = link_tag.get_text(strip=True)  # 抓取文字
                href = link_tag['href']  # 抓取 href 屬性
                results.append({'text': text, 'href': href})
        
        # 輸出結果
        
        
        # { id: 'c-001', name: '內科' },
        
        # print("Title from H2:", title_h2)
        # print("Links and Texts from H3:")
        if title_h2 not in partment:
            for result in results:
                i+=1
                doctor.append(result['text'])
                partment.append(title_h2)
                # print("{"+f"id: 'c-00{i}',name: '{title_h2}-{result['text']}'"+"},")
                
               
                
 科別:title_h2     ,  醫生:result['text']       
                
                
                
                
                
                
                
                
                
                
                
