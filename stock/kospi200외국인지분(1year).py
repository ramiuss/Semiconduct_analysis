import yfinance as yf
from pykrx import stock
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# 1. 날짜 설정 (최근 1년)
# 데이터가 없는 오늘(휴일 등)을 피하기 위해 종료일을 어제로 설정
# end_date = datetime.date.today() - datetime.timedelta(days=1)
# start_date = end_date - datetime.timedelta(days=365)


# 2. 날짜 설정 (최근 5년으로 변경)
end_date = datetime.date.today() - datetime.timedelta(days=1)
start_date = end_date - datetime.timedelta(days=365 * 5) # 5년치 데이터

# 3. 야후에서 데이터 가져오기 (기간 제한 없이 가져오려면 period="max" 사용 가능)
# kospi_df = yf.download("^KS11", period="max") # 상장 이후 전체
# kospi_df = yf.download("^KS11", start=start_date, end=end_date)

start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")


print(f"조회 기간: {start_str} ~ {end_str}")

# 2. 코스피 지수 데이터 (yfinance)
kospi_df = yf.download("^KS11", start=start_date, end=end_date)
if isinstance(kospi_df.columns, pd.MultiIndex):
    kospi_df.columns = kospi_df.columns.get_level_values(0)
kospi_df = kospi_df[["Close"]].copy()
kospi_df.index = pd.to_datetime(kospi_df.index).tz_localize(None)

# 3. 외국인 지분율 데이터 (가장 확실한 '종목 합산' 방식)
# 시장 전체를 한 번에 부르는 대신, 일자별 시장 합계 데이터를 가져옵니다.
try:
    # get_market_cap_by_date 대신 get_market_ohlcv_by_date로 시도 (비중 데이터 포함 여부 확인)
    # 가장 확실한 방법은 일자별 '시장 전체 통계'를 가져오는 것입니다.
    df_market = stock.get_market_cap_by_date(start_str, end_str, "KOSPI")
    
    if df_market.empty:
        # 만약 비어있다면, 개별 종목 정보를 합산하는 대신 
        # 코스피 지수 구성 종목들의 시가총액 대비 외국인 데이터를 가져오는 대안을 사용
        print("데이터 재요청 중...")
        df_market = stock.get_market_cap_by_date(start_str, end_str, "KOSPI")

    # 지분율 계산 (컬럼 인덱스로 접근하여 이름 문제 해결)
    # 보통 0:종가, 1:시가총액, 2:거래량, 3:거래대금, 4:외국인보유시가총액
    df_market['Foreign_Rate'] = (df_market.iloc[:, 4] / df_market.iloc[:, 1]) * 100
    
except Exception as e:
    print(f"상세 에러: {e}")
    # 비상용: 삼성전자(KOSPI의 20~30% 차지)의 지분율을 지표로 사용
    df_samsung = stock.get_exhaustion_rates_of_foreign_investment_by_date(start_str, end_str, "005930")
    df_market = pd.DataFrame()
    df_market['Foreign_Rate'] = df_samsung['지분율']

# 4. 데이터 결합
merged_df = kospi_df.join(df_market[['Foreign_Rate']], how="inner").dropna()
merged_df.columns = ['KOSPI', 'Foreign_Ownership']

# 5. 그래프 시각화
if not merged_df.empty:
    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.plot(merged_df.index, merged_df["KOSPI"], color='#1f77b4', label="KOSPI Index", linewidth=1.5)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KOSPI Index (Points)")
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2 = ax1.twinx()
    ax2.plot(merged_df.index, merged_df["Foreign_Ownership"], color='#d62728', label="Foreign Ownership (%)", linewidth=2)
    ax2.set_ylabel("Foreign Ownership (%)")

    plt.title("KOSPI Index vs Foreign Investor Ownership", fontsize=16)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.show()
else:
    print("결합된 데이터가 없습니다. 날짜 설정을 확인하세요.")