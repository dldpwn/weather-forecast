
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NutriDay | 영양 관리",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, p, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, [data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    font-family: 'Gowun Dodum', sans-serif !important;
}

.stApp {
    background-color: #FAF9F3;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

h1, h2, h3 {
    color: #294B3D;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E3E9DF;
    border-radius: 18px;
    padding: 20px;
}

.stButton > button,
.stLinkButton > a {
    background-color: #4F8069;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1rem;
}

.stButton > button:hover,
.stLinkButton > a:hover {
    background-color: #294B3D;
    color: white;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🥗 NutriDay")
    st.page_link("main.py", label="내 영양 대시보드", icon="🏠")
    st.page_link("pages/calculate.py", label="맞춤형 식단 플래너", icon="🍽️")

st.title("🥗 NutriDay")
st.caption("나의 건강한 하루를 위한 영양 관리")

st.markdown("""
<div style="
    background: linear-gradient(120deg, #DDEFE5, #F1F4E8);
    padding: 28px;
    border-radius: 22px;
    margin-bottom: 24px;">
    <h2 style="margin: 0; color: #294B3D;">나에게 맞는 영양 관리</h2>
    <p style="margin: 8px 0 0; color: #496858;">
        기본 정보를 입력하고 하루 에너지 필요량을 확인해 보세요.
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("내 기본 정보")

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("성별", ["여성", "남성"])
        age = st.number_input("나이", min_value=10, max_value=100, value=17)
        height = st.number_input(
            "키 (cm)", min_value=100.0, max_value=220.0, value=170.0
        )

    with col2:
        weight = st.number_input(
            "체중 (kg)", min_value=30.0, max_value=150.0, value=60.0
        )
        activity = st.selectbox(
            "평소 활동량",
            [
                "거의 활동하지 않음",
                "가벼운 활동",
                "보통 활동",
                "많은 활동",
                "매우 많은 활동"
            ]
        )

activity_factors = {
    "거의 활동하지 않음": 1.2,
    "가벼운 활동": 1.375,
    "보통 활동": 1.55,
    "많은 활동": 1.725,
    "매우 많은 활동": 1.9
}

if st.button("내 영양 정보 계산하기", use_container_width=True):
    bmi = weight / ((height / 100) ** 2)

    if gender == "남성":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity_factors[activity]

    st.session_state["calculated_bmi"] = bmi
    st.session_state["calculated_bmr"] = bmr
    st.session_state["calculated_tdee"] = tdee
    st.session_state["calculated_age"] = age
    st.session_state["calculated_height"] = height
    st.session_state["calculated_weight"] = weight
    st.session_state["calculated_gender"] = gender
    st.session_state["calculated_activity"] = activity

if "calculated_tdee" in st.session_state:
    st.divider()
    st.subheader("📊 나의 계산 결과")

    bmi = st.session_state["calculated_bmi"]
    bmr = st.session_state["calculated_bmr"]
    tdee = st.session_state["calculated_tdee"]
    saved_age = st.session_state["calculated_age"]

    col1, col2, col3 = st.columns(3)

    col1.metric("BMI", f"{bmi:.1f}")
    col2.metric("기초대사량", f"{bmr:,.0f} kcal")
    col3.metric("하루 에너지 소비 추정량", f"{tdee:,.0f} kcal")

    if saved_age < 18:
        st.info(
            "청소년은 성장 단계에 따라 필요한 에너지가 달라질 수 있어요. "
            "이 계산값은 참고용이며, BMI도 성인 기준으로 건강 상태를 판단하는 데 "
            "사용하지 않는 것이 좋아요."
        )

    st.markdown("""
    <div style="
        background-color: #EAF3EC;
        padding: 22px;
        border-radius: 18px;
        margin-top: 18px;">
        <h3 style="margin: 0;">오늘의 영양 관리</h3>
        <p style="margin-bottom: 0;">
            계산한 에너지 소비량을 참고해 맞춤형 식단을 살펴보세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.page_link(
        "pages/calculate.py",
        label="🍽️ 맞춤형 식단 플래너로 이동하기",
        use_container_width=True
    )
