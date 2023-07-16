# -*- coding: utf-8 -*-
"""
2023.07.16 Sun
유데미 사이트의 강의 정보를 수집하는 코드입니다.
개 데이터가 수집되었습니다.
"""

# 1. 필요 모듈 가져오기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import datetime
import time
import pandas as pd
import numpy as np
from tqdm import tqdm


# 2. 옵션설정
# service = Service(executable_path=ChromeDriverManager().install())
options = uc.ChromeOptions() 
start_time = time.time()

# 3. 카테고리별로 평점 4.5 이상인 강의들만 리스트 수집
categories = ["web-development", "data-science", "mobile-apps", "programming-languages", "game-development",
              "databases", "software-testing", "software-engineering", "development-tools", "no-code-development"]

df = pd.DataFrame(columns=['분류', '강의명', '난이도', '가격(현재가격)','가격(원래가격)', '총소요시간', '강의소개']) 

for category in categories :
    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.get(f"https://www.udemy.com/ko/courses/development/{category}/?p=1&ratings=4.5&sort=popularity")
    time.sleep(5)
    driver.maximize_window()
    last_page = int(driver.find_element(By.XPATH, '//*[@aria-label="생략 부호"]/following-sibling::span').text) #마지막 페이지 번호
    print(last_page)

    # 4. 1페이지부터 last_page까지 페이지별 강의(lec) 크롤링
    url_list = []
    for i in range(1,last_page+1):
    # for i in range(1,2): #test
        driver.get(f"https://www.udemy.com/ko/courses/development/{category}/?p={i}&ratings=4.5&sort=popularity")
        time.sleep(5)
        lec_boxes = driver.find_elements(By.XPATH, '//*[@id="udemy"]/div[1]/div[2]/div/div/div[6]/div[2]/div/div[2]/div/div[2]/div[2]/div')
        for box in lec_boxes:
            a_tag = box.find_element(By.TAG_NAME, 'a')
            urls = a_tag.get_attribute('href')
            # ~~\n초급자\n현재 가격\n₩17,000\n원래 가격\n₩88,000 형태로 box에서 정보 추출 확인
            try:
                details=box.text.split("\n현재 가격\n")
                levels=details[0].split("\n")[-1]
                
            except IndexError:
                continue
            try:
                now_prices = details[1].split('\n')[0]
            except IndexError:
                now_prices = np.nan
            try:
                raw_prices = details[1].split('\n')[2]
            except IndexError:
                raw_prices = np.nan
            
            url_list.append((urls, levels, now_prices, raw_prices))
    # driver.quit()
    # print(url_list)
    print(category," : ", len(url_list), "개 강의 크롤링 시작")
    
    # 5. 페이지별 강의 상세내용 크롤링 시작
    # driver = uc.Chrome(use_subprocess=True, options=options)
    for url, levels, now_prices, raw_prices in tqdm(url_list):
        if url != "https://udemy.wjtb.co.kr/insight/index?ref=right-rail&locale=ko_KR": #유데미 광고 페이지인 경우에는 크롤하지 않음
            driver.get(url)
            time.sleep(3)
            driver.maximize_window()
            # driver.implicitly_wait(5)  # 에러 방지를 위해 최대 5초 대기
            time.sleep(3)
            # 5-1. 태그가 없는 경우, nan값을 할당하고 넘어가는 함수를 사용
            def find_element_nan(driver, path):
                try:
                    element = driver.find_element(By.XPATH, path)
                    return element.text
                except:
                    return np.nan
            
            # hashtags = find_element_nan(driver, '//a[contains(@href, "topic")]')
            try:
                hashtags_parent = driver.find_element(By.CLASS_NAME, 'topic-menu.topic-menu-condensed.ud-breadcrumb')
                hashtags_a = hashtags_parent.find_elements(By.TAG_NAME, 'a')
                hashtag = hashtags_a[-1].text
            except:
                hashtag = np.nan

            title = find_element_nan(driver, '//h1[@data-purpose="lead-title"]')
            level = levels
            now_price = now_prices
            raw_price = raw_prices
            lec_time = find_element_nan(driver, '//span[@data-purpose="video-content-length"]')
            body = find_element_nan(driver, '//div[@class="component-margin what-you-will-learn--what-will-you-learn--1nBIT"]')
            
            # 5. csv 형태로 추출
            new_row = {'분류': hashtag, '강의명': title, '난이도': level, '가격(현재가격)': now_price, '가격(원래가격)':raw_price,
                        '총소요시간': lec_time, '강의소개': body, '출처': url}
            df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
            df.to_csv('./udemy_ver01_230715.csv', index=False)

    driver.quit()

# 6. 총 실행 시간 출력
print(len(df), '개 데이터 크롤링 완료')
end_time = time.time()
execution_time = end_time - start_time

hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)
print("작업 실행 시간: {}시간 {}분 {}초".format(hours, minutes, seconds))