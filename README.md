# 🦅 ARGUS Public Data

ARGUS PRIMA 시스템 전용 공개 데이터 레포지토리.

**마지막 업데이트**: 2026-05-22 14:42 UTC
**누적 데이터**: 358행 (헤더 포함)

## 파일

| 파일 | 설명 |
|:---|:---|
| `argus_data.csv` | ETF 20종 OHLCV + 매크로 전체 누적 (+ LME 구리 재고 4컬럼) |
| `argus_inventory_daily.csv` | westmetall LME 구리 cash/3mo/stock/spread 일간 forward ledger |
| `latest.json` | 최신 1행 JSON (빠른 조회) |

## Claude fetch 방법 (bash_tool)

```python
import urllib.request, json, io, pandas as pd

url = "https://raw.githubusercontent.com/daifulee/argus-public-data/main/latest.json"
with urllib.request.urlopen(url) as r:
    m = json.loads(r.read())

url = "https://raw.githubusercontent.com/daifulee/argus-public-data/main/argus_data.csv"
with urllib.request.urlopen(url) as r:
    df = pd.read_csv(io.StringIO(r.read().decode()))
```

## 업데이트 주기
평일 매일 16:00 KST — `daifulee/argus-briefing` Actions 자동 push
