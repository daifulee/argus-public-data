# 🦅 ARGUS Public Data

ARGUS PRIMA 시스템 전용 공개 데이터 레포지토리.

**마지막 업데이트**: 2026-05-14 09:25 UTC
**누적 데이터**: 354행 (헤더 포함)

## 파일

| 파일 | 설명 |
|:---|:---|
| `argus_data.csv` | ETF 20종 OHLCV + 매크로 전체 누적 |
| `latest.json` | 최신 1행 JSON (빠른 조회) |

## Claude fetch 방법 (bash_tool)

```python
import urllib.request, json, io, pandas as pd

# 최신 지표 (빠름)
url = "https://raw.githubusercontent.com/daifulee/argus-public-data/main/latest.json"
with urllib.request.urlopen(url) as r:
    m = json.loads(r.read())
# WTI, TNX, VIX 등 즉시 사용 가능

# 전체 히스토리 (모멘텀 계산용)
url = "https://raw.githubusercontent.com/daifulee/argus-public-data/main/argus_data.csv"
with urllib.request.urlopen(url) as r:
    df = pd.read_csv(io.StringIO(r.read().decode()))
```

## 업데이트 주기
평일 매일 16:00 KST — `daifulee/argus-briefing` Actions 자동 push

## archive/ 폴더 (2026-05-14 신설)

ARGUS 시스템의 과거 SSOT 버전, 통합 완료된 LOG, 폐기된 candidate 의사결정 등을 audit + 학습 자료로 보관하는 영구 archive입니다. LIVE 운영에는 사용되지 않습니다.

상세: [archive/README.md](archive/README.md)
