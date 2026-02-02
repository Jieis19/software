import os
import time
import pandas as pd
from win32com.client import Dispatch
import pythoncom

# 初始化連線
session = Dispatch('Notes.NotesSession')
server_name = "TWAPPN01/TAIWAN/MXIC"
db_name = "FM\\Employee.nsf"

db = session.GetDatabase(server_name, db_name)
view = db.GetView('7. 顯示')

rows = []
entry = view.GetFirstDocument
count = 0
output_file = 'Employee_Data_Backup.xlsx'

print("開始抓取資料...")

try:
    while entry:
        try:
            row = {}
            # 優化：直接迭代 Items
            for item in entry.Items:
                name = item.Name
                val = item.Values
                if val:
                    row[name] = val[0] if isinstance(val, (list, tuple)) else val
                else:
                    row[name] = None
            
            rows.append(row)
            count += 1
            
            # 每 100 筆顯示一次進度並存檔，避免中斷時全部遺失
            if count % 100 == 0:
                pd.DataFrame(rows).to_excel(output_file, index=False)
                print(f"目前進度：已處理 {count} 筆，已自動備份至 Excel...")

            # 取得下一筆
            next_entry = view.GetNextDocument(entry)
            
            # 重要：手動釋放 COM 物件避免記憶體溢位導致卡住
            entry = next_entry
            
        except Exception as e:
            print(f"處理第 {count} 筆時發生錯誤: {e}")
            entry = view.GetNextDocument(entry) # 發生錯誤跳過該筆繼續
            continue

except KeyboardInterrupt:
    print("\n使用者手動中斷程式。")

finally:
    # 最終儲存
    if rows:
        df = pd.DataFrame(rows)
        df.to_excel('Employee_Data_Final.xlsx', index=False)
        print(f"任務結束。總共抓取: {len(rows)} 筆。檔案已儲存為 Employee_Data_Final.xlsx")
    else:
        print("沒有抓取到任何資料。")





處理第 100 筆時發生錯誤: 'NoneType' object has no attribute 'total_seconds'
