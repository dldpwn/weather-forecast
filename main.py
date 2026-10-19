
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영양소 & 화학 반응 계산기",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 사이드바
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    st.page_link("pages/calculate.py", label="🥗 맞춤형 식단 플래너", icon="🥗")

# 3. 메인 화면
st.title("🍎 내 몸의 에너지 균형: 기초대사량 & 영양 가이드")
st.write(
    "나의 신체 정보를 입력하고, 비만도(BMI), 하루 대사량, "
    "그리고 몸속 화학 반응과 관련된 영양 정보를 확인해 보세요!"
)
st.divider()

st.subheader("🧍 신체 정보 입력")

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("성별", ["남성", "여성"])
    age = st.number_input(
        "나이 (세)",
        min_value=10,
        max_value=100,
        value=17
    )

with col2:
    height = st.number_input(
        "키 (cm)",
        min_value=100.0,
        max_value=220.0,
        value=170.0
    )
    weight = st.number_input(
        "체중 (kg)",
        min_value=30.0,
        max_value=150.0,
        value=60.0
    )

activity_level = st.selectbox(
    "평소 활동량",
    [
        "거의 운동하지 않음",
        "가벼운 운동 (주 1~3회)",
        "보통 운동 (주 3~5회)",
        "적극적 운동 (주 6~7회)",
        "매우 격렬한 운동"
    ]
)

activity_factors = {
    "거의 운동하지 않음": 1.2,
    "가벼운 운동 (주 1~3회)": 1.375,
    "보통 운동 (주 3~5회)": 1.55,
    "적극적 운동 (주 6~7회)": 1.725,
    "매우 격렬한 운동": 1.9
}

st.write("")

# 4. 계산 버튼
if st.button("계산 및 분석하기", use_container_width=True):

    # BMI 계산
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)

    # BMI 분류 (성인 기준 참고값)
    if bmi < 18.5:
        bmi_status = "저체중"
    elif bmi < 23:
        bmi_status = "정상"
    elif bmi < 25:
        bmi_status = "과체중"
    else:
        bmi_status = "비만 범위"

    # 기초대사량(BMR) 계산: Mifflin-St Jeor 식
    if gender == "남성":
        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            + 5
        )
    else:
        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            - 161
        )

    # 일일 총 에너지 소비량(TDEE) 추정
    tdee = bmr * activity_factors[activity_level]

    # 계산 결과를 세션 상태에 저장
    st.session_state["calculated_tdee"] = tdee
    st.session_state["calculated_bmi"] = bmi
    st.session_state["calculated_bmi_status"] = bmi_status
    st.session_state["calculated_bmr"] = bmr

# 5. 결과 출력
# 버튼을 누른 뒤 저장된 값이 있을 때만 결과 표시
if "calculated_tdee" in st.session_state:

    bmi = st.session_state["calculated_bmi"]
    bmi_status = st.session_state["calculated_bmi_status"]
    bmr = st.session_state["calculated_bmr"]
    tdee = st.session_state["calculated_tdee"]

    st.divider()
    st.subheader("📊 신체 측정 및 대사량 결과")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="체질량지수 (BMI)",
            value=f"{bmi:.1f}",
            delta=bmi_status
        )

    with m2:
        st.metric(
            label="기초대사량 (BMR)",
            value=f"{bmr:.1f} kcal"
        )

    with m3:
        st.metric(
            label="일일 총 소비량 (TDEE)",
            value=f"{tdee:.1f} kcal"
        )

    st.caption(
        "BMR은 기초대사량 추정치이며, TDEE는 활동량 계수를 적용한 "
        "하루 총 에너지 소비량의 추정치입니다."
    )

    st.write("")
    st.subheader("🥗 영양소별 에너지 배분 예시")

    # 총 에너지의 50% 탄수화물, 30% 단백질, 20% 지방으로 배분
    carbs_g = (tdee * 0.5) / 4
    protein_g = (tdee * 0.3) / 4
    fat_g = (tdee * 0.2) / 9

    st.write(f"- **탄수화물:** 약 {carbs_g:.1f} g")
    st.write(f"- **단백질:** 약 {protein_g:.1f} g")
    st.write(f"- **지방:** 약 {fat_g:.1f} g")

    st.caption(
        "영양소 비율은 계산 예시이며 개인에게 필요한 섭취량을 "
        "의학적으로 판정한 값은 아닙니다."
    )

    st.divider()

    st.success(
        "✨ 계산이 완료되었습니다! "
        "식단 플래너에서 목표에 맞는 식단 예시를 확인해 보세요."
    )

    st.page_link(
        "pages/calculate.py",
        label="🥗 식단 플래너로 이동 ➡️",
        icon="🥗"
    )
