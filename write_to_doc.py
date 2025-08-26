import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 從環境變數讀取資訊 ---
# 1. 從 GitHub Secrets 讀取服務帳號金鑰
key_file_content = os.getenv('GCP_SA_KEY')
if not key_file_content:
    raise ValueError("錯誤：GCP_SA_KEY 祕密未設定。")

# 2. 從 GitHub Action 的輸入讀取故事內容
story_content = os.getenv('STORY_CONTENT')
if not story_content:
    raise ValueError("錯誤：故事內容為空。")

# 3. 您的 Google 文件 ID
DOCUMENT_ID = '1o5rTZ9iCnYDuRxt7HOW12jB7U1mNTspXj4V5Xarh1Mc' 

# 將金鑰字串轉換回 JSON 物件
sa_credentials_json = json.loads(key_file_content)

# 設定 API 範圍
SCOPES = ['https://www.googleapis.com/auth/documents']

def main():
    """主執行函式：清空並寫入新的故事內容至文件"""
    print("正在進行 Google API 認證...")
    
    creds = service_account.Credentials.from_service_account_info(
        sa_credentials_json, scopes=SCOPES)
        
    service = build('docs', 'v1', credentials=creds)

    try:
        print(f"正在讀取文件 ID: {DOCUMENT_ID}...")
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        doc_content = document.get('body').get('content')
        
        # 計算文件末端的索引位置。文件本體從 index 1 開始。
        end_of_doc_index = doc_content[-1].get('endIndex') - 1
        
        requests = []

        # 請求 1: 如果文件不是空的，就先刪除從頭到尾的所有內容
        if end_of_doc_index > 1:
            print(f"文件非空，準備清空內容 (從 index 1 到 {end_of_doc_index})...")
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_of_doc_index,
                    }
                }
            })

        # 請求 2: 在文件的開頭 (index 1) 插入新的完整故事內容
        print("準備插入新的故事內容...")
        requests.append({
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': story_content
            }
        })

        print("正在執行批次更新...")
        service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()
            
        print("成功將最新故事內容寫入 Google 文件！")

    except Exception as e:
        print(f"發生錯誤: {e}")
        # 引發錯誤以讓 GitHub Action 知道此步驟失敗
        raise e

if __name__ == '__main__':
    main()
