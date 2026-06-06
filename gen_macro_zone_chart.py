#!/usr/bin/env python3
# gen_macro_zone_chart.py v4
# overlay.json 생성만 담당 (template.html 불변)
# 매일: live argus_data.csv → overlay.json 갱신
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
    print("[gen_macro_zone_chart v4] 시작")
    SITE_DIR.mkdir(exist_ok=True)

    # template.html → site/index.html 복사 (Pages 배포용, 없을 때만)
    if not INDEX.exists() and TEMPLATE.exists():
        INDEX.write_bytes(TEMPLATE.read_bytes())
        print(f"  index.html 초기 복사 완료")
    elif TEMPLATE.exists():
        # template.html이 갱신됐으면 재복사
        t_sha = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()[:8]
        i_sha = hashlib.sha256(INDEX.read_bytes()).hexdigest()[:8] if INDEX.exists() else ""
        if t_sha != i_sha:
            INDEX.write_bytes(TEMPLATE.read_bytes())
            print(f"  index.html 갱신 (template 변경 감지)")

    # zone_data_v4.json 로드
    if not ZONE_JSON.exists():
        print(f"ERROR: {ZONE_JSON} 없음"); sys.exit(1)
    with open(ZONE_JSON) as f:
        data = json.load(f)

    # live CSV
    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")

    # overlay 생성
    overlay_per = {}
    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro", "")
        xv = get_val(rows, xmc)

        ymc_s = P.get("single", {}).get("y_macro", "")
        yv_s = get_val(rows, ymc_s)

        # 궤적 갱신
        traj = P.get("traj", {})
        if as_of not in traj.get("dates", []):
            traj = dict(traj)  # 복사
            traj.setdefault("dates", []).append(as_of)
            traj.setdefault("x",  []).append(round(xv,3) if xv else (traj["x"][-1] if traj.get("x") else 0))
            last_ys = traj["ys"][-1] if traj.get("ys") else 0
            traj.setdefault("ys", []).append(round(yv_s,3) if yv_s else last_ys)
            last_yc = traj["yc"][-1] if traj.get("yc") else 0
            traj.setdefault("yc", []).append(last_yc)
            for k in ["dates","x","ys","yc"]:
                if k in traj: traj[k] = traj[k][-12:]

        overlay_per[tk] = {
            "cur_x":        round(xv, 3) if xv else None,
            "cur_x_raw":    xv,
            "single_cur_y": round(yv_s, 3) if yv_s else None,
            "comp_cur_y":   None,  # comp Y는 BT_LONG 없으면 근사 유지
            "traj":         traj,
        }

    overlay = {"as_of": as_of, "per": overlay_per}
    ov_json = json.dumps(overlay, separators=(",",":"), ensure_ascii=False)
    OVERLAY.write_text(ov_json, encoding="utf-8")
    sha8 = hashlib.sha256(OVERLAY.read_bytes()).hexdigest()[:8]
    print(f"  overlay.json: {len(ov_json)} bytes / sha={sha8}")
    print(f"  index.html:   {INDEX.stat().st_size//1024}KB")
    print("[gen_macro_zone_chart v4] 완료")

if __name__ == "__main__":
    main()
