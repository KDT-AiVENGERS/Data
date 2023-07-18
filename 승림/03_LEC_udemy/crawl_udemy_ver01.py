# -*- coding: utf-8 -*-
"""
2023.07.17 Mon
유데미 사이트의 강의(평점 4.5 이상인 강의만) 정보를 수집하는 코드입니다. 9번, 10번, 13번 라인만 확인 및 변경해주시면 됩니다!
코드 실행 중 에러 발생으로 중단될 경우, current_info.pickle 파일로 현재 정보가 저장됩니다.
"""
# 🌟 각자 수집하기로 한 카테고리 index number의 시작 숫자, 끝 숫자를 하나씩 입력해주세요! (승림 : 1,2,3)(재현 : 4,5,6)(인호 : 7,8,9)
# 7,8,9번을 담당했다면 start_idx = 7, end_idx = 9 입니다.
start_idx = 1 
end_idx = 3

# 🌟 중간에 코드가 끊겨서 다시 재시작하나요? 그러면 restart = True 로 변경해주세요. 변경하지 않으면 처음부터 다시 수집되니 주의해주세요!
restart = False

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
import pickle as pkl
from tqdm import tqdm

# 2. 실행시간 측정
start_time = time.time()

# 3. 데이터프레임 및 카테고리 정의
df = pd.DataFrame(columns=['대분류', '소분류', '강의명', '난이도', '가격(현재가격)','가격(원래가격)', '총소요시간', '강의소개', '언어', '출처']) 

categories = ["web-development", "data-science", "mobile-apps", "programming-languages", "game-development",
              "databases", "software-testing", "software-engineering", "development-tools", "no-code-development"]

# 4. current_info를 저장할 pkl 파일 정보 생성
current_info = {"category": categories[start_idx], "page": 1, "last_page": "(확인예정)", "lec_num": 0}
lec_count = current_info['lec_num']

# 5. 에러 때문에 중간부터 다시 시작하는 상황 대비
if restart == True:
    df = pd.read_csv(f"./udemy_{current_info['category']}_230718.csv") 
    with open('current_info.pickle', 'rb') as file:
        current_info = pkl.load(file)

    start_idx = categories.index(current_info['category'])
    if current_info['lec_num']==15: #강의가 16개(idx 0~15)이므로 마지막 강의면 다음 페이지로 넘어갑니다.
        current_info['page']+= 1
        current_info['lec_num'] = 0
    lec_count = current_info['lec_num'] + 1

# 6. 불러온 변수 확인 후 크롤링 시작!
print(f"크롤링 시작 : 👍 {current_info['category']} : 총 {current_info['last_page']}페이지 중 {current_info['page']}번째 페이지의 {current_info['lec_num']}번째 강의부터 수집 시작 ")

# 7. 카테고리(대분류) 돌기
try:
    for category in categories[start_idx:(end_idx + 1)]:
        options = uc.ChromeOptions()
        driver = uc.Chrome(use_subprocess=True, options=options)
        last_page = current_info['last_page']
        if last_page == "(확인예정)":
            while True:
                try:     
                    driver.get(f"https://www.udemy.com/ko/courses/development/{category}/?p=1&ratings=4.5&sort=popularity")
                    break
                except Exception as e:
                    exception_name = type(e).__name__
                    print(f"🥲 네트워크가 연결이 잘 안돼요... Exception: {exception_name}")
                    time.sleep(3)
            driver.maximize_window()
            time.sleep(5)
            last_page = int(driver.find_element(By.XPATH, '//*[@aria-label="생략 부호"]/following-sibling::span').text) #마지막 페이지 번호
            current_info['last_page'] = last_page
        current_info['category'] = category
        with open('current_info.pickle', 'wb') as file: # pickle 파일로 저장
            pkl.dump(current_info, file)

        # 8. 1페이지부터 last_page까지 페이지별 강의(lec) 크롤링
        for page in tqdm(range(current_info['page'], last_page + 1)):
            current_info["page"] = page
            while True:
                try:     
                    driver.get(f"https://www.udemy.com/ko/courses/development/{category}/?p={page}&ratings=4.5&sort=popularity")
                    break
                except Exception as e:
                    exception_name = type(e).__name__
                    print(f"🥲 네트워크가 연결이 잘 안돼요... Exception: {exception_name}")
                    time.sleep(3)
            with open('current_info.pickle', 'wb') as file:  # pickle 파일로 저장
                pkl.dump(current_info, file)
            time.sleep(3)
            lec_container = driver.find_element(By.XPATH, '//div[@class="filter-panel--paginated-course-list--A07TT"]')
            lec_boxes = lec_container.find_elements(By.XPATH, '//div[@class="course-card--main-content--2XqiY course-card--has-price-text--1c0ze"]')

            # 태그가 없는 경우, nan값을 할당하고 넘어가는 함수를 사용합니다.
            def find_element_nan(driver, path):
                try:
                    element = driver.find_element(By.XPATH, path)
                    return element.text
                except:
                    return np.nan
                
            # 9. 페이지별 강의 상세내용 크롤링 시작    
            url_list = [] #페이지마다 리셋
            for box in lec_boxes:
                a_tag = box.find_element(By.TAG_NAME, 'a')
                urls = a_tag.get_attribute('href')
                lec_times = find_element_nan(box, '//div[@data-purpose="course-meta-info"]/span[1]')
                levels = find_element_nan(box, '//div[@data-purpose="course-meta-info"]/span[3]')
                now_prices = find_element_nan(box, '//div[@data-purpose="course-price-text"]/span[2]')
                raw_prices = find_element_nan(box, '//div[@data-purpose="course-old-price-text"]/span[2]')
                url_list.append((urls, lec_times, levels, now_prices, raw_prices))

            for url_idx, (urls, lec_times, levels, now_prices, raw_prices) in enumerate(url_list):
                if url_idx >= lec_count:
                    while True:
                        try:     
                            driver.get(urls)
                            time.sleep(3)
                            break
                        except Exception as e:
                            exception_name = type(e).__name__
                            print(f"🥲 네트워크가 연결이 잘 안돼요... Exception: {exception_name}")
                            time.sleep(3)
                    current_info["lec_num"] = url_idx
                    with open('current_info.pickle', 'wb') as file: # pickle 파일로 저장
                        pkl.dump(current_info, file)
                    driver.maximize_window()
                    time.sleep(3)
                    
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
                    lec_time = lec_times
                    body = find_element_nan(driver, '//div[@class="component-margin what-you-will-learn--what-will-you-learn--1nBIT"]')
                    language = find_element_nan(driver, '//div[@data-purpose="lead-course-locale"]')
                    url = urls

                    # 8. csv 형태로 추출
                    new_row = {'대분류': category, '소분류': hashtag, '강의명': title, '난이도': level, 
                            '가격(현재가격)': now_price, '가격(원래가격)': raw_price, '총소요시간': lec_time, 
                            '강의소개': body, '언어': language, '출처': url}
                    df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
                    df.to_csv(f'./udemy_{category}_230718.csv', index=False)
            lec_count = 0
        driver.quit()

except KeyboardInterrupt:
    print(f"👍 {current_info['category']} : 총 {current_info['last_page']}페이지 중 {current_info['page']}번째 페이지의 {current_info['lec_num']}번째 강의까지 수집 완료 ")


# 10. 총 실행 시간 출력
print(len(df), '개 데이터 크롤링 완료')
end_time = time.time()
execution_time = end_time - start_time

hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)
print("작업 실행 시간: {}시간 {}분 {}초".format(hours, minutes, seconds))