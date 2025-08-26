import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 從 GitHub Secrets 讀取服務帳號金鑰
# 我們將整個 JSON 內容作為一個字串傳入環境變數
key_file_content = os.getenv('GCP_SA_KEY')
if not key_file_content:
    raise ValueError("GCP_SA_KEY environment variable not set.")

# 將字串轉換回 JSON 物件
sa_credentials_json = json.loads(key_file_content)

# --- 您需要修改的變數 ---
# 1. 從您的 Google 文件網址中取得文件 ID
#    例如：https://docs.google.com/document/d/THIS_IS_THE_ID/edit
DOCUMENT_ID = 'YOUR_DOCUMENT_ID_HERE' 
# 2. 您想要新增的文字
TEXT_TO_ADD = "這是由 GitHub Action 自動新增的文字！\n"
# --- 修改結束 ---

# 設定 API 範圍
SCOPES = ['https://www.googleapis.com/auth/documents']

def main():
    """主執行函式：認證並寫入文件"""
    print("正在進行 Google API 認證...")
    
    # 透過服務帳號金鑰進行認證
    creds = service_account.Credentials.from_service_account_info(
        sa_credentials_json, scopes=SCOPES)
        
    # 建立 Google Docs 服務的客戶端
    service = build('docs', 'v1', credentials=creds)

    try:
        print(f"正在讀取文件 ID: {DOCUMENT_ID}...")
        # 取得文件目前的內容，以便找到最後的位置
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        doc_content = document.get('body').get('content')
        
        # 計算文件末端的索引位置
        # 我們插入在最後一個元素的後面
        end_index = doc_content[-1].get('endIndex') - 1
        
        print(f"文件末端索引為: {end_index}")

        # 準備要執行的請求：在文件末端插入文字
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': TEXT_TO_ADD
                }
            }
        ]

        print(f"正在寫入文字: '{TEXT_TO_ADD.strip()}'")
        # 執行批次更新請求
        service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()
            
        print("成功寫入 Google 文件！")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == '__main__':
    main()
