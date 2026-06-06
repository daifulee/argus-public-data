#!/usr/bin/env python3
# gen_macro_zone_chart.py v3.1
# v3.1: re.sub 제거 (JSON unicode escape regex 오파싱 버그 수정)
import json, pathlib, csv, datetime, hashlib, sys

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATE  = BASE_DIR / "template.html"
LIVE_CSV  = BASE_DIR / "argus_data.csv"
LONG_CSV  = BASE_DIR / "zone_long_trimmed.csv"
SITE_DIR  = BASE_DIR / "site"
OUT_HTML  = SITE_DIR / "index.html"

def load_csv_tail(path, n=15):
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

def replace_data_block(tmpl, new_json):
    # re.sub 금지 — JSON unicode escape 오파싱
    marker = "const DATA="
    idx_s = tmpl.find(marker)
    if idx_s < 0: raise ValueError("const DATA= 미발견")
    idx_e = -1
    for em in ["\nconst GROUPS=", "\nlet cur=", "\nfunction "]:
        p = tmpl.find(em, idx_s)
        if p > 0: idx_e = p; break
    if idx_e < 0: raise ValueError("DATA 블록 끝 미발견")
    return tmpl[:idx_s] + "const DATA=" + new_json + tmpl[idx_e:]

def main():
    print("[gen_macro_zone_chart v3.1] 시작")
    if not TEMPLATE.exists():
        print("ERROR: template.html 없음"); sys.exit(1)

    tmpl = TEMPLATE.read_text(encoding="utf-8")
    marker = "const DATA="
    idx_s = tmpl.find(marker)
    idx_e = -1
    for em in ["\nconst GROUPS=", "\nlet cur=", "\nfunction "]:
        p = tmpl.find(em, idx_s)
        if p > 0: idx_e = p; break
    if idx_s < 0 or idx_e < 0:
        print("ERROR: DATA 블록 경계 미발견"); sys.exit(1)

    raw_json = tmpl[idx_s + len(marker):idx_e].rstrip().rstrip(";")
    data = json.loads(raw_json)

    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_csv_tail(live_src, n=15)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of}")

    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro", "")
        xv = get_val(rows, xmc)
        if xv is not None:
            P["cur_x"] = xv; P["cur_x_raw"] = xv
        if "single" in P:
            ymc = P["single"].get("y_macro", "")
            yv = get_val(rows, ymc)
            if yv is not None:
                P["single"]["cur_y"] = yv; P["single"]["cur_y_raw"] = yv
        if "traj" in P:
            traj = P["traj"]
            if as_of not in traj.get("dates", []):
                traj.setdefault("dates", []).append(as_of)
                traj.setdefault("x", []).append(round(xv,3) if xv else (traj["x"][-1] if traj.get("x") else 0))
                ymc2 = P.get("single", {}).get("y_macro", "")
                yv2 = get_val(rows, ymc2)
                last_ys = traj["ys"][-1] if traj.get("ys") else 0
                traj.setdefault("ys", []).append(round(yv2,3) if yv2 else last_ys)
                last_yc = traj["yc"][-1] if traj.get("yc") else 0
                traj.setdefault("yc", []).append(last_yc)
                for k in ["dates","x","ys","yc"]:
                    if k in traj: traj[k] = traj[k][-12:]

    new_json = json.dumps(data, separators=(",",":"), ensure_ascii=False)
    out_html = replace_data_block(tmpl, new_json)
    SITE_DIR.mkdir(exist_ok=True)
    OUT_HTML.write_text(out_html, encoding="utf-8")
    sha8 = hashlib.sha256(OUT_HTML.read_bytes()).hexdigest()[:8]
    print(f"  출력: {OUT_HTML} ({OUT_HTML.stat().st_size//1024}KB / sha={sha8})")
    print("[gen_macro_zone_chart v3.1] 완료")

if __name__ == "__main__":
    main()
