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

print("開始抓取資料 (已加入日期與空值防錯機制)...")

try:
    while entry:
        try:
            row = {}
            for item in entry.Items:
                name = item.Name
                try:
                    val = item.Values
                    # 關鍵修正：檢查 val 是否存在
                    if val is not None:
                        # 取出第一個元素
                        first_val = val[0] if isinstance(val, (list, tuple)) and len(val) > 0 else val
                        
                        # 處理可能的日期物件或特殊物件，統一轉為字串避免 total_seconds 錯誤
                        if first_val is None:
                            row[name] = ""
                        else:
                            row[name] = str(first_val)
                    else:
                        row[name] = ""
                except Exception:
                    # 如果讀取單個 Item 失敗，給予空值並繼續
                    row[name] = ""
            
            rows.append(row)
            count += 1
            
            # 每 100 筆顯示進度並存檔
            if count % 100 == 0:
                pd.DataFrame(rows).to_excel(output_file, index=False)
                print(f"目前進度：已成功處理 {count} 筆...")

            # 取得下一筆
            entry = view.GetNextDocument(entry)
            
        except Exception as e:
            print(f"第 {count} 筆文件結構異常，已跳過。錯誤原因: {e}")
            entry = view.GetNextDocument(entry)
            continue

except KeyboardInterrupt:
    print("\n偵測到手動中斷。")

finally:
    if rows:
        df = pd.DataFrame(rows)
        # 存檔前最後檢查：確保沒有遺漏的資料
        df.to_excel('Employee_Data_Final.xlsx', index=False)
        print(f"【任務完成】總共抓取: {len(rows)} 筆。")
        print("最終檔案：Employee_Data_Final.xlsx")
    else:
        print("未抓取到任何資料。")
