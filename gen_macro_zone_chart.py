#!/usr/bin/env python3
"""
gen_macro_zone_chart.py v3 — ARGUS 매크로 수익구간 차트 자동 생성기
매일 실행: live argus_data.csv → cur_x/cur_y/traj 갱신 → site/index.html
"""
import json, pathlib, csv, datetime, hashlib, sys, re

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATE  = BASE_DIR / "template.html"
LIVE_CSV  = BASE_DIR / "argus_data.csv"
LONG_CSV  = BASE_DIR / "zone_long_trimmed.csv"
SITE_DIR  = BASE_DIR / "site"
OUT_HTML  = SITE_DIR / "index.html"

def load_csv_tail(path, n=15):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows[-n:] if len(rows) >= n else rows

def get_val(rows, col):
    for row in reversed(rows):
        v = row.get(col,'').strip()
        if v:
            try: return float(v)
            except: pass
    return None

def get_as_of(rows):
    for row in reversed(rows):
        for k in ['Date','DATE','date']:
            v = row.get(k,'').strip()
            if v: return v[:10]
    return datetime.date.today().isoformat()

def main():
    print("[gen_macro_zone_chart v3] 시작")
    if not TEMPLATE.exists():
        print(f"ERROR: {TEMPLATE} 없음"); sys.exit(1)

    tmpl = TEMPLATE.read_text(encoding='utf-8')

    # DATA 블록 추출
    m = re.search(r'const DATA=(\{.*?\});', tmpl, re.DOTALL)
    if not m:
        print("ERROR: DATA 블록 미발견"); sys.exit(1)

    data = json.loads(m.group(1))
    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_csv_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")

    # 티커별 cur_x/cur_y/traj 갱신
    for tk, P in data['per'].items():
        xmc = P['x_macro']
        xv = get_val(rows, xmc)
        if xv is not None:
            P['cur_x'] = xv
            P['cur_x_raw'] = xv

        # single cur_y
        if 'single' in P:
            ymc = P['single'].get('y_macro','')
            yv = get_val(rows, ymc)
            if yv is not None:
                P['single']['cur_y'] = yv
                P['single']['cur_y_raw'] = yv

        # traj 갱신 (x는 실측, ys/yc는 근사값 유지)
        if 'traj' in P:
            traj = P['traj']
            traj['dates'].append(as_of)
            if xv is not None:
                traj['x'].append(round(xv,3))
            else:
                traj['x'].append(traj['x'][-1] if traj['x'] else 0)
            # ys/yc: 마지막값 유지 (근사)
            if 'ys' in traj and traj['ys']:
                ymc = P['single'].get('y_macro','')
                yv_s = get_val(rows, ymc)
                traj['ys'].append(round(yv_s,3) if yv_s else traj['ys'][-1])
            if 'yc' in traj and traj['yc']:
                traj['yc'].append(traj['yc'][-1])
            # 최근 12개만
            for key in ['dates','x','ys','yc']:
                if key in traj:
                    traj[key] = traj[key][-12:]

    # DATA 교체
    new_data_json = json.dumps(data, separators=(',',':'))
    out_html = re.sub(
        r'const DATA=\{.*?\};',
        f'const DATA={new_data_json};',
        tmpl, flags=re.DOTALL
    )

    # as_of를 /**DATA**/ 슬롯에 주입 (있으면)
    out_html = out_html.replace('/**DATA**/', f'/* as_of:{as_of} */')

    SITE_DIR.mkdir(exist_ok=True)
    OUT_HTML.write_text(out_html, encoding='utf-8')
    sha8 = hashlib.sha256(OUT_HTML.read_bytes()).hexdigest()[:8]
    print(f"  출력: {OUT_HTML} ({OUT_HTML.stat().st_size//1024}KB / sha={sha8})")
    print("[gen_macro_zone_chart v3] 완료")

if __name__ == '__main__':
    main()
