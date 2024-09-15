
import json
# from llama_cpp import Llama
# from bs4 import BeautifulSoup

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
import time
from duckduckgo_search import DDGS

from concurrent.futures import ThreadPoolExecutor, as_completed

import os
from dotenv import load_dotenv
from groq import Groq


# 載入 .env 檔案
load_dotenv()

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)

def search_duckduckgo(query):
    results = DDGS().text(query, max_results=3)
    return results

    # 設定 Chrome 的選項
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # 啟用無頭模式（背景執行，不顯示瀏覽器）

    # 使用 ChromeDriver 來啟動瀏覽器
    service = Service(executable_path='C://Users//pondahai//Downloads//chromedriver-win64//chromedriver.exe')  # 請確保替換為你的 chromedriver 路徑
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 打開 DuckDuckGo
    driver.get("https://duckduckgo.com/html")
    
    # 找到搜尋框並輸入查詢內容
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.submit()

    time.sleep(2)  # 等待頁面加載

    # 抓取搜尋結果
    results = []
    search_results = driver.find_elements(By.CLASS_NAME, 'result__snippet')
    #print(search_results)
    for result in search_results:
        #print(result)
        text = result.text
        link = result.get_attribute('href')
        results.append({'text': text, 'link': link})

    # 關閉瀏覽器
    driver.quit()
    
    return results

def format_prompt(instruction, chat, question):
    message = [
        {"role": "system", "content": instruction},
        *[
            {"role": "user", "content": entry['human']} if 'human' in entry else {"role": "assistant", "content": entry['assistant']}
            for entry in chat
        ],
        {"role": "user", "content": question}
    ]
    return message


def stream_chat_completions(prompt, max_retries=3):

    data = {
        'model': 'your-model-name',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': True,
        'max_tokens': 8192
    }

    chat_completion = client.chat.completions.create(
        messages=[{'role': 'user', 'content': prompt}],
        model="llama3-8b-8192",
    )
    
    yield chat_completion.choices[0].message.content




if __name__ == "__main__":
    query = input("請輸入搜尋關鍵字：")
    
    parsing_question = "接下來我會輸入一個提問，你根據這個這項提問，生成三條要在搜尋引擎尋找背景資料的關鍵字in zh_TW，不用回答細節，不用題號，只要輸出關鍵字，每條用一行，Reply in zh_TW: "
    line = ""
    lines = [""]
    for response in stream_chat_completions(parsing_question + query):
        line += response

    lines = line.split("\n")
    print(lines)
    print()
    result = []
    
    if len(lines) == 3:
        for ask in lines:
            result += search_duckduckgo(ask)

            total = ''

            if result:
                # 假設 result 是列表形式，需要迭代處理
                for item in result:  # 你可能需要解析 result 得到真正的項目列表
                    print('--------------------')
                    print(item['body'])
                    print('====================')


        #             prompt = item['body'] + '\n我用少數幾句zh_TW總結這一段文字並且強調文中提到的數字. Reply in zh_TW.'
        # 
        #             for content in stream_chat_completions(prompt):
        #                 total += content
        #                 print(content, end='', flush=True)
                    
                    total += item['body']
                    print()
                    print()
                
                print('++++++++++++++++++++')
                print(total)
                print('++++++++++++++++++++')
                prompt = total + '\n你先用zh_TW回答分析這篇文字並且特別強調提到的數字\n然後給出基於這篇文字事實的總結短文. Reply in zh_TW.'
                for content in stream_chat_completions(prompt):
                    print(content, end='', flush=True)
         
    else:
        for answer in lines:
            print(answer)        
           
