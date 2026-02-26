import yfinance as yf
from pykrx import stock
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# =========================
# 1. 날짜 설정 (최근 1년)
# =========================
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365 * 5)

start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")

# =========================
# 2. 삼성전자 주가 (Index 정리)
# =========================
price_raw = yf.download("005930.KS", start=start_date, end=end_date)

# MultiIndex 컬럼 제거 (환경 차이 방어)
if isinstance(price_raw.columns, pd.MultiIndex):
    price_raw.columns = price_raw.columns.get_level_values(0)

price_df = price_raw[["Close"]].copy()
price_df.index = pd.to_datetime(price_df.index).date
price_df.index.name = "Date"

# =========================
# 3. 외국인 순매수 (KRX)
# =========================
trading_df = stock.get_market_trading_volume_by_date(
    start_str,
    end_str,
    "005930"
)

trading_df = trading_df.copy()
trading_df.index = pd.to_datetime(trading_df.index).date
trading_df.index.name = "Date"

# pykrx 기준: 외국인합계 = 외국인 순매수
trading_df["ForeignNetBuy"] = trading_df["외국인합계"]
trading_df["ForeignCumulative"] = trading_df["ForeignNetBuy"].cumsum()

# =========================
# 4. join (안전한 결합)
# =========================
merged_df = price_df.join(
    trading_df[["ForeignCumulative"]],
    how="inner"
)

# =========================
# 5. 그래프
# =========================
fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.plot(
    merged_df.index,
    merged_df["Close"],
    label="Close Price (KRW)"
)
ax1.set_xlabel("Date")
ax1.set_ylabel("Price (KRW)")

ax2 = ax1.twinx()
ax2.plot(
    merged_df.index,
    merged_df["ForeignCumulative"],
    linestyle="--",
    label="Foreign Net Buy (Cumulative)"
)
ax2.set_ylabel("Foreign Net Buy (Shares)")

plt.title("Samsung Electronics: Price vs Foreign Net Buy (Last 1 Year)")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.grid(True)
plt.tight_layout()
plt.show()
