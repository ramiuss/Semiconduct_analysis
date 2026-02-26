import yfinance as yf
from pykrx import stock
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# ===============================
# 1. 날짜 설정
# ===============================
end_date = datetime.date.today() - datetime.timedelta(days=1)
start_date = end_date - datetime.timedelta(days=365 * 5)

start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")

print(f"조회 기간: {start_str} ~ {end_str}")

# ===============================
# 2. KOSPI 지수
# ===============================
kospi_df = yf.download(
    "^KS11",
    start=start_date,
    end=end_date + datetime.timedelta(days=1),
    progress=False
)

if isinstance(kospi_df.columns, pd.MultiIndex):
    kospi_df.columns = kospi_df.columns.get_level_values(0)

kospi_df = kospi_df[['Close']].copy()
kospi_df.index = pd.to_datetime(kospi_df.index)

# ===============================
# 3. pykrx 데이터
# ===============================
df_market = stock.get_market_cap_by_date(start_str, end_str, "KOSPI")
df_investor = stock.get_market_trading_value_by_date(start_str, end_str, "KOSPI")

df_market.index = pd.to_datetime(df_market.index)
df_investor.index = pd.to_datetime(df_investor.index)

# ===============================
# 4. 외국인 지분율
# ===============================
if '외국인지분율' in df_market.columns:
    df_market['Foreign_Rate'] = df_market['외국인지분율']
    foreign_available = True
else:
    foreign_available = False
    print("⚠ 외국인지분율 컬럼이 없어 그래프에서 제외됩니다.")

# ===============================
# 5. 개인 누적 순매수
# ===============================
p_cols = [c for c in df_investor.columns if '개인' in c]
if not p_cols:
    raise ValueError("개인 순매수 컬럼을 찾을 수 없습니다.")

df_investor['Individual_Cum'] = (
    df_investor[p_cols[0]].cumsum() / 1_000_000_000_000
)

# ===============================
# 6. 데이터 결합
# ===============================
dfs = [
    kospi_df,
    df_investor[['Individual_Cum']]
]

if foreign_available:
    dfs.append(df_market[['Foreign_Rate']])

merged_df = pd.concat(dfs, axis=1, join='inner').dropna()

# ===============================
# 7. 시각화 (정상 구조)
# ===============================
fig, ax1 = plt.subplots(figsize=(15, 8))

# KOSPI (면적 + 선)
ax1.fill_between(
    merged_df.index,
    merged_df["Close"],
    color="gray",
    alpha=0.15
)
ax1.plot(
    merged_df.index,
    merged_df["Close"],
    color="gray",
    linewidth=1
)
ax1.set_ylabel("KOSPI Index")

# 외국인 지분율 (있을 때만)
legend_lines = []
legend_labels = []

legend_lines.append(
    plt.Line2D([0], [0], color="gray", lw=4, alpha=0.3)
)
legend_labels.append("KOSPI Index")

if foreign_available:
    ax2 = ax1.twinx()
    l1 = ax2.plot(
        merged_df.index,
        merged_df["Foreign_Rate"],
        color="red",
        linewidth=2
    )
    ax2.set_ylabel("Foreign Ownership (%)", color="red")
    ax2.tick_params(axis='y', labelcolor='red')

    legend_lines += l1
    legend_labels.append("Foreign Ownership (%)")

# 개인 누적 순매수 (항상 선 그래프)
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
l2 = ax3.plot(
    merged_df.index,
    merged_df["Individual_Cum"],
    color="blue",
    linewidth=2
)
ax3.set_ylabel("Individual Cum. Buy (Trillion KRW)", color="blue")
ax3.tick_params(axis='y', labelcolor='blue')

legend_lines += l2
legend_labels.append("Individual Cum. Buy (Trillion)")

ax1.legend(legend_lines, legend_labels, loc="upper left")

plt.title("KOSPI 5Y Analysis: Index vs Foreign vs Individual", fontsize=16)
plt.grid(True, linestyle=":")
plt.tight_layout()
plt.show()
