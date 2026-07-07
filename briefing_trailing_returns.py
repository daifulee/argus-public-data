#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGUS 브리핑 트레일링 성과 모듈 (S226+) — 모든 브리핑 경로 공용
─────────────────────────────────────────────────────────────────────────
run_prima4(df)["equity"] (정규화 100 시작 equity curve)에서 5종 산출:
  누적 월간(MTD) · 누적 연간(YTD) · 지난 3개월 · 지난 6개월 · 지난 1년.
asof 규칙: 목표일 이전 최근 거래일 종가 기준. 트레일링 5종은 윈도우 고정 →
데이터 시작점과 무관하게 robust (데이터 부족 시 None → 표기 'N/A').

브리핑 통합: prima_briefing.py(Discord) / argus_brief_html_v2.py(HTML) /
argus-briefing-runner(in-chat) 가 본 모듈 import하여 사용.
주석: 한국어. LIVE 파생값 → 표시 시 🌟 감싸기 권장.
"""

import pandas as pd

# 기간 라벨 (표시 순서)
PERIODS = [
    ("MTD", "누적 월간 (Month-To-Date)"),
    ("YTD", "누적 연간 (Year-To-Date)"),
    ("3M",  "지난 3개월"),
    ("6M",  "지난 6개월"),
    ("1Y",  "지난 1년"),
]


def compute_trailing_returns(equity):
    """equity curve(Series, DatetimeIndex) → {key: (수익률%, 기준거래일 or None)}.

    수익률 None = 데이터 부족(룩백이 equity 시작 이전).
    """
    equity = equity.sort_index()
    T = equity.index[-1]
    last = float(equity.iloc[-1])
    start = equity.index[0]

    def ret_from(base_date):
        s = equity.loc[:base_date]
        if len(s) == 0 or base_date < start:
            return (None, None)
        base = float(s.iloc[-1])
        bd = s.index[-1]
        return (((last / base - 1) * 100) if base > 0 else None, bd)

    res = {}
    res["MTD"] = ret_from(pd.Timestamp(T.year, T.month, 1) - pd.Timedelta(days=1))  # 전월말
    res["YTD"] = ret_from(pd.Timestamp(T.year - 1, 12, 31))                          # 전년말
    res["3M"]  = ret_from(T - pd.DateOffset(months=3))
    res["6M"]  = ret_from(T - pd.DateOffset(months=6))
    res["1Y"]  = ret_from(T - pd.DateOffset(months=12))
    res["_asof"] = T
    res["_inception_total"] = (last - 100.0)  # 정규화 100 가정 시 시작 이후 누적%
    res["_inception_date"] = start
    return res


def _fmt(v):
    return "N/A" if v is None else f"{v:+.2f}%"


def format_trailing_block(equity, style="markdown", star=True):
    """브리핑 출력용 트레일링 성과 블록 문자열.

    style: 'markdown'(in-chat) / 'discord'(Embed 텍스트) / 'plain'.
    star : True면 LIVE 파생값을 🌟 **값** 🌟 로 감쌈(Commander 표시 규약).
    """
    res = compute_trailing_returns(equity)
    asof = res["_asof"].date()

    def wrap(v):
        s = _fmt(v)
        if v is None:
            return s
        return f"🌟 **{s}** 🌟" if star else s

    if style == "markdown":
        L = [f"📈 **트레일링 성과** (run_prima4 equity, 기준 {asof})", "",
             "| 기간 | 수익률 |", "|:--|--:|"]
        for k, lab in PERIODS:
            L.append(f"| {lab} | {wrap(res[k][0])} |")
        L.append(f"| (참고) 누적 전체 | {wrap(res['_inception_total'])} |")
        return "\n".join(L)

    if style == "discord":
        # Embed field value (마크다운 표 미지원 → 정렬 텍스트)
        L = [f"📈 트레일링 성과 (기준 {asof})"]
        for k, lab in PERIODS:
            v = res[k][0]
            sv = _fmt(v)
            sv = f"**{sv}**" if (star and v is not None) else sv
            L.append(f"• {lab}: {sv}")
        L.append(f"• (참고) 누적 전체: **{_fmt(res['_inception_total'])}**")
        return "\n".join(L)

    # plain
    L = [f"트레일링 성과 (기준 {asof})"]
    for k, lab in PERIODS:
        bd = res[k][1]
        L.append(f"  {lab:26} {_fmt(res[k][0]):>10}  {bd.date() if bd else ''}")
    L.append(f"  {'(참고) 누적 전체':26} {_fmt(res['_inception_total']):>10}  {res['_inception_date'].date()}~")
    return "\n".join(L)


def format_trailing_html(equity, **kwargs):
    """HTML 트레일링 성과 표 — 다크 배경 밝은 팔레트(초록 #4ade80 / 빨강 #ff8a8a).
    브리핑 카드(card al / ct / td) 패턴 정합. equity = run_prima4 equity(정규화 100, DatetimeIndex).
    가드: None / 비-DatetimeIndex → 빈 문자열 반환(브리핑 무손상). **kwargs 흡수(호출부 호환)."""
    if equity is None:
        return ""
    eq = equity.sort_index()
    if not isinstance(eq.index, pd.DatetimeIndex):
        # df['Date'] 재인덱싱 누락 시(정수 인덱스) 표기 생략 — 잘못된 표 대신 무표시
        return ""
    res = compute_trailing_returns(eq)
    asof = res["_asof"].date()

    def _cell(v):
        if v is None:
            return '<td style="color:#64748b">N/A</td>'
        col = "#4ade80" if v >= 0 else "#ff8a8a"
        return f'<td style="color:{col};font-weight:700">{v:+.2f}%</td>'

    h = ('<div class="card al"><div class="ct">📈 트레일링 성과 '
         f'<span style="color:#64748b;font-size:10px">(run_prima4 equity · 기준 {asof})</span></div>'
         '<div class="td"><table>\n'
         '<tr><th>기간</th><th>수익률</th></tr>\n')
    for k, lab in PERIODS:
        h += f'<tr><td>{lab}</td>{_cell(res[k][0])}</tr>\n'
    h += (f'<tr style="color:#475569"><td>(참고) 누적 전체</td>'
          f'{_cell(res["_inception_total"])}</tr>\n')
    h += '</table></div></div>\n'
    return h



if __name__ == "__main__":
    # 단독 실행 데모: 엔진 LIVE equity로 산출
    import os, sys, importlib.util
    DATA = os.environ.get("ARGUS_DATA", "/mnt/project/argus_data.csv")
    ENG = os.environ.get("ARGUS_ENGINE", "/mnt/project/PRIMA2_v0_5_5_NFCI_PD_CQQQ_LIVE.py")
    df = pd.read_csv(DATA, index_col=0, parse_dates=True).sort_index()
    devnull = os.open(os.devnull, os.O_WRONLY); so = os.dup(1); se = os.dup(2)
    try:
        os.dup2(devnull, 1); os.dup2(devnull, 2)
        spec = importlib.util.spec_from_file_location("prima_engine", ENG)
        mod = importlib.util.module_from_spec(spec); sys.modules["prima_engine"] = mod
        try:
            spec.loader.exec_module(mod)
        except RuntimeError:
            pass
        result = mod.run_prima4(df)
    finally:
        os.dup2(so, 1); os.dup2(se, 2); os.close(devnull); os.close(so); os.close(se)
    print(format_trailing_block(result["equity"], style="plain", star=False))
    print()
    print(format_trailing_block(result["equity"], style="markdown"))
    print()
    print(format_trailing_html(result["equity"])[:200], "...")
