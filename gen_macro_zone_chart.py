#!/usr/bin/env python3
# gen_macro_zone_chart.py v4.2
# site/index.html 복사를 최우선으로 처리
# argus_data.csv만으로 작동 (zone_long_trimmed.csv 선택적)
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
        for row in csv.DictReader(f):
            rows.append(row)
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
    print("[gen_macro_zone_chart v4.2] 시작")
    
    # ── 1. site/ 디렉토리 + index.html 최우선 처리 ──────────────
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    
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
    
    # ── 2. zone_data_v4.json 로드 ────────────────────────────────
    if not ZONE_JSON.exists():
        print(f"ERROR: zone_data_v4.json 없음"); sys.exit(1)
    with open(ZONE_JSON) as f:
        data = json.load(f)
    
    # ── 3. live CSV 로드 ─────────────────────────────────────────
    live_src = None
    for candidate in [LIVE_CSV, LONG_CSV]:
        if candidate.exists():
            live_src = candidate
            break
    if live_src is None:
        print("ERROR: argus_data.csv 없음"); sys.exit(1)
    
    print(f"  live 소스: {live_src.name}")
    rows = load_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")
    
    # ── 4. overlay 생성 ──────────────────────────────────────────
    overlay_per = {}
    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro", "")
        xv = get_val(rows, xmc)
        
        ymc_s = P.get("single", {}).get("y_macro", "")
        yv_s = get_val(rows, ymc_s)
        
        # comp_cur_y: top3 첫 매크로 근사값
        top3 = P.get("comp", {}).get("top3", [])
        comp_yv = get_val(rows, top3[0]) if top3 else None
        
        # 궤적 갱신
        traj = dict(P.get("traj", {}))
        if traj and as_of not in traj.get("dates", []):
            traj.setdefault("dates", []).append(as_of)
            traj.setdefault("x", []).append(round(xv, 3) if xv else (traj["x"][-1] if traj.get("x") else 0))
            last_ys = traj["ys"][-1] if traj.get("ys") else 0
            traj.setdefault("ys", []).append(round(yv_s, 3) if yv_s else last_ys)
            last_yc = traj["yc"][-1] if traj.get("yc") else last_ys
            traj.setdefault("yc", []).append(last_yc)
            for k in ["dates", "x", "ys", "yc"]:
                if k in traj: traj[k] = traj[k][-12:]
        
        overlay_per[tk] = {
            "cur_x":        round(xv, 3) if xv is not None else None,
            "cur_x_raw":    xv,
            "single_cur_y": round(yv_s, 3) if yv_s is not None else None,
            "comp_cur_y":   round(comp_yv, 3) if comp_yv is not None else None,
            "traj":         traj,
        }
    
    overlay = {"as_of": as_of, "per": overlay_per}
    ov_json = json.dumps(overlay, separators=(",", ":"), ensure_ascii=False)
    OVERLAY.write_text(ov_json, encoding="utf-8")
    sha8 = hashlib.sha256(OVERLAY.read_bytes()).hexdigest()[:8]
    print(f"  overlay.json: {len(ov_json)//1024}KB / sha={sha8}")
    print(f"  index.html:   {INDEX.stat().st_size//1024}KB")
    print(f"  site/ 파일: {[f.name for f in SITE_DIR.iterdir()]}")
    print("[gen_macro_zone_chart v4.2] 완료")

if __name__ == "__main__":
    main()
