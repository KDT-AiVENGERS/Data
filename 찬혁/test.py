import pandas as pd

filename = './empty_file.csv'

# 빈 데이터프레임 생성
df = pd.DataFrame()

# CSV 파일 저장
df.to_csv(filename, index=False)

print(f'빈 CSV 파일 {filename}이 생성되었습니다.')