import pandas as pd
import json
import time
import random
from bs4 import BeautifulSoup
import os

# 引入Selenium相关模块
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException 

# --- 核心配置 ---
SEARCH_URL = "https://we.51job.com/pc/search"

# TODO: 请在这里填入你从浏览器中【重新复制】的、最新的Cookie字符串
COOKIES_STR = '' # 例如: 'acw_tc=...; ssxmod_itp=...;'

def parse_cookies(cookies_str):
    if not cookies_str: return []
    cookies_list = []
    for item in cookies_str.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookies_list.append({'name': name, 'value': value, 'domain': '.51job.com'})
    return cookies_list

def get_job_info_with_selenium(keyword, pages):
    """
    使用Selenium驱动真实浏览器，【通过模拟点击'下一页'按钮】来翻页。
    """
    
    # --- 1. 初始化 WebDriver ---
    print("正在初始化浏览器驱动...")
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
    
    driver_path = os.path.join(os.path.dirname(__file__), '..', 'drivers', 'chromedriver.exe')
    
    try:
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"浏览器驱动初始化失败: {e}")
        return pd.DataFrame()
    print("浏览器驱动初始化成功。")

    # --- 2. 准备工作：访问主页，添加Cookie ---
    driver.get("https://we.51job.com/") 
    cookies = parse_cookies(COOKIES_STR)
    if not cookies:
        print("【警告】Cookie为空！")
    else:
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookie添加成功。")

    # --- 3. 首次访问搜索结果的第一页 ---
    print("正在加载搜索结果第一页...")
    target_url = f"{SEARCH_URL}?keyword={keyword}&jobArea=000000&pageNum=1"
    driver.get(target_url)
    
    all_jobs_data = []

    # --- 4. 循环点击'下一页'按钮 ---
    for page in range(1, pages + 1):
        print(f"--- 正在处理第 {page} 页数据 ---")

        try:
            # 等待职位列表加载完成
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "joblist-item-job"))
            )
            print("页面职位列表加载成功！")
            time.sleep(random.uniform(1.5, 2.5)) # 等待JS渲染

            # 提取当前页面的数据
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            job_cards = soup.find_all('div', class_='joblist-item-job')

            if not job_cards:
                print(f"警告：第 {page} 页未解析出职位卡片，可能为空白页。")
                continue # 继续尝试下一页

            page_job_count = 0
            for card in job_cards:
                if 'sensorsdata' in card.attrs:
                    try:
                        job_data = json.loads(card['sensorsdata'])
                        all_jobs_data.append(job_data)
                        page_job_count += 1
                    except json.JSONDecodeError:
                        pass
            
            print(f"第 {page} 页成功解析到 {page_job_count} 条新职位。")

            # 【核心翻页步骤】查找并点击“下一页”按钮
            # 检查是否是最后一页 (如果"下一页"按钮是灰色不可点击状态)
            next_button = driver.find_element(By.CLASS_NAME, "btn-next")
            if "is-disabled" in next_button.get_attribute("class"):
                print("检测到'下一页'按钮已禁用，已到达最后一页。抓取结束。")
                break
            
            # 如果不是最后一页，则点击按钮
            next_button.click()
            print("已点击【下一页】，等待页面刷新...")

        except TimeoutException:
            print(f"错误：在第 {page} 页等待职位列表超时，可能已被拦截或网络问题。")
            break
        except NoSuchElementException:
            print(f"错误：在第 {page} 页未找到'下一页'按钮，抓取结束。")
            break
        except Exception as e:
            print(f"抓取第 {page} 页时发生未知错误: {e}")
            break
            
    # --- 5. 关闭浏览器 ---
    driver.quit()
    print("浏览器已关闭。")

    if not all_jobs_data:
        return pd.DataFrame()
    
    # 因为数据是累加的，最后再统一创建DataFrame和去重
    df = pd.DataFrame(all_jobs_data)
    print(f"\n去重前，共抓取到 {len(df)} 条职位记录。")
    df.drop_duplicates(subset=['jobId'], inplace=True)
    print(f"基于'jobId'去重后，剩余 {len(df)} 条独一无二的职位。")
    
    required_columns = ['jobId', 'jobTitle', 'jobArea', 'jobSalary', 'jobYear', 'jobDegree','companyId', 'companyName', 'companyTypeString', 'companySizeString','jobLabel', 'jobHref']
    existing_columns = [col for col in required_columns if col in df.columns]
    return df[existing_columns]

if __name__ == '__main__':
    search_keyword = 'Python'
    total_pages = 50 # 设定目标抓取50页
    
    df_raw = get_job_info_with_selenium(search_keyword, total_pages)
    
    if not df_raw.empty:
        output_path = '../data/jobs_raw.csv'
        df_raw.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n【成功】数据抓取与去重完成！")
        print(f"最终获得 {len(df_raw)} 条有效职位数据已保存至 '{output_path}'")
    else:
        print("\n【任务结束】未能获取任何数据，请检查错误日志。")
