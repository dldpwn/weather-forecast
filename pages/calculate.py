
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NutriDay | 식단 플래너",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 디자인 시스템 ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

:root {
    --mint: #DDEFE5;
    --green: #4F8069;
    --dark: #294B3D;
    --cream: #FAF9F3;
    --muted: #75877C;
}

html, body, [class*="st-"],
p, label, input, textarea,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    font-family: 'Gowun Dodum', sans-serif !important;
}

.stApp {
    background: var(--cream);
}

.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: var(--dark) !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E7EDE6;
    padding: 20px;
    border-radius: 18px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
}

[data-testid="stMetricValue"] {
    color: var(--dark) !important;
}

.stButton > button {
    background: var(--green);
    color: white;
    border: none;
    border-radius: 13px;
    min-height: 46px;
    font-family: 'Gowun Dodum', sans-serif !important;
}

.stButton > button:hover {
    background: var(--dark);
    color: white;
    border: none;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 18px;
    border-color: #E7EDE6;
}

hr {
    border-color: #E5EAE1;
}

#MainMenu, footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.markdown("## 🌿 NutriDay")
    st.caption("나를 위한 건강 관리")
    st.divider()
    st.page_link("main.py", label="🏠 건강 대시보드")
    st.page_link("pages/calculate.py", label="🥗 맞춤형 식단 플래너")

# ── 상단 소개 ──
st.markdown("### 🌿 NUTRIDAY")
st.title("나만의 식단 플래너")
st.write("하루 에너지 정보와 목표를 바탕으로 식단 예시를 구성해 보세요.")

st.markdown("""
<div style="
    background: linear-gradient(120deg, #DDEFE5, #F0F4DF);
    padding: 25px;
    border-radius: 22px;
    margin: 18px 0 25px 0;
">
    <div style="font-size:14px; color:#4F8069;">
        YOUR DAILY MEAL PLAN
    </div>
    <div style="font-size:25px; color:#294B3D; font-weight:bold;
                margin-top:8px;">
        오늘의 식단을 계획해 볼까요? 🥑
    </div>
    <div style="font-size:14px; color:#526D5D; margin-top:8px;">
        목표 칼로리와 영양소 배분을 살펴보세요.
    </div>
</div>
""", unsafe_allow_html=True)

# ── 목표 설정 ──
st.subheader("🎯 목표 설정")

saved_tdee = st.session_state.get("calculated_tdee", 2000.0)
default_tdee = float(min(4000.0, max(1000.0, saved_tdee)))

with st.container(border=True):
    c1, c2 = st.columns(2)

    with c1:
        target_tdee = st.number_input(
            "하루 총 에너지 소비량 (kcal)",
            min_value=1000.0,
            max_value=4000.0,
            value=default_tdee,
            step=50.0,
            help="메인 페이지에서 계산한 값이 있으면 자동으로 입력됩니다."
        )

    with c2:
        goal = st.selectbox(
            "식단 목표",
            [
                "에너지 균형 참고하기",
                "체중 감량 목표 참고 (-500 kcal)",
                "근육 증가 목표 참고 (+300 kcal)"
            ]
        )

if "감량" in goal:
    final_calories = target_tdee - 500
elif "증가" in goal:
    final_calories = target_tdee + 300
else:
    final_calories = target_tdee

st.write("")

with st.container(border=True):
    st.markdown("#### 🌱 설정한 하루 에너지 목표")
    st.metric("목표 에너지", f"{final_calories:,.0f} kcal")
    st.caption(
        "이 값은 단순 계산 예시입니다. 특히 성장기에는 "
        "임의의 감량·증량 칼로리 목표를 적용하지 마세요."
    )

# ── 식단 생성 ──
if st.button("🍽️ 식단 예시 구성하기", use_container_width=True):
    st.session_state["meal_plan_calories"] = final_calories
    st.session_state["meal_plan_goal"] = goal

if "meal_plan_calories" in st.session_state:
    calories = st.session_state["meal_plan_calories"]

    # 에너지 배분 예시
    carb_g = calories * 0.5 / 4
    protein_g = calories * 0.3 / 4
    fat_g = calories * 0.2 / 9

    st.divider()
    st.subheader("📊 하루 영양소 구성 예시")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("탄수화물", f"{carb_g:.1f} g")
    metric2.metric("단백질", f"{protein_g:.1f} g")
    metric3.metric("지방", f"{fat_g:.1f} g")

    chart_col, detail_col = st.columns([1.1, 1])

    with chart_col:
        st.markdown("#### 영양소 에너지 비율")
        macro_data = pd.DataFrame({
            "영양소": ["탄수화물", "단백질", "지방"],
            "에너지 비율 (%)": [50, 30, 20]
        })
        st.bar_chart(
            macro_data,
            x="영양소",
            y="에너지 비율 (%)",
            color="#75A88C",
            height=270
        )

    with detail_col:
        st.markdown("#### 에너지 배분")
        with st.container(border=True):
            st.markdown("🍚 **탄수화물 · 50%**")
            st.progress(0.5)
            st.caption(f"약 {calories * 0.5:,.0f} kcal")

        with st.container(border=True):
            st.markdown("🥚 **단백질 · 30%**")
            st.progress(0.3)
            st.caption(f"약 {calories * 0.3:,.0f} kcal")

        with st.container(border=True):
            st.markdown("🥑 **지방 · 20%**")
            st.progress(0.2)
            st.caption(f"약 {calories * 0.2:,.0f} kcal")

    st.divider()
    st.subheader("🍽️ 하루 식사 예시")

    breakfast_cal = calories * 0.3
    lunch_cal = calories * 0.4
    dinner_cal = calories * 0.3

    tab1, tab2, tab3 = st.tabs(
        ["🌅 아침", "☀️ 점심", "🌙 저녁"]
    )

    with tab1:
        with st.container(border=True):
            st.markdown("### 🌅 아침 식사")
            st.metric("배분 에너지 예시", f"{breakfast_cal:,.0f} kcal")
            st.markdown("- 통밀빵과 달걀")
            st.markdown("- 과일과 견과류")
            st.markdown("- 우유 또는 두유")

    with tab2:
        with st.container(border=True):
            st.markdown("### ☀️ 점심 식사")
            st.metric("배분 에너지 예시", f"{lunch_cal:,.0f} kcal")
            st.markdown("- 현미밥 또는 잡곡밥")
            st.markdown("- 닭고기, 생선 또는 두부")
            st.markdown("- 다양한 채소와 반찬")

    with tab3:
        with st.container(border=True):
            st.markdown("### 🌙 저녁 식사")
            st.metric("배분 에너지 예시", f"{dinner_cal:,.0f} kcal")
            st.markdown("- 고구마 또는 잡곡밥")
            st.markdown("- 연어, 달걀 또는 두부")
            st.markdown("- 구운 채소와 샐러드")

    st.caption(
        "음식 목록은 식단 아이디어이며 개별 음식의 실제 칼로리를 "
        "계산한 식단표는 아닙니다. 식품 종류와 섭취량에 따라 영양소 함량은 달라집니다."
    )

else:
    st.info("👆 목표를 설정한 다음 식단 예시 구성하기를 눌러 주세요.")

st.divider()
st.page_link(
    "main.py",
    label="← 건강 대시보드로 돌아가기",
    icon="🏠",
    use_container_width=True
)
st.caption("NUTRIDAY · 나를 이해하는 건강 관리 프로젝트 🌿")
