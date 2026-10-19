
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="맞춤형 식단 플래너",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 둥근 폰트 및 디자인 설정
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, [class*="st-"],
button, input, textarea, select,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    font-family: 'Gowun Dodum', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Gowun Dodum', sans-serif !important;
    font-weight: 600 !important;
}

.stButton button {
    border-radius: 12px;
}

[data-testid="stSelectbox"] div,
[data-testid="stNumberInput"] div {
    font-family: 'Gowun Dodum', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# 3. 사이드바 메뉴
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.page_link(
        "main.py",
        label="🧪 영양소 & 화학 계산기",
        icon="🧮"
    )
    st.page_link(
        "pages/calculate.py",
        label="🥗 맞춤형 식단 플래너",
        icon="🥗"
    )

# 4. 메인 화면
st.title("🥗 내 칼로리에 맞춘 스마트 식단 플래너")
st.write(
    "나의 일일 에너지 소비량을 입력하고 "
    "목표에 맞는 식단 예시를 확인해 보세요!"
)
st.divider()

# 5. 목표 설정 및 칼로리 입력
st.subheader("1. 목표 설정 및 칼로리 입력")

c1, c2 = st.columns(2)

with c1:
    default_tdee = st.session_state.get("calculated_tdee", 2000.0)

    target_tdee = st.number_input(
        "내 일일 소비 칼로리 (TDEE, kcal)",
        min_value=1000.0,
        max_value=4000.0,
        value=float(min(4000.0, max(1000.0, default_tdee))),
        step=50.0
    )

with c2:
    goal = st.selectbox(
        "나의 건강 목표",
        [
            "체중 유지 (TDEE 유지)",
            "체중 감량 (-500 kcal)",
            "근육 증가 (+300 kcal)"
        ]
    )

# 6. 목표 칼로리 계산
if "감량" in goal:
    final_calories = target_tdee - 500
elif "증가" in goal:
    final_calories = target_tdee + 300
else:
    final_calories = target_tdee

st.write("")
st.info(f"🎯 **설정된 목표 칼로리: 약 {final_calories:.0f} kcal**")

# 7. 식단 구성
if st.button("🍽️ 맞춤형 식단 구성하기", use_container_width=True):

    # 영양소별 에너지 배분
    carb_g = (final_calories * 0.5) / 4
    protein_g = (final_calories * 0.3) / 4
    fat_g = (final_calories * 0.2) / 9

    st.divider()
    st.subheader("📋 하루 추천 영양소 및 식단 예시")

    col_a, col_b, col_c = st.columns(3)

    col_a.metric("탄수화물", f"{carb_g:.1f} g")
    col_b.metric("단백질", f"{protein_g:.1f} g")
    col_c.metric("지방", f"{fat_g:.1f} g")

    st.write("")
    st.markdown("#### 🍳 추천 하루 식단표 (예시)")

    # 식사별 칼로리 배분
    breakfast_cal = final_calories * 0.3
    lunch_cal = final_calories * 0.4
    dinner_cal = final_calories * 0.3

    tab1, tab2, tab3 = st.tabs(
        ["🌅 아침 식단", "☀️ 점심 식단", "🌙 저녁 식단"]
    )

    with tab1:
        st.write(f"**목표 칼로리: 약 {breakfast_cal:.0f} kcal**")
        st.markdown("- 통밀빵과 계란")
        st.markdown("- 과일과 견과류")
        st.markdown("- 우유 또는 두유")

    with tab2:
        st.write(f"**목표 칼로리: 약 {lunch_cal:.0f} kcal**")
        st.markdown("- 현미밥 또는 잡곡밥")
        st.markdown("- 닭고기, 생선 또는 두부")
        st.markdown("- 다양한 채소와 반찬")

    with tab3:
        st.write(f"**목표 칼로리: 약 {dinner_cal:.0f} kcal**")
        st.markdown("- 고구마 또는 잡곡밥")
        st.markdown("- 연어, 달걀 또는 두부")
        st.markdown("- 구운 채소와 샐러드")

    st.caption(
        "식단은 예시이며 실제 음식의 종류와 양에 따라 "
        "칼로리 및 영양소 함량은 달라집니다."
    )
