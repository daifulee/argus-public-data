#!/usr/bin/env python3
"""
gen_macro_zone_chart.py — ARGUS 매크로 수익구간 차트 자동 생성기
GitHub Actions에서 매일 실행: live argus_data.csv → site/index.html
"""
import json, pathlib, csv, datetime, hashlib, sys

# ── 경로 설정 ──────────────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent
ZONE_BASE = BASE_DIR / "zone_base.json"
ZONE_AXIS = BASE_DIR / "zone_axis.json"
LONG_CSV  = BASE_DIR / "zone_long_trimmed.csv"
TEMPLATE  = BASE_DIR / "template.html"
LIVE_CSV  = BASE_DIR / "argus_data.csv"
SITE_DIR  = BASE_DIR / "site"
OUT_HTML  = SITE_DIR / "index.html"

def load_csv_tail(path, n=15):
    """CSV 마지막 n행 읽기 (매크로 컬럼만)"""
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows[-n:] if len(rows) >= n else rows

def get_live_value(rows, col):
    """마지막 유효값 반환 (float)"""
    for row in reversed(rows):
        v = row.get(col, '').strip()
        if v:
            try:
                return float(v)
            except ValueError:
                pass
    return None

def get_as_of(rows):
    """날짜 컬럼 탐색 → as_of 문자열"""
    date_keys = ['Date','DATE','date','timestamp','as_of']
    for row in reversed(rows):
        for k in date_keys:
            v = row.get(k, '').strip()
            if v:
                return v[:10]
    return datetime.date.today().isoformat()

def build_trajectory(rows, axis_map):
    """10영업일 궤적 데이터 구성 {ticker: [(x,y,date), ...]}"""
    traj = {}
    for tk, ax in axis_map.items():
        xmc = ax['x']
        ymc = ax.get('y') or xmc
        pts = []
        for row in rows[-12:]:
            d = row.get('Date') or row.get('date') or ''
            xv = row.get(xmc, '')
            yv = row.get(ymc, '')
            try:
                pts.append({'x': float(xv), 'y': float(yv), 'd': d[:10]})
            except (ValueError, TypeError):
                pass
        traj[tk] = pts
    return traj

def main():
    print("[gen_macro_zone_chart] 시작")
    
    # ── 파일 로드 ──────────────────────────────────────────────────
    if not ZONE_BASE.exists():
        print(f"ERROR: {ZONE_BASE} 없음"); sys.exit(1)
    if not ZONE_AXIS.exists():
        print(f"ERROR: {ZONE_AXIS} 없음"); sys.exit(1)
    if not TEMPLATE.exists():
        print(f"ERROR: {TEMPLATE} 없음"); sys.exit(1)
    
    with open(ZONE_BASE) as f:
        zone_data = json.load(f)
    with open(ZONE_AXIS) as f:
        axis_map = json.load(f)
    
    # live 데이터 (argus_data.csv 우선, 없으면 zone_long_trimmed.csv fallback)
    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_csv_tail(live_src, n=15)
    
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")
    
    # 현재 좌표 (마지막 유효값)
    current = {}
    for tk, ax in axis_map.items():
        xv = get_live_value(rows, ax['x'])
        yv = get_live_value(rows, ax.get('y') or ax['x'])
        if xv is not None:
            current[tk] = {'x': xv, 'y': yv, 'as_of': as_of}
    
    # 궤적
    traj = build_trajectory(rows, axis_map)
    
    # ── template.html DATA 플레이스홀더 치환 ─────────────────────
    tmpl = TEMPLATE.read_text(encoding='utf-8')
    
    overlay_json = json.dumps({
        'as_of': as_of,
        'current': current,
        'trajectory': traj,
    }, separators=(',', ':'))
    
    out_html = tmpl.replace('/**DATA**/', f'const OVERLAY={overlay_json};')
    
    SITE_DIR.mkdir(exist_ok=True)
    OUT_HTML.write_text(out_html, encoding='utf-8')
    
    sha8 = hashlib.sha256(OUT_HTML.read_bytes()).hexdigest()[:8]
    print(f"  출력: {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes / sha={sha8})")
    print("[gen_macro_zone_chart] 완료")

if __name__ == '__main__':
    main()
