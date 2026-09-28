import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영양소 & 화학 반응 계산기",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# 2. 디자인 및 사이드바 스타일 적용 (앱 전체 폰트 및 글자 크기 강제 통일)
st.markdown("""
    
""", unsafe_allow_html=True)

# --- 사이드바 영역 ---
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.info("💡 왼쪽 위의 **`>` (화살표)**를 누르면 사이드바를 다시 숨길 수 있어요!")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    st.page_link("pages/calculate.py", label="🥗 맞춤형 식단 플래너", icon="🥗")

# --- 메인 화면 ---
st.title("🧪 내 몸에 맞는 영양소 & 화학 반응 계산기")
st.write("나의 신체 정보를 입력하고, 비만도(BMI), 하루 대사량, 그리고 몸속 화학 반응을 확인해보세요!")
st.divider()

st.subheader("1. 신체 정보 입력")
col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("성별", ["남성", "여성"])
    age = st.number_input("나이 (세)", min_value=10, max_value=100, value=17)

with col2:
    height = st.number_input("키 (cm)", min_value=100.0, max_value=220.0, value=170.0)
    weight = st.number_input("체중 (kg)", min_value=30.0, max_value=150.0, value=60.0)

activity_level = st.selectbox(
    "평소 활동량",
    ["거의 운동하지 않음", "가벼운 운동 (주 1~3회)", "보통 운동 (주 3~5회)", "적극적 운동 (주 6~7회)", "매우 격렬한 운동"]
)

activity_factors = {
    "거의 운동하지 않음": 1.2,
    "가벼운 운동 (주 1~3회)": 1.375,
    "보통 운동 (주 3~5회)": 1.55,
    "적극적 운동 (주 6~7회)": 1.725,
    "매우 격렬한 운동": 1.9
}

st.write("")

if st.button("계산 및 분석하기", use_container_width=True):
    # 1. BMI 계산 (체중(kg) / 키(m의 제곱))
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)

    # BMI 판정
    if bmi < 18.5:
        bmi_status = "저체중"
    elif 18.5 <= bmi < 23:
        bmi_status = "정상"
    elif 23 <= bmi < 25:
        bmi_status = "과체중"
    else:
        bmi_status = "비만"

    # 2. 기초대사량(BMR) 계산
    if gender == "남성":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # 3. 일일 총 에너지 소비량(TDEE) 계산
    tdee = bmr * activity_factors[activity_level]

    # 세션 상태에 계산값 저장
    st.session_state["calculated_tdee"] = tdee

    st.divider()
    st.subheader("📊 신체 측정 및 대사량 결과")

    # 결과 지표 표시
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="체질량지수 (BMI)", value=f"{bmi:.1f}", delta=bmi_status)
    with m2:
        st.metric(label="기초대사량 (BMR)", value=f"{bmr:.1f} kcal")
    with m3:
        st.metric(label="일일 총 에너지 소비량 (TDEE)", value=f"{tdee:.1f} kcal")

    st.write("")
    st.markdown("#### 🥗 권장 영양소 섭취량")
    carbs_g = (tdee * 0.5) / 4
    protein_g = (tdee * 0.3) / 4
    fat_g = (tdee * 0.2) / 9
    st.write(f"- **탄수화물**: 약 **{carbs_g:.1f}g** (주요 에너지원)")
    st.write(f"- **단백질**: 약 **{protein_g:.1f}g** (신체 조직 구성 및 효소)")
    st.write(f"- **지방**: 약 **{fat_g:.1f}g** (에너지 저장 및 세포막 구성)")

    st.divider()
    
    # --- 서브 페이지 이동 안내 및 버튼 ---
    st.success("✨ 계산이 완료되었습니다! 내 칼로리에 맞춘 맞춤형 식단을 확인하러 가볼까요?")
    
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        st.write("👉 우측의 버튼을 누르면 **맞춤형 식단 플래너** 페이지로 이동합니다.")
    with col_btn2:
        st.page_link("pages/calculate.py", label="식단 플래너로 이동 ➡️", icon="🥗")
