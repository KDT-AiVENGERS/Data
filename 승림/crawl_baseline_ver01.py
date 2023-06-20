# -*- coding: utf-8 -*-
"""
2023.06.20 Tue
원티드 채용공고 리스트 중, '개발' 분야 채용공고 수집을 기반으로 작성한 베이스라인 코드입니다.
각자 담당 사이트에서 DB에 채울 수 있는 데이터가 무엇인지 최대한 파악한 후,
다음 회의 때 공통적으로 수집할 수 있는 부분을 정의하면 좋겠습니다!
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


# 2. 옵션설정 : detach = 직접 확인할 수 있게 크롬창 켜놓기, service = 크롬드라이버 매니저 자동관리용입니다.
# 편하신대로 변경해서 사용하셔도 됩니다!
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


# 3. 개발직군 전체 조회 페이지로 이동 후, 필요시 직무 리스트를 반환하는 함수 사용.(개발 전체 id= 518).
start_time = time.time()
devid = 518
driver.implicitly_wait(5)


# 4. (option) get_job_list 함수는 결과로 job_list 리스트를 리턴합니다. 필요시 사용하시면 됩니다!
# 사이트별 job_list(직무명)가 동일한지 확인하기 위해 job_list는 사이트마다 생성해주시면 좋겠습니다!


def get_job_list():
    driver.get(f"https://www.wanted.co.kr/wdlist/{devid}?country=all&job_sort=company.response_rate_order")
    # 직무 리스트를 볼 수 있는 버튼을 클릭해서 활성화
    button_open = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/article/div/div[2]/button')
    button_open.click()
    # 직무 리스트를 얻어내는 단계
    job_list = []
    jobs = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[3]/article/div/div[2]/section/div[1]/div/button')
    for job in jobs:
        job_list.append(job.text)
    driver.quit()
    return job_list

# wanted_job_list = get_job_list()
# wanted_job_list.pop(0) #'개발 전체'가 있어서 삭제
# print(wanted_job_list)


# 5. 직무별 채용공고 크롤링을 위해 job_list, job_id 정의
# - wanted_job_list : get_job_list() 함수로 얻어냄
# - wanted_job_id : 원티드 측에서 해당 작업 2~3번 이상 반복 시 로그인을 요청하는 이슈 발생하여 직접 확인함
# 직무명 / wanted_job_id / 사람인_job_id / 점핏_job_id 이런 식으로 매칭할 DB테이블이 있어야 할 것 같습니다.

wanted_job_list = ['웹 개발자', '서버 개발자', '소프트웨어 엔지니어', '프론트엔드 개발자', '자바 개발자',
                   'C,C++ 개발자', '파이썬 개발자', '안드로이드 개발자', 'Node.js 개발자', 'iOS 개발자',
                   '머신러닝 엔지니어', '데이터 엔지니어', 'DevOps / 시스템 관리자', '시스템,네트워크 관리자', '개발 매니저',
                   '기술지원', 'QA,테스트 엔지니어', '데이터 사이언티스트', '보안 엔지니어', '빅데이터 엔지니어',
                   '임베디드 개발자', '프로덕트 매니저', '하드웨어 엔지니어', 'PHP 개발자', '블록체인 플랫폼 엔지니어',
                   '크로스플랫폼 앱 개발자', 'DBA', 'ERP전문가', '.NET 개발자', '웹 퍼블리셔',
                   '영상,음성 엔지니어', '그래픽스 엔지니어', 'CTO,Chief Technology Officer', 'BI 엔지니어', 'VR 엔지니어',
                   '루비온레일즈 개발자', 'CIO,Chief Information Officer']

wanted_job_id = [873, 872, 10110, 669, 660,
                 900, 899, 677, 895, 678,
                 1634, 655, 674, 665, 877,
                 1026, 676, 1024, 671, 1025,
                 658, 876, 672, 893, 1027,
                 10111, 10231, 10230, 661, 939,
                 896, 898, 795, 1022, 10112]

wanted_dict = dict(zip(wanted_job_id, wanted_job_list))


# 6. 스크롤 함수 정의
# scroll_more : 주어진 시간(초) 동안 3초에 한 번씩 스크롤 내리는 함수.
# 기본은 60초로 세팅되어 있고, second=0으로 설정하면 채용공고 전체를 찾을 때까지 수행(실제 크롤링할 때)


def scroll_more(second=60):
    if second != 0:
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=second)
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            driver.implicitly_wait(3)
            if datetime.datetime.now() > end:
                break
    elif second > 0:
        scroll_now = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            driver.implicitly_wait(3)
            scroll_height = driver.execute_script('return document.body.scrollHeight')
            if scroll_now == scroll_height:
                break
            else:
                scroll_now = driver.execute_script('return document.body.scrollHeight')
    elif second < 0:
        print('올바른 값(양수)을 입력해주세요!')


# 7. Dataframe 생성 : column은 사이트별로 수집가능한 데이터가 무엇인지 파악 후, 각자 최대한 적어서 공유 예정!
df = pd.DataFrame(columns=['직무명', '채용공고명', '해시태그', '채용공고상세', '근무지역',
                            '회사명', '회사분야', '출처'])  # 원티드는 마감일 크롤링이 불가!

# 8. 직무별 채용공고 크롤링 시작
for jobid in wanted_job_id:
    driver.get(f"https://www.wanted.co.kr/wdlist/{devid}/{jobid}?country=all&job_sort=company.response_rate_order")
    driver.implicitly_wait(3)
    # 스크롤 함수 사용 : 시간을 넉넉하게 할수록 채용공고는 많이 수집되며, 태그 찾는 시간도 더 길게 주어야 합니다!
    scroll_more(second=5)
    # li 태그 찾을 때까지 최대 5초 대기
    timeout = 5
    li_elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, "//li")))
    # 확인된 li 태그들 = 채용공고(jd) 상세 url을 리스트에 담아두기
    jd_boxes = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[3]/div/div/div[4]/ul/li')
    job_name = wanted_dict[jobid]
    print(job_name, " 직무 : 총 ", len(jd_boxes), "개 채용공고 크롤링 시작")
    url_list = []
    for li in jd_boxes:
        a_tag = li.find_element(By.XPATH, "./div/a")
        href = a_tag.get_attribute("href")
        url_list.append(href)

    # 9. 채용공고 상세정보 페이지에 접근해 필요한 정보 추출
    for url in tqdm(url_list):
        driver.get(url)
        driver.maximize_window()
        driver.implicitly_wait(3)
        head_title, hashtags, body_jd, location, company_name, company_field = [np.nan] * 6  # 변수 값 초기화
        head_title = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/section[2]/h2').text
        hashtags = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/section[2]/div[3]/ul').text
        body_jd = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/div[2]/section[1]').text
        location = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/section[2]/div[1]/span').text
        company_name = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/section[3]/button[1]/div[2]/h5').text
        company_field = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[1]/div[1]/div/section[3]/button[1]/div[2]/h6').text

        # 10. 우선 csv 형태로 추출할 수 있도록 해두겠습니다(파일명 변경 부탁드려요!)
        new_row = {'직무명': job_name, '채용공고명': head_title, '해시태그': hashtags,
                   '채용공고상세': body_jd, '근무지역': location,
                   '회사명': company_name, '회사분야': company_field,
                   '출처': url}
        df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        df.to_csv('./크롤링_원티드_ver01_230621.csv', index=False)

print(len(df), '개 데이터 크롤링 완료')
driver.quit()

# 10. 총 실행 시간 출력
end_time = time.time()
execution_time = end_time - start_time

hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = int(execution_time % 60)
print("작업 실행 시간: {}시간 {}분 {}초".format(hours, minutes, seconds))