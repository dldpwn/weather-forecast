
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="식단 구성 확인 | NutriDay",
    page_icon="🥗",
    layout="wide"
)

# -----------------------------
# 페이지 스타일
# -----------------------------
st.markdown("""
<style>
    html, body, p, label,
    h1, h2, h3, h4, h5, h6,
    .stMarkdown,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #377D61;
        margin-bottom: 0.3rem;
    }

    .sub-text {
        color: #777777;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .info-card {
        background-color: #F1F8F3;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")

    st.page_link("main.py", label="🏠 메인 페이지")
    st.page_link(
        "pages/calculate.py",
        label="🥗 식단 구성 확인"
    )

# -----------------------------
# 제목
# -----------------------------
st.markdown(
    '<div class="main-title">🥗 하루 식단 구성 확인</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-text">'
    '하루 에너지 참고값을 기준으로 영양소별 에너지 구성을 확인해 보세요.'
    '</div>',
    unsafe_allow_html=True
)

# -----------------------------
# 하루 에너지 참고값
# -----------------------------
# 메인 페이지에서 전달한 값이 있으면 사용하고,
# 없으면 기본값 2000 kcal 사용
daily_energy = st.session_state.get(
    "meal_plan_calories",
    2000
)

st.markdown("### 🔥 하루 에너지 참고값")

daily_energy = st.number_input(
    "하루 에너지 참고값 (kcal)",
    min_value=500,
    max_value=6000,
    value=int(daily_energy),
    step=100,
    help="메인 페이지에서 계산한 값이 있다면 해당 값을 기준으로 시작해요."
)

# -----------------------------
# 식단 목표 선택
# -----------------------------
st.markdown("### 🎯 식단 목표")

goal = st.radio(
    "목표를 선택하세요.",
    ["에너지 균형", "체중 감량 참고", "근육 증가 참고"],
    horizontal=True
)

if goal == "에너지 균형":
    target_energy = daily_energy
elif goal == "체중 감량 참고":
    target_energy = max(500, daily_energy - 500)
else:
    target_energy = daily_energy + 300

st.session_state["meal_plan_calories"] = target_energy

st.metric(
    label="목표 하루 에너지",
    value=f"{target_energy:,.0f} kcal"
)

st.caption(
    "목표별 에너지 조정은 단순한 예시이며, 개인에게 적합한 섭취량을 "
    "확정하는 의학적 권고는 아니에요."
)

st.divider()

# -----------------------------
# 영양소 에너지 비율 설정
# -----------------------------
st.markdown("### 🍚 영양소 에너지 비율")

st.caption(
    "아래 비율은 그래프 작성을 위한 예시예요. "
    "세 영양소의 비율 합계는 100%가 되도록 계산해요."
)

col1, col2, col3 = st.columns(3)

with col1:
    carb_ratio = st.number_input(
        "탄수화물 (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )

with col2:
    protein_ratio = st.number_input(
        "단백질 (%)",
        min_value=0,
        max_value=100,
        value=20,
        step=5
    )

with col3:
    fat_ratio = st.number_input(
        "지방 (%)",
        min_value=0,
        max_value=100,
        value=30,
        step=5
    )

ratio_sum = carb_ratio + protein_ratio + fat_ratio

if ratio_sum != 100:
    st.warning(
        f"현재 비율 합계는 {ratio_sum}%예요. "
        "그래프를 보려면 세 영양소의 합계를 100%로 맞춰 주세요."
    )
    st.stop()

# -----------------------------
# 에너지량 및 섭취량 계산
# -----------------------------
carb_kcal = target_energy * carb_ratio / 100
protein_kcal = target_energy * protein_ratio / 100
fat_kcal = target_energy * fat_ratio / 100

# 탄수화물 1g = 약 4 kcal
# 단백질 1g = 약 4 kcal
# 지방 1g = 약 9 kcal
carb_g = carb_kcal / 4
protein_g = protein_kcal / 4
fat_g = fat_kcal / 9

chart_data = pd.DataFrame({
    "영양소": ["탄수화물", "단백질", "지방"],
    "에너지량(kcal)": [
        carb_kcal,
        protein_kcal,
        fat_kcal
    ],
    "에너지 비율(%)": [
        carb_ratio,
        protein_ratio,
        fat_ratio
    ],
    "환산 섭취량(g)": [
        carb_g,
        protein_g,
        fat_g
    ]
})

# -----------------------------
# 에너지 비율 그래프
# -----------------------------
st.markdown("### 📊 하루 에너지 구성 비율")

st.caption(
    f"목표 에너지 {target_energy:,.0f} kcal 기준"
)

fig = px.pie(
    chart_data,
    names="영양소",
    values="에너지량(kcal)",
    hole=0.55
)

fig.update_traces(
    texttemplate="%{label}<br>%{percent}",
    textposition="inside",
    hovertemplate=(
        "%{label}<br>"
        "에너지량: %{value:.0f} kcal<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    showlegend=True,
    margin=dict(t=20, b=20, l=10, r=10),
    legend_title_text="영양소"
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="nutrition_donut_chart"
)

# -----------------------------
# 영양소별 계산 결과
# -----------------------------
st.markdown("### 📋 영양소별 계산 결과")

display_data = chart_data.copy()

display_data["에너지량(kcal)"] = (
    display_data["에너지량(kcal)"].round(1)
)

display_data["에너지 비율(%)"] = (
    display_data["에너지 비율(%)"].map(
        lambda x: f"{x}%"
    )
)

display_data["환산 섭취량(g)"] = (
    display_data["환산 섭취량(g)"].round(1)
)

st.dataframe(
    display_data,
    hide_index=True,
    use_container_width=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "탄수화물",
        f"{carb_g:,.1f} g",
        f"{carb_kcal:,.0f} kcal"
    )

with col2:
    st.metric(
        "단백질",
        f"{protein_g:,.1f} g",
        f"{protein_kcal:,.0f} kcal"
    )

with col3:
    st.metric(
        "지방",
        f"{fat_g:,.1f} g",
        f"{fat_kcal:,.0f} kcal"
    )

# -----------------------------
# 안내
# -----------------------------
st.divider()

st.markdown("### 💡 알아두기")

st.markdown("""
- 이 그래프는 하루 에너지 목표를 탄수화물·단백질·지방에 배분한 **계산 예시**예요.
- 비타민과 무기질은 에너지를 직접 제공하지 않으므로 이 에너지 비율 그래프에는 포함하지 않아요.
- 실제 음식으로 섭취한 영양소의 양을 분석하는 기능은 아니에요.
- 개인에게 적합한 영양 섭취량은 나이, 성장 상태, 활동량 등 여러 요소에 따라 달라질 수 있어요.
""")
