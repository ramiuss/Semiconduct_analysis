import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# 1. CSV 파일 불러오기
file_name = 'result_hbm.csv' 
df = pd.read_csv(file_name)

# --- [추가된 부분] 데이터 전처리: 문자열을 숫자로 변환 ---
def clean_numeric(value):
    if pd.isna(value): return 0
    # 숫자와 마침표(.)만 남기고 모두 제거 (단위, 콤마 등 삭제)
    cleaned = re.sub(r'[^\d.]', '', str(value))
    return float(cleaned) if cleaned else 0

# 계산에 필요한 컬럼들을 숫자로 강제 변환합니다.
df['data__accelerators__capacity'] = df['data__accelerators__capacity'].apply(clean_numeric)
df['data__accelerators__spec'] = df['data__accelerators__spec'].apply(clean_numeric)
df['data__accelerators__stacks'] = df['data__accelerators__stacks'].apply(clean_numeric)
# --------------------------------------------------

# 2. 데이터 확인
print("--- 변환 후 데이터 타입 확인 ---")
print(df[['data__accelerators__capacity', 'data__accelerators__spec']].dtypes)

# 3. 그래프 그리기 설정
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# 4. 시각화
plt.title('AI Accelerators: HBM Capacity vs Bandwidth', fontsize=15)
scatter = sns.scatterplot(
    data=df, 
    x='data__accelerators__capacity', 
    y='data__accelerators__spec', 
    hue='data__accelerators__arch', 
    size='data__accelerators__stacks',
    sizes=(50, 400),
    alpha=0.7
)

# 점 옆에 아키텍처(arch) 이름 표시
for i in range(df.shape[0]):
    plt.text(df['data__accelerators__capacity'].iloc[i] + 0.5, 
             df['data__accelerators__spec'].iloc[i], 
             df['data__accelerators__arch'].iloc[i], fontsize=9)

plt.xlabel('HBM Capacity (GB)')
plt.ylabel('HBM Bandwidth (Spec Value)')
plt.legend(title='Architecture', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# 5. 간단한 통계 분석 (이제 에러 없이 작동합니다!)
print("\n--- 아키텍처별 평균 대역폭(Spec) ---")
summary = df.groupby('data__accelerators__arch')['data__accelerators__spec'].mean().sort_values(ascending=False)
print(summary)

plt.show()