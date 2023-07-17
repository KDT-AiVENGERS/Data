# -*- coding: utf-8 -*-
"""
2023.07.15 Sat
프로그래머스 사이트의 강의 정보를 수집하는 코드입니다.
126개 데이터가 수집되었습니다.
"""

# 1. 필요 모듈 가져오기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import time
import pandas as pd
import numpy as np
from tqdm import tqdm

# 2. 옵션설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
service = Service(executable_path=ChromeDriverManager().install())

start_time = time.time()

# 3. 마지막 페이지 url 확인 후 last_page 확인
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(f"https://school.programmers.co.kr/learn?page=1")
time.sleep(1)
button_last = driver.find_element(By.XPATH, '//*[@id="edu-service-app-main"]/div/div[2]/div/div/section[2]/div/button[4]')
button_last.click()
time.sleep(1)
last_page_url = driver.current_url

last_page = int(last_page_url.split("page=")[1])

# 4. 1페이지부터 last_page까지 페이지별 강의(lec) 크롤링
df = pd.DataFrame(columns=['분류', '강의명', '난이도', '가격(원가-할인가)', '총소요시간', '강의소개']) 
url_list = []
for i in range(1,last_page+1):
    driver.get(f"https://school.programmers.co.kr/learn?page={i}")
    time.sleep(1)
    lec_boxes = driver.find_elements(By.XPATH, '//*[@id="edu-service-app-main"]/div/div[2]/div/div/section[2]/a')
    urls = [lec.get_attribute('href') for lec in lec_boxes]
    url_list.extend(urls)
driver.quit()
print(len(url_list), "개 강의 크롤링 시작")

# 4. 페이지별 강의 상세내용 크롤링 시작
driver = webdriver.Chrome(service=service, options=chrome_options)
for url in tqdm(url_list):
    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(5)  # 에러 방지를 위해 최대 5초 대기

    # 4-1. 태그가 없는 경우, nan값을 할당하고 넘어가는 함수를 사용
    def find_element_nan(driver, xpath):
        try:
            element = driver.find_element(By.XPATH, xpath)
            return element.text
        except:
            return np.nan
    
    hashtags = find_element_nan(driver, '//h3[contains(text(), "사용 언어")]/following-sibling::div')
    title = find_element_nan(driver, '//*[@id="overview-fixed-menu"]/div/h3')
    level = find_element_nan(driver, '//h3[contains(text(), "코스 난이도")]/following-sibling::div')
    price = find_element_nan(driver, '//*[@id="overview-fixed-menu"]/div/div')
    lec_time = find_element_nan(driver, '//*[@id="overview-fixed-menu"]/div/ul/li[3]/h6') #시간이 아니라 다른 요소가 담길 수 있어서 후처리 필요!
    body = find_element_nan(driver, '//*[@class="content-item"]')
    
    # 5. csv 형태로 추출
    new_row = {'분류': hashtags, '강의명': title, '난이도': level, '가격(원가-할인가)': price,
                '총소요시간': lec_time, '강의소개': body, '출처': url}
    df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
    df.to_csv('./prgms_ver01_230715.csv', index=False)

driver.quit()

# 6. 총 실행 시간 출력
print(len(df), '개 데이터 크롤링 완료')
end_time = time.time()
execution_time = end_time - start_time

hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)
print("작업 실행 시간: {}시간 {}분 {}초".format(hours, minutes, seconds))