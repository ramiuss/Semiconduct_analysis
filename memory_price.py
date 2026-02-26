import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# 1. 데이터 소스 URL
urls = [
    "https://www.trendforce.com/presscenter/news/2026-memory-price-outlook", 
    "https://www.counterpointresearch.com/memory-prices-2026"
]

data = []

# 2. 각 URL에서 데이터 크롤링
for url in urls:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text()
        if "HBM" in text or "DRAM" in text or "NAND" in text:
            # 정규표현식으로 % 변화 추출
            match = re.search(r"(\d+)%", text)
            if match:
                change = match.group(1)
            else:
                change = None
            data.append({
                "year": 2026,
                "memory": "기사본문",
                "price_usd": None,
                "trend": text,
                "change_percent": change,
                "source": url
            })

# 3. 샘플 데이터 추가
sample_data = [
    {"year": 2025, "memory": "HBM3", "price_usd": 700, "trend": "상승", "change_percent": 20, "source": "sample"},
    {"year": 2026, "memory": "HBM3e", "price_usd": 900, "trend": "급등", "change_percent": 30, "source": "sample"},
    {"year": 2026, "memory": "DDR5", "price_usd": 150, "trend": "보합", "change_percent": 0, "source": "sample"},
    {"year": 2026, "memory": "NAND", "price_usd": 100, "trend": "상승", "change_percent": 10, "source": "sample"},
]

# 4. 합치기
df_web = pd.DataFrame(data)
df_sample = pd.DataFrame(sample_data)
merged_df = pd.concat([df_web, df_sample], ignore_index=True)

# 5. CSV 저장
merged_df.to_csv("result_hbm.csv", index=False, encoding="utf-8-sig")

print("✅ result_hbm.csv 파일 생성 완료!")
