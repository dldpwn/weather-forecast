import streamlit as st

# 1. 페이지 설정 (initial_sidebar_state="collapsed"로 평소엔 사이드바 숨김)
st.set_page_config(
    page_title="영양소 & 화학 반응 계산기",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# 2. 디자인 및 사이드바 스타일 적용
st.markdown("""
    
""", unsafe_allow_html=True)

# --- 사이드바 영역 (원할 때 열고 닫을 수 있음) ---
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.info("💡 왼쪽 위의 **`>` (화살표)**를 누르면 사이드바를 다시 숨길 수 있어요!")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    # 파일 이름을 반영하여 경로를 pages/calculate.py로 수정했습니다.
    st.page_link("pages/calculate.py", label="📄 계산 서브 페이지", icon="📄")

# --- 메인 화면 ---
st.title("🧪 내 몸에 맞는 영양소 & 화학 반응 계산기")
st.write("나의 신체 정보를 입력하고, 하루 대사량과 권장 영양소, 그리고 몸속 화학 반응을 확인해보세요!")
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
    if gender == "남성":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    tdee = bmr * activity_factors[activity_level]
    carbs_g = (tdee * 0.5) / 4
    protein_g = (tdee * 0.3) / 4
    fat_g = (tdee * 0.2) / 9

    st.divider()
    st.subheader("📊 계산 결과")

    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="기초대사량 (BMR)", value=f"{bmr:.1f} kcal")
    with m2:
        st.metric(label="일일 총 에너지 소비량 (TDEE)", value=f"{tdee:.1f} kcal")

    st.write("")
    st.markdown("#### 🥗 권장 영양소 섭취량")
    st.write(f"- **탄수화물**: 약 **{carbs_g:.1f}g** (주요 에너지원)")
    st.write(f"- **단백질**: 약 **{protein_g:.1f}g** (신체 조직 구성 및 효소)")
    st.write(f"- **지방**: 약 **{fat_g:.1f}g** (에너지 저장 및 세포막 구성)")

    st.divider()
    st.subheader("🔬 교과 연계: 우리 몸속 화학 반응")
    st.info(
        "**1. 세포 호흡 (에너지 생성 반응)**\n"
        "우리가 섭취한 탄수화물(포도당)은 미토콘드리아에서 산소와 반응하여 ATP 에너지를 합성합니다.\n\n"
        "**2. 단백질의 소화와 합성**\n"
        "섭취한 단백질은 아미노산으로 분해된 후, 체내에서 근육과 생체 촉매(효소)로 재조합됩니다."
    )
