#!/usr/bin/env python3
# gen_macro_zone_chart.py v4.3
# comp_cur_y: comp_params 회귀계수로 정확 계산
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
        for k in ["Date","DATE","date"]:
            v = row.get(k,"").strip()
            if v: return v[:10]
    return datetime.date.today().isoformat()

def calc_comp_cur_y(x_val, live_rows, comp_params):
    """comp_params 회귀계수로 comp_cur_y 정확 계산"""
    if not comp_params or x_val is None:
        return None
    try:
        total = 0.0
        for p in comp_params:
            mc_val = get_val(live_rows, p["mc"])
            if mc_val is None:
                return None
            # 잔차 = (y - slope*x - intercept) / std
            resid = (mc_val - (p["slope"] * x_val + p["intercept"])) / p["std"]
            # IC 부호 적용 후 가중
            total += resid * (1 if p["ic"] > 0 else -1) * p["w"]
        return round(total, 3)
    except:
        return None

def main():
    print("[gen_macro_zone_chart v4.3] 시작")
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    # index.html 복사 (최우선)
    if TEMPLATE.exists():
        t_bytes = TEMPLATE.read_bytes()
        t_sha = hashlib.sha256(t_bytes).hexdigest()[:8]
        i_sha = hashlib.sha256(INDEX.read_bytes()).hexdigest()[:8] if INDEX.exists() else ""
        if t_sha != i_sha:
            INDEX.write_bytes(t_bytes)
            print(f"  index.html 갱신 ({len(t_bytes)//1024}KB)")
        else:
            print(f"  index.html 최신 (변경 없음)")
    else:
        print("ERROR: template.html 없음"); sys.exit(1)

    if not ZONE_JSON.exists():
        print(f"ERROR: zone_data_v4.json 없음"); sys.exit(1)
    with open(ZONE_JSON) as f:
        data = json.load(f)

    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")

    overlay_per = {}
    comp_ok, comp_fail = 0, 0
    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro","")
        xv = get_val(rows, xmc)

        # single cur_y
        ymc_s = P.get("single",{}).get("y_macro","")
        yv_s = get_val(rows, ymc_s)

        # comp cur_y: 회귀계수로 정확 계산
        comp = P.get("comp",{})
        comp_params = comp.get("comp_params",[])
        comp_yv = calc_comp_cur_y(xv, rows, comp_params)
        if comp_params:
            if comp_yv is not None: comp_ok += 1
            else: comp_fail += 1; comp_yv = P["comp"].get("cur_y")  # static 폴백

        # 궤적 갱신
        traj = dict(P.get("traj",{}))
        if traj and as_of not in traj.get("dates",[]):
            traj.setdefault("dates",[]).append(as_of)
            traj.setdefault("x",[]).append(round(xv,3) if xv else (traj["x"][-1] if traj.get("x") else 0))
            last_ys = traj["ys"][-1] if traj.get("ys") else 0
            traj.setdefault("ys",[]).append(round(yv_s,3) if yv_s else last_ys)
            last_yc = traj["yc"][-1] if traj.get("yc") else last_ys
            traj.setdefault("yc",[]).append(round(comp_yv,3) if comp_yv else last_yc)
            for k in ["dates","x","ys","yc"]:
                if k in traj: traj[k] = traj[k][-12:]

        overlay_per[tk] = {
            "cur_x":        round(xv,3) if xv is not None else None,
            "cur_x_raw":    xv,
            "single_cur_y": round(yv_s,3) if yv_s is not None else None,
            "comp_cur_y":   comp_yv,
            "traj":         traj,
        }

    print(f"  comp_cur_y: 정확계산 {comp_ok}개 / 폴백 {comp_fail}개")
    overlay = {"as_of": as_of, "per": overlay_per}
    ov_json = json.dumps(overlay, separators=(",",":"), ensure_ascii=False)
    OVERLAY.write_text(ov_json, encoding="utf-8")
    sha8 = hashlib.sha256(OVERLAY.read_bytes()).hexdigest()[:8]
    print(f"  overlay.json: {len(ov_json)//1024}KB / sha={sha8}")
    print(f"  site/ 파일: {[f.name for f in SITE_DIR.iterdir()]}")
    print("[gen_macro_zone_chart v4.3] 완료")

if __name__ == "__main__":
    main()
