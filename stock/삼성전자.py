import yfinance as yf
import datetime
import matplotlib.pyplot as plt

# =========================
# 날짜 설정 (최근 1개월)
# =========================
end = datetime.date.today()
start = end - datetime.timedelta(days=30)

# =========================
# 삼성전자 티커
# =========================
ticker = "005930.KS"

# =========================
# 주가 데이터 다운로드
# =========================
df = yf.download(ticker, start=start, end=end)

# 데이터 확인 (선택)
print(df.head())

# =========================
# 그래프 그리기
# =========================
plt.figure(figsize=(10, 5))
plt.plot(df.index, df["Close"])
plt.title("Samsung Electronics - Last 1 Month")
plt.xlabel("Date")
plt.ylabel("Price (KRW)")
plt.grid(True)
plt.tight_layout()
plt.show()
