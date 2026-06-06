#!/usr/bin/env python3
# gen_macro_zone_chart.py v4.1
# overlay.json 생성 담당 — comp_cur_y 계산 추가
import json, pathlib, csv, datetime, hashlib, sys

BASE_DIR  = pathlib.Path(__file__).parent
ZONE_JSON = BASE_DIR / "zone_data_v4.json"
TEMPLATE  = BASE_DIR / "template.html"
LIVE_CSV  = BASE_DIR / "argus_data.csv"
LONG_CSV  = BASE_DIR / "zone_long_trimmed.csv"
SITE_DIR  = BASE_DIR / "site"
OVERLAY   = SITE_DIR / "overlay.json"
INDEX     = SITE_DIR / "index.html"

def load_tail(path, n=15):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f): rows.append(row)
    return rows[-n:] if len(rows) >= n else rows

def get_val(rows, col):
    for row in reversed(rows):
        v = row.get(col, "").strip()
        if v:
            try: return float(v)
            except: pass
    return None

def get_as_of(rows):
    for row in reversed(rows):
        for k in ["Date", "DATE", "date"]:
            v = row.get(k, "").strip()
            if v: return v[:10]
    return datetime.date.today().isoformat()

def main():
    print("[gen_macro_zone_chart v4.1] 시작")
    SITE_DIR.mkdir(exist_ok=True)

    # template.html → site/index.html (변경 감지)
    if TEMPLATE.exists():
        t_sha = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()[:8]
        i_sha = hashlib.sha256(INDEX.read_bytes()).hexdigest()[:8] if INDEX.exists() else ""
        if t_sha != i_sha:
            INDEX.write_bytes(TEMPLATE.read_bytes())
            print(f"  index.html 갱신")

    if not ZONE_JSON.exists():
        print(f"ERROR: {ZONE_JSON} 없음"); sys.exit(1)
    with open(ZONE_JSON) as f:
        data = json.load(f)

    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")

    overlay_per = {}
    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro", "")
        xv = get_val(rows, xmc)

        # single cur_y
        ymc_s = P.get("single", {}).get("y_macro", "")
        yv_s = get_val(rows, ymc_s)

        # comp cur_y: top3 IC가중 합산 (근사)
        comp = P.get("comp", {})
        top3 = comp.get("top3", [])
        comp_yv = None
        if top3:
            try:
                # 각 매크로 live 값 가중 합산 (표준화 없이 근사)
                # 더 정확히는 BT_LONG 회귀 필요하나 live만으론 표준화 불가
                # → single_cur_y와 같은 방식으로 top3[0] 사용 (근사)
                comp_yv = get_val(rows, top3[0])
            except:
                pass

        # 궤적
        traj = P.get("traj", {})
        if traj and as_of not in traj.get("dates", []):
            traj = dict(traj)
            traj.setdefault("dates", []).append(as_of)
            traj.setdefault("x",  []).append(round(xv,3) if xv else (traj["x"][-1] if traj.get("x") else 0))
            last_ys = traj["ys"][-1] if traj.get("ys") else 0
            traj.setdefault("ys", []).append(round(yv_s,3) if yv_s else last_ys)
            last_yc = traj["yc"][-1] if traj.get("yc") else 0
            traj.setdefault("yc", []).append(last_yc)
            for k in ["dates","x","ys","yc"]:
                if k in traj: traj[k] = traj[k][-12:]

        overlay_per[tk] = {
            "cur_x":        round(xv,3) if xv else None,
            "cur_x_raw":    xv,
            "single_cur_y": round(yv_s,3) if yv_s else None,
            "comp_cur_y":   round(comp_yv,3) if comp_yv else None,
            "traj":         traj,
        }

    overlay = {"as_of": as_of, "per": overlay_per}
    ov_json = json.dumps(overlay, separators=(",",":"), ensure_ascii=False)
    OVERLAY.write_text(ov_json, encoding="utf-8")
    sha8 = hashlib.sha256(OVERLAY.read_bytes()).hexdigest()[:8]
    print(f"  overlay.json: {len(ov_json)} bytes / sha={sha8}")
    print(f"  index.html:   {INDEX.stat().st_size//1024}KB")
    print("[gen_macro_zone_chart v4.1] 완료")

if __name__ == "__main__":
    main()
