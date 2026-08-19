"""프리미엄 리포트 구독 신청 랜딩페이지.

결제 시스템(PG)이 아직 없어(사업자등록 전) 실제 결제는 받지 않는다. 신청은 mailto 링크로
운영자 메일에 신청 내용을 보내는 방식이며, 서버/DB 없이 정적으로 동작한다. 실제 등록은
운영자가 입금 확인 후 subscribers.py로 수동 처리한다.
"""
from __future__ import annotations

from urllib.parse import quote

import streamlit as st

OWNER_EMAIL = "rushsis2203@gmail.com"

PLANS = {
    "통합 (KBO/NPB + MLB)": 50_000,
    "리그별 (KBO/NPB 또는 MLB 중 1개)": 30_000,
}

st.set_page_config(page_title="구독 신청 · 토토분석", page_icon="📬", layout="wide")

st.title("📬 프리미엄 리포트 구독 신청")
st.caption("매일 EV>0 조합을 배당·추천 베팅 금액과 함께 이메일로 보내드립니다. 적중하면 알림 메일도 따로 갑니다.")

st.markdown('📊 <a href="/" target="_self">⬅ 공개 트랙레코드(적중률·ROI) 먼저 보기</a>', unsafe_allow_html=True)

st.divider()

col_pitch, col_price = st.columns([3, 2])

with col_pitch:
    st.subheader("무엇을 받나요")
    st.markdown(
        "- 매일 경기 전 EV(기대값) 양수 조합 추천 (경기/마켓/선택/배당 포함)\n"
        "- 조합별 추천 베팅 금액 (켈리 기준)\n"
        "- KBO/NPB, MLB **리그별로 분리 발송** (한 메일에 섞이지 않음)\n"
        "- 추천 조합이 적중하면 별도 적중 알림 메일\n"
    )
    st.info(
        "이 리포트는 통계적 분석 결과이며 베팅/투자 권유가 아닙니다. 실제 배팅 여부와 금액은 "
        "본인 판단과 책임 하에 결정하세요.",
        icon="ℹ️",
    )
    st.warning(
        "아직 결제 시스템(PG) 연동 전이라 카드 결제는 받지 않습니다. 아래에서 신청하시면 "
        "운영자가 직접 연락드려 입금 방법을 안내하고, 확인 후 구독자로 등록합니다.",
        icon="🚧",
    )
    st.error(
        "**수익성은 아직 증명되지 않았습니다.** 지금까지의 실계좌 성적은 표본이 작아 "
        "수익률의 신뢰구간이 0을 포함하며, 개별 픽의 적중률도 배당이 함축하는 확률을 "
        "넘어서지 못했습니다. 이 구독은 \"돈을 벌어드리는 서비스\"가 아니라 매일 자동으로 "
        "계산되는 확률·기댓값·근거 수치를 받아보는 분석 자료입니다. "
        "판단 근거는 공개 트랙레코드에서 직접 확인하세요.",
        icon="⚠️",
    )
    st.markdown('📊 <a href="/" target="_self">공개 트랙레코드의 신뢰도 지표 확인하기 →</a>', unsafe_allow_html=True)

with col_price:
    st.subheader("가격")
    for plan_name, price in PLANS.items():
        st.metric(plan_name, f"{price:,}원 / 월")

st.divider()

st.subheader("신청하기")
email = st.text_input("받으실 이메일 주소", placeholder="you@example.com")
plan_name = st.radio("플랜 선택", list(PLANS.keys()))
price = PLANS[plan_name]

subject = quote(f"[토토분석] 구독 신청 - {plan_name}")
body = quote(
    f"신청 플랜: {plan_name} (월 {price:,}원)\n"
    f"받을 이메일: {email or '(여기에 이메일 주소를 적어주세요)'}\n\n"
    "위 내용으로 구독 신청합니다."
)
mailto_url = f"mailto:{OWNER_EMAIL}?subject={subject}&body={body}"

st.link_button("📧 이 내용으로 구독 신청 메일 보내기", url=mailto_url, type="primary")
st.caption(f"메일 앱이 열리면 {OWNER_EMAIL} 앞으로 신청 내용이 채워져 있습니다. 그대로 보내주시면 됩니다.")

st.divider()
st.caption(
    "본 서비스는 합법 스포츠토토(프로토) 참고용 통계 분석 자료이며, 베팅·투자 권유가 아닙니다. "
    "성과 수치는 표기된 기간·표본에 한정되며 미래 성과를 보장하지 않습니다. "
    "19세 미만은 이용할 수 없습니다. "
    "도박 문제로 어려움을 겪고 있다면 한국도박문제예방치유원 상담전화 1336으로 연락하세요."
)
