import streamlit as st

# 1. 페이지 설정 (사이드바 기본 숨김)
st.set_page_config(
    page_title="맞춤형 식단 플래너",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 디자인 및 사이드바 스타일 적용
st.markdown("""
    
""", unsafe_allow_html=True)

# --- 사이드바 영역 ---
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    st.page_link("pages/calculate.py", label="🥗 맞춤형 식단 플래너", icon="🥗")

# --- 메인 화면 ---
st.title("🥗 내 칼로리에 맞춘 스마트 식단 플래너")
st.write("메인 페이지에서 계산된 본인의 일일 에너지 소비량(TDEE)을 입력하고, 목표에 맞는 맞춤형 식단을 구성해보세요!")
st.divider()

# 1. 사용자 목표 및 칼로리 설정
st.subheader("1. 목표 설정 및 칼로리 입력")
c1, c2 = st.columns(2)

with c1:
    target_tdee = st.number_input("내 일일 소비 칼로리 (TDEE, kcal)", min_value=1000.0, max_value=4000.0, value=2000.0, step=50.0)

with c2:
    goal = st.selectbox(
        "나의 건강 목표",
        ["체중 유지 (TDEE 유지)", "체중 감량 (-500 kcal)", "근육 증가 (+300 kcal)"]
    )

# 목표에 따른 최종 칼로리 계산
if "감량" in goal:
    final_calories = target_tdee - 500
elif "증량" in goal:
    final_calories = target_tdee + 300
else:
    final_calories = target_tdee

st.write("")
st.info(f"🎯 **설정된 최종 목표 칼로리: 약 {final_calories:.0f} kcal**")

# 2. 식단 구성 버튼
if st.button("🍽️ 맞춤형 식단 구성하기", use_container_width=True):
    # 영양소 칼로리 배분 (탄수화물 50%, 단백질 30%, 지방 20% 기준)
    carb_kcal = final_calories * 0.5
    protein_kcal = final_calories * 0.3
    fat_kcal = final_calories * 0.2

    carb_g = carb_kcal / 4
    protein_g = protein_kcal / 4
    fat_g = fat_kcal / 9

    st.divider()
    st.subheader("📋 하루 추천 영양소 및 식단 예시")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("탄수화물", f"{carb_g:.1f} g")
    col_b.metric("단백질", f"{protein_g:.1f} g")
    col_c.metric("지방", f"{fat_g:.1f} g")

    st.write("")
    st.markdown("#### 🍳 추천 하루 식단표 (예시)")
    
    # 아침, 점심, 저녁 칼로리 배분 (3:4:3)
    breakfast_cal = final_calories * 0.3
    lunch_cal = final_calories * 0.4
    dinner_cal = final_calories * 0.3

    tab1, tab2, tab3 = st.tabs(["🌅 아침 식단", "☀️ 점심 식단", "🌙 저녁 식단"])
    
    with tab1:
        st.write(f"**목표 칼로리: 약 {breakfast_cal:.0f} kcal**")
        st.markdown("- 통밀빵 2장 (탄수화물)")
        st.markdown("- 삶은 계란 2개 (단백질)")
        st.markdown("- 아몬드 한 줌 & 사과 반 개 (지방 및 비타민)")

    with tab2:
        st.write(f"**목표 칼로리: 약 {lunch_cal:.0f} kcal**")
        st.markdown("- 현미밥 또는 흑미밥 1공기 (탄수화물)")
        st.markdown("- 닭가슴살 샐러드 또는 소고기 우둔살 구이 (단백질)")
        st.markdown("- 각종 나물 및 올리브유 드레싱 (식이섬유 및 지방)")

    with tab3:
        st.write(f"**목표 칼로리: 약 {dinner_cal:.0f} kcal**")
        st.markdown("- 고구마 1~2개 또는 단호박 (탄수화물)")
        st.markdown("- 연어 구이 또는 두부 스테이크 (단백질)")
        st.markdown("- 구운 채소 믹스 (무기질 및 비타민)")
