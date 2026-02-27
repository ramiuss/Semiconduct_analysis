import os, datetime
import pandas as pd
from pykrx import stock

os.makedirs("data", exist_ok=True)

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=365*5)

start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")

# 삼성전자 5년 OHLCV
samsung = stock.get_market_ohlcv_by_date(start_str, end_str, "005930")
samsung.to_csv("data/krx_005930_5y.csv")

# SK하이닉스 5년 OHLCV
hynix = stock.get_market_ohlcv_by_date(start_str, end_str, "000660")
hynix.to_csv("data/krx_000660_5y.csv")

print("saved:", len(samsung), len(hynix))