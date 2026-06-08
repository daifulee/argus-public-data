#!/usr/bin/env python3
# gen_macro_zone_chart.py v5.4
# 궤적·cur_y 모두 LIVE data + zparams 고정 z-score로 통일 (궤적 마지막=현재 보장)
# zone_data_v4.json → template.html DATA 주입 (축 변경 자동 반영)
# 신규 파생 지표 (GSR/MOVE_VIX/VIX_MA60_RATIO) 일간 궤적 대응
# traj 60영업일 = LIVE 데이터에서 매 실행 재구축
import json, pathlib, csv, datetime, hashlib, sys

BASE_DIR  = pathlib.Path(__file__).parent
ZONE_JSON = BASE_DIR / "zone_data_v4.json"
TEMPLATE  = BASE_DIR / "template.html"
LIVE_CSV  = BASE_DIR / "argus_data.csv"
LONG_CSV  = BASE_DIR / "zone_long_trimmed.csv"
SITE_DIR  = BASE_DIR / "site"
OVERLAY   = SITE_DIR / "overlay.json"
INDEX     = SITE_DIR / "index.html"

def load_tail(path, n=65):
    """최근 n행 로드 (파생 지표 rolling 계산용 65행 기본)"""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f): rows.append(row)
    return rows[-n:] if len(rows) >= n else rows

def _float(v):
    """문자열 → float 안전 변환"""
    if v is None: return None
    try: return float(str(v).strip())
    except: return None

def enrich_derived(rows):
    """파생 지표를 각 row에 주입: GSR, MOVE_VIX, VIX_MA60_RATIO"""
    # VIX 60일 이동평균 계산 (VIX_MA60_RATIO용)
    vix_vals = [_float(r.get("VIX")) for r in rows]
    vix_ma60 = [None] * len(rows)
    for i in range(len(rows)):
        window = [v for v in vix_vals[max(0,i-59):i+1] if v is not None]
        if len(window) >= 20:  # 최소 20일
            vix_ma60[i] = sum(window) / len(window)

    for i, row in enumerate(rows):
        # GSR = GLD / SLV (종가 비율)
        gld = _float(row.get("GLD_Close"))
        slv = _float(row.get("SLV_Close"))
        if gld and slv and slv > 0:
            row["GSR"] = str(round(gld / slv, 4))

        # MOVE_VIX = MOVE / VIX
        move = _float(row.get("MOVE"))
        vix = _float(row.get("VIX"))
        if move is not None and vix and vix > 0:
            row["MOVE_VIX"] = str(round(move / vix, 4))

        # VIX_MA60_RATIO = VIX / VIX_60d_MA
        if vix is not None and vix_ma60[i] and vix_ma60[i] > 0:
            row["VIX_MA60_RATIO"] = str(round(vix / vix_ma60[i], 4))
    
    return rows

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

def calc_comp_resid(get_macro, comp_params):
    """comp_params 잔차회귀로 comp_y 계산 (X 상관 제거).
    get_macro(mc)는 매크로 값 반환(None 가능). x값은 'x_macro' 키로 전달."""
    if not comp_params:
        return None
    x_val = get_macro("__x__")
    if x_val is None:
        return None
    zvals = []
    for p in comp_params:
        v = get_macro(p["mc"])
        if v is None or p["rstd"] == 0:
            continue
        resid = (v - (p["slope"] * x_val + p["intercept"])) / p["rstd"]
        zvals.append(p["dir"] * resid)
    if not zvals:
        return None
    return round(sum(zvals) / len(zvals), 3)

def main():
    print("[gen_macro_zone_chart v5.4] 시작")
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE.exists():
        print("ERROR: template.html 없음"); sys.exit(1)
    if not ZONE_JSON.exists():
        print(f"ERROR: zone_data_v4.json 없음"); sys.exit(1)

    # zone_data 로드 (index.html DATA 주입 + overlay 생성 공용)
    with open(ZONE_JSON) as f:
        data = json.load(f)

    # index.html 생성: template.html의 /**DATA**/ 마커 뒤 const DATA={...}를 zone_data로 교체
    t_text = TEMPLATE.read_text(encoding="utf-8")
    marker = "/**DATA**/"
    if marker in t_text:
        mi = t_text.index(marker)
        ds = t_text.index("const DATA=", mi)
        # 중괄호 매칭으로 DATA 끝 찾기
        brace_start = t_text.index("{", ds)
        depth, i = 0, brace_start
        for i in range(brace_start, len(t_text)):
            if t_text[i] == "{": depth += 1
            elif t_text[i] == "}": depth -= 1
            if depth == 0: break
        data_end = i + 1
        # zone_data JSON 주입
        data_json = json.dumps(data, ensure_ascii=False, separators=(",",":"))
        new_text = t_text[:ds] + "const DATA=" + data_json + t_text[data_end:]
        INDEX.write_text(new_text, encoding="utf-8")
        print(f"  index.html 생성 (DATA 주입 {len(data_json)//1024}KB, 총 {len(new_text)//1024}KB)")
    else:
        # 마커 없으면 단순 복사 (폴백)
        INDEX.write_bytes(TEMPLATE.read_bytes())
        print(f"  index.html 복사 (DATA 마커 없음, 단순 복사)")

    live_src = LIVE_CSV if LIVE_CSV.exists() else LONG_CSV
    print(f"  live 소스: {live_src.name}")
    rows = load_tail(live_src, n=65)
    rows = enrich_derived(rows)  # 파생 지표 주입 (GSR/MOVE_VIX/VIX_MA60_RATIO)
    as_of = get_as_of(rows)
    print(f"  as_of: {as_of} ({len(rows)}행 로드, 파생 3종 주입)")

    # ── 각 row의 파생값 접근 헬퍼 ──
    def row_macro(row, mc):
        v = row.get(mc, "")
        try: return float(str(v).strip())
        except: return None

    overlay_per = {}
    comp_cnt = 0
    for tk, P in data.get("per", {}).items():
        xmc = P.get("x_macro","")
        ymc_s = P.get("single",{}).get("y_macro","")
        comp = P.get("comp",{})
        comp_params = comp.get("comp_params",[])
        chosen = P.get("chosen","single")

        # ── 궤적: LIVE 60행에서 전체 재구축 (항상 live data만) ──
        traj = {"dates":[], "x":[], "ys":[], "yc":[]}
        for row in rows:
            dt = ""
            for k in ["Date","DATE","date"]:
                if row.get(k,"").strip(): dt = row[k].strip()[:10]; break
            xv = row_macro(row, xmc)
            yv = row_macro(row, ymc_s)
            if xv is None: continue
            if yv is None: yv = traj["ys"][-1] if traj["ys"] else 0.0
            # comp yc: comp_params 잔차회귀 (x값은 __x__ 키로 전달)
            yc = None
            if chosen == "comp" and comp_params:
                def gm(mc, _row=row, _xv=xv):
                    if mc == "__x__": return _xv
                    return row_macro(_row, mc)
                yc = calc_comp_resid(gm, comp_params)
            if yc is None:
                yc = traj["yc"][-1] if traj["yc"] else round(yv,3)
            traj["dates"].append(dt)
            traj["x"].append(round(xv,3))
            traj["ys"].append(round(yv,3))
            traj["yc"].append(round(yc,3))
        for k in ["dates","x","ys","yc"]:
            traj[k] = traj[k][-60:]

        # ── cur = 궤적 마지막 (동일 데이터 → 항상 연결) ──
        cur_x = traj["x"][-1] if traj["x"] else None
        cur_ys = traj["ys"][-1] if traj["ys"] else None
        comp_yv = traj["yc"][-1] if (chosen=="comp" and traj["yc"]) else None
        if comp_yv is not None: comp_cnt += 1

        overlay_per[tk] = {
            "cur_x":        cur_x,
            "cur_x_raw":    cur_x,
            "single_cur_y": cur_ys,
            "comp_cur_y":   comp_yv,
            "traj":         traj,
            "x_macro":        xmc,
            "single_y_macro": ymc_s,
            "comp_y_macro":   P.get("comp", {}).get("y_macro"),
        }

    print(f"  comp 잔차회귀 계산: {comp_cnt}개 (궤적 마지막=현재 보장)")
    overlay = {"as_of": as_of, "per": overlay_per}
    ov_json = json.dumps(overlay, separators=(",",":"), ensure_ascii=False)
    OVERLAY.write_text(ov_json, encoding="utf-8")
    sha8 = hashlib.sha256(OVERLAY.read_bytes()).hexdigest()[:8]
    print(f"  overlay.json: {len(ov_json)//1024}KB / sha={sha8}")

    # ── zone_data_v4.json에 갱신된 traj 반영 (매일 누적) ──
    for tk, ov in overlay_per.items():
        if tk in data.get("per", {}) and "traj" in ov:
            data["per"][tk]["traj"] = ov["traj"]
    data["traj_range"] = f"{as_of}"
    data["as_of"] = as_of
    zd_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    ZONE_JSON.write_text(zd_json, encoding="utf-8")
    zd_sha = hashlib.sha256(ZONE_JSON.read_bytes()).hexdigest()[:8]
    print(f"  zone_data_v4.json 갱신 ({len(zd_json)//1024}KB / sha={zd_sha})")

    print(f"  site/ 파일: {[f.name for f in SITE_DIR.iterdir()]}")
    print("[gen_macro_zone_chart v5.4] 완료")

if __name__ == "__main__":
    main()
