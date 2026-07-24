"""공개 트랙레코드 페이지 (Streamlit Cloud 배포용).

이 앱은 실제 추천 조합·모델 가중치 등 유료 상품 데이터는 전혀 담지 않는다.
data/Track_Record.xlsx(적중률·ROI·잔고 추이 집계만)만 읽어서 보여주는 신뢰용 공개 페이지다.
데이터는 본 저장소(app_public 전용, 비공개 상품 저장소와 분리됨)에 주기적으로 동기화된다.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data" / "Track_Record.xlsx"
KST = timezone(timedelta(hours=9))

st.set_page_config(page_title="토토분석 트랙레코드", page_icon="📊", layout="wide")


@st.cache_data
def load_sheets(path: Path, mtime: float) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=None)


def format_pct(value: object) -> str:
    return value if isinstance(value, str) else "N/A"


st.title("📊 토토분석 실계좌 트랙레코드")
st.caption("모델이 추천한 조합을 실제로 베팅한 결과를 그대로 공개합니다. 승패를 가리지 않고 전부 반영된 수치입니다.")
st.info("이 페이지는 통계적 분석 결과의 참고용 공개 자료이며, 베팅/투자 권유가 아닙니다.", icon="ℹ️")
st.markdown('📬 <a href="subscribe" target="_self">프리미엄 리포트 구독 신청하기 →</a>', unsafe_allow_html=True)

if not DATA_PATH.exists():
    st.warning("아직 공개된 트랙레코드 데이터가 없습니다. 곧 업데이트됩니다.")
    st.stop()

sheets = load_sheets(DATA_PATH, DATA_PATH.stat().st_mtime)
summary_df = sheets["전체요약"].set_index("지표")["값"]
daily_df = sheets["일자별"]
league_df = sheets["리그별"]
balance_df = sheets["잔고추이"]

updated_at = datetime.fromtimestamp(DATA_PATH.stat().st_mtime, tz=KST).strftime("%Y-%m-%d %H:%M KST")
st.caption(f"마지막 갱신: {updated_at}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("적중률", summary_df.get("적중률", "N/A"))
col2.metric("누적 순수익", summary_df.get("누적 순수익", "N/A"))
col3.metric("베팅 대비 수익률(ROI)", summary_df.get("베팅 대비 수익률(ROI)", "N/A"))
col4.metric("초기 자본 대비 누적 수익률", summary_df.get("초기 자본 대비 누적 수익률", "N/A"))

st.subheader("잔고 추이")
if not balance_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=balance_df["날짜"], y=balance_df["최종 잔고"], mode="lines+markers", name="잔고"))
    fig.update_layout(yaxis_title="잔고(원)", xaxis_title="날짜", height=360)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("아직 잔고 추이 데이터가 없습니다.")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("리그별 성과")
    st.dataframe(league_df, hide_index=True, use_container_width=True)
with col_b:
    st.subheader("일자별 성과")
    st.dataframe(daily_df.sort_values("날짜", ascending=False), hide_index=True, use_container_width=True)

with st.expander("전체 베팅 내역 보기 (투명성 공개)"):
    st.dataframe(sheets["베팅내역"], hide_index=True, use_container_width=True)
