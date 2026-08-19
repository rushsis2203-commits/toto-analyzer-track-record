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
CALIBRATION_PATH = Path(__file__).resolve().parent / "data" / "Pick_Calibration.xlsx"
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
risk_df = sheets["신뢰도"].set_index("지표")["값"] if "신뢰도" in sheets else None

updated_at = datetime.fromtimestamp(DATA_PATH.stat().st_mtime, tz=KST).strftime("%Y-%m-%d %H:%M KST")

# 표시광고법상 성과 수치는 기간·표본을 함께 밝혀야 한다. 숫자만 떼어 보여주지 않는다.
period = ""
if not daily_df.empty:
    period = f"{daily_df['날짜'].iloc[0]} ~ {daily_df['날짜'].iloc[-1]} · "
sample_note = (
    f"집계 기준: {period}"
    f"{summary_df.get('운영일수', 'N/A')}일 / {summary_df.get('총 베팅 수', 'N/A')}건"
)
st.caption(f"{sample_note} · 마지막 갱신: {updated_at}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("적중률", summary_df.get("적중률", "N/A"), help=sample_note)
col2.metric("누적 순수익", summary_df.get("누적 순수익", "N/A"), help=sample_note)
col3.metric("베팅 대비 수익률(ROI)", summary_df.get("베팅 대비 수익률(ROI)", "N/A"), help=sample_note)
col4.metric("초기 자본 대비 누적 수익률", summary_df.get("초기 자본 대비 누적 수익률", "N/A"), help=sample_note)
st.caption(f"※ 위 수치는 모두 {sample_note.replace('집계 기준: ', '')} 표본에 한정된 값이며, 미래 성과를 보장하지 않습니다.")

# --- 불리한 수치도 같은 화면에 --------------------------------------------------------
# 좋아 보이는 숫자만 공개하면 첫 연패에서 신뢰가 무너진다. 최대낙폭·신뢰구간·수익 집중도를
# 위 지표 바로 아래 둔다.
if risk_df is not None:
    st.subheader("신뢰도 (불리한 수치 포함)")
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    risk_col1.metric(
        "최대 낙폭(MDD)", risk_df.get("최대 낙폭(MDD)", "N/A"),
        help=str(risk_df.get("최대 낙폭 구간", "")),
    )
    risk_col2.metric("ROI 95% 신뢰구간", risk_df.get("ROI 95% 신뢰구간", "N/A"))
    top_days_key = next((k for k in risk_df.index if k.startswith("상위") and "제외" in k), None)
    risk_col3.metric(
        "상위 3일 제외 시 순수익",
        risk_df.get(top_days_key, "N/A") if top_days_key else "N/A",
        help=f"상위일: {risk_df.get('상위일 날짜', 'N/A')}",
    )

    significance = str(risk_df.get("ROI가 0보다 크다고 말할 수 있는가", ""))
    if significance.startswith("아니오"):
        st.warning(
            f"**수익성은 아직 통계적으로 증명되지 않았습니다.** {significance} "
            "표본이 더 쌓이기 전까지 이 트랙레코드를 수익 근거로 해석하지 마세요.",
            icon="⚠️",
        )
    with st.expander("신뢰도 지표 전체 보기"):
        st.dataframe(sheets["신뢰도"], hide_index=True, width="stretch")

st.subheader("잔고 추이")
if not balance_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=balance_df["날짜"], y=balance_df["최종 잔고"], mode="lines+markers", name="잔고"))
    fig.update_layout(yaxis_title="잔고(원)", xaxis_title="날짜", height=360)
    st.plotly_chart(fig, width="stretch")
else:
    st.write("아직 잔고 추이 데이터가 없습니다.")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("리그별 성과")
    st.dataframe(league_df, hide_index=True, width="stretch")
with col_b:
    st.subheader("일자별 성과")
    st.dataframe(daily_df.sort_values("날짜", ascending=False), hide_index=True, width="stretch")

with st.expander("전체 베팅 내역 보기 (투명성 공개)"):
    st.dataframe(sheets["베팅내역"], hide_index=True, width="stretch")


# --- 레그 단위 캘리브레이션 ------------------------------------------------------------
# 조합 ROI는 표본이 100건대라 신뢰구간이 ±30%p씩 벌어진다. 반면 개별 픽은 3,000건 넘게
# 쌓여 있어 "모델이 60%라고 한 픽이 실제로 몇 % 맞았는지"는 통계적으로 말할 수 있다.
if CALIBRATION_PATH.exists():
    calibration = load_sheets(CALIBRATION_PATH, CALIBRATION_PATH.stat().st_mtime)
    calibration_summary = calibration["요약"].set_index("지표")["값"]

    st.subheader("개별 픽 캘리브레이션")
    st.caption(
        f"모델이 \"이 픽은 60% 맞는다\"고 했을 때 실제로 몇 %가 맞았는지 대조한 표입니다. "
        f"표본 {calibration_summary.get('전체 픽 수', 'N/A')} "
        f"({calibration_summary.get('표본 기간', 'N/A')})."
    )

    cal_col1, cal_col2, cal_col3 = st.columns(3)
    cal_col1.metric("모델 예측 평균", calibration_summary.get("모델 예측 평균 확률", "N/A"))
    cal_col2.metric("실제 적중률", calibration_summary.get("실제 적중률", "N/A"))
    cal_col3.metric(
        "브라이어 점수", calibration_summary.get("브라이어 점수", "N/A"),
        help=f"기준선(평균만 찍는 모델): {calibration_summary.get('기준선(평균만 찍는 모델)', 'N/A')} · 낮을수록 좋음",
    )

    if "확률구간별" in calibration:
        bucket_df = calibration["확률구간별"]
        st.dataframe(bucket_df, hide_index=True, width="stretch")

    st.info(
        f"마켓당 평균 하우스 마진은 {calibration_summary.get('마켓당 평균 하우스 마진', 'N/A')}이고, "
        f"2폴더 조합이면 {calibration_summary.get('2폴더 조합 시 누적 마진', 'N/A')}가 누적됩니다. "
        "베팅으로 수익을 내려면 모델이 이 마진을 넘어서야 합니다.",
        icon="ℹ️",
    )

    verdict = str(calibration_summary.get("Gate 2 판정", ""))
    if verdict.startswith("미통과") or verdict.startswith("표본 부족"):
        st.warning(f"**시장 대비 우위는 아직 확인되지 않았습니다.** {verdict}", icon="⚠️")

    with st.expander("마켓별·리그별 캘리브레이션 자세히 보기"):
        if "마켓별" in calibration:
            st.markdown("**마켓별**")
            st.dataframe(calibration["마켓별"], hide_index=True, width="stretch")
        if "리그별" in calibration:
            st.markdown("**리그별**")
            st.dataframe(calibration["리그별"], hide_index=True, width="stretch")

st.divider()
st.caption(
    "본 페이지는 합법 스포츠토토(프로토) 참고용 통계 분석 자료이며, 베팅·투자 권유가 아닙니다. "
    "모든 성과 수치는 표기된 기간·표본에 한정된 값이고 미래 성과를 보장하지 않습니다. "
    "19세 미만은 이용할 수 없습니다. "
    "도박 문제로 어려움을 겪고 있다면 한국도박문제예방치유원 상담전화 1336으로 연락하세요."
)
