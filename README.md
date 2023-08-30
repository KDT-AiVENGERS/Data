[북극성 통합 repository 바로가기](https://github.com/KDT-AiVENGERS/.github/tree/develop/profile/polarstar)  
  
# Data repository📌
Data 저장소는 북극성 프로젝트의 채용공고 추천 및 강의 추천에 사용된 **데이터의 수집 및 전처리**를 수행하기 위한 목적으로 만들어졌습니다.  
팀원 개인별 폴더를 만들어 각자 담당한 출처에서 데이터를 수집하는 코드를 작성 및 실행하였으며, 지속적으로 상호 연락하며 보완하는 과정을 거쳐 데이터를 수집하고 처리하였습니다. 뿐만 아니라 수집한 데이터를 활용해 EDA, 형태소 분석, 단어 임베딩 등 Task에 활용해 볼 법한 사항들을 실험하기도 하였습니다.  
  
# Teammates📌
|곽찬혁|김재현|백승림|임태근|최인호|
|-----|-----|-----|-----|-----|
  
# Data Collection📌
공고데이터의 경우 총 5개의 사이트를 수집하였으나 수집 데이터 처리의 시간비용을 고려하여 **3개 사이트**에서 수집한 데이터만을 활용하였습니다. 수집한 데이터와 출처사이트는 아래와 같습니다.  
  
1. 채용공고 데이터(Wanted, Jumpit, Jobplanet)  
2. 강의 데이터(Udemy)  
  
<img src="https://github.com/KDT-AiVENGERS/Data/assets/77615059/118d5f8c-a7f0-4dba-a3ba-d7d866ea513f" width=900 height=400>
  
# Data Preprocessing📌
- **채용공고 데이터**는 기 훈련된 BERT 모델의 Domain Adaptation을 위한 MLM 방식 훈련에 사용하기 위하여 중복제거, 데이터 표준화 등의 전처리를 수행하였습니다.
- **강의 데이터**는 강의추천 알고리즘에 활용할 목적으로 데이터 형식 및 타입을 통일하고 결측치를 제거하는 등의 전처리를 수행하였습니다.
  
<img src="https://github.com/KDT-AiVENGERS/Data/assets/77615059/bda23fad-b379-4520-94c0-ce0fed89074b" width=650 height=420> 
  
형태소 분석을 통해 공고상 중복되어 등장하게 되는 의미없는 듯한 단어들(~하신 분, 경험 etc..)을 제거하여 Input으로 활용했을 때 성능을 비교해 보고자 하였습니다. 분석 및 불용어 선택까지는 진행이 되었으나 시간상 제약으로 모델학습 및 비교작업까지 진행하지는 못하였습니다.

# Libraries📌
1. Selenium, BeautifulSoup Pandas, Numpy, matplotlib, seaborn, Scikit-learn  
2. Konlpy(Okt, Mecab, Hannanum), nltk
3. Customized Konlpy

# Details📌
### Crawling Code Develop  
[Crawling Code 예시](https://github.com/KDT-AiVENGERS/PolarStar-Data/blob/develop/%EC%8A%B9%EB%A6%BC/01_JD_wanted/crawl_baseline_ver02.py)  
- 크롤링 시, **네트워크 불안정 혹은 Keyboard Interruption 등**으로 수집을 일시정지해야 하는 경우에 대비하기 위해 pkl 파일로 수집현황을 저장하여 원활한 크롤링이 진행될 수 있도록 코드를 develop하였습니다.  
- 개인 PC 환경에 따라 **인터넷 속도 차이로 인한 데이터 손실 문제**가 발생하는 것을 확인하고, 팀원별로 데이터 수집 현황을 체크하며 sleep 시간 변경 혹은 일정량 크롤링 후 chromedriver를 close 후 재실행 처리하는 등의 추가 작업을 수행하였습니다.  
  
### Data Preprocessing
#### 공고 데이터 처리
- 사이트 별로 상이한 column을 “회사명, 지원기간, 공고명, 직무내용, 자격요건, 우대조건, 경력조건, 기술 스택, 출처 URL, 복지, 회사소개, 주요업무”로 통일하였습니다.
- 크롤링 과정에서 결측된 부분은 채워주는 방식을 사용하였고 그 외 결측치 행은 삭제를 진행하였습니다.
- 경력조건 column의 내용은 사이트별로 내용이 상이하여 정규표현식을 사용하여 n년이상의 경력이면 n으로 신입은 0으로 정수형으로 처리 하였습니다.
- 사이트별 상이한 직무내용 데이터를 통일시키고 직무내용이 다르고 나머지 column의 내용이 같은 데이터들은 concat하여 여러 직무내용을 가질 수 있도록 만들었습니다.
- 데이터의 핵심이 될 기술스택 column의 데이터의 결측치가 많아 자격요건 column과 concat하는 방식으로 데이터를 보존하였습니다.
- 추가적인 데이터가 들어오면 같은 frame으로 만들어 질 수 있도록 작성하였습니다.
  
#### 강의 데이터 처리
- 강의추천 로직에 주요하게 쓰일 강의소개 Column부분이 결측인 데이터는 삭제처리하였습니다. 제공 언어와 강의소개에 쓰인 언어가 다른 강의를 이상치로 판별하여 제거하였습니다.
- 가격 Column의 숫자 형식을 통일하였고 무료인 경우 0으로 대치하였습니다. 총 소요시간 Column의 경우 H시간 MM분 형태로 통일하여 데이터를 표준화 하였습니다.
- 서비스 대상 유저가 대중적으로 사용할 것으로 예상되는 한국어, 영어 강의만을 선택하였습니다.  
  
<span style="color:red">각 처리 코드에 대한 링크??</span>  
