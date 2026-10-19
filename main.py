
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NutriDay | 건강 대시보드",
    page_icon="🌿",
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

.stButton > button,
.stDownloadButton > button {
    background: var(--green);
    color: white;
    border: none;
    border-radius: 13px;
    min-height: 46px;
    font-family: 'Gowun Dodum', sans-serif !important;
    transition: background 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--dark);
    color: white;
    border: none;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 18px;
    border-color: #E7EDE6;
}

[data-testid="stProgressBar"] > div > div {
    background-color: var(--green);
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

# ── 상단 영역 ──
st.markdown("### 🌿 NUTRIDAY")
st.title("나를 위한 건강 대시보드")
st.write("신체 정보와 활동량을 바탕으로 에너지 정보를 확인해 보세요.")

st.markdown("""
<div style="
    background: linear-gradient(120deg, #DDEFE5, #F0F4DF);
    padding: 25px;
    border-radius: 22px;
    margin: 18px 0 25px 0;
">
    <div style="font-size: 14px; color: #4F8069;">
        YOUR DAILY WELLNESS
    </div>
    <div style="font-size: 25px; color: #294B3D; font-weight: bold;
                margin-top: 8px;">
        건강한 하루는 나를 이해하는 것부터 🌱
    </div>
    <div style="font-size: 14px; color: #526D5D; margin-top: 8px;">
        나의 에너지 소비량과 주요 영양소를 살펴보세요.
    </div>
</div>
""", unsafe_allow_html=True)

# ── 신체 정보 입력 ──
st.subheader("🧍 신체 정보")
st.caption("아래 정보를 입력하고 분석하기 버튼을 눌러 주세요.")

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("성별", ["남성", "여성"])
        age = st.number_input(
            "나이 (세)", min_value=10, max_value=100, value=17
        )

    with col2:
        height = st.number_input(
            "키 (cm)", min_value=100.0, max_value=220.0,
            value=170.0, step=0.5
        )
        weight = st.number_input(
            "체중 (kg)", min_value=30.0, max_value=150.0,
            value=60.0, step=0.5
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

if st.button("✨ 분석 결과 확인하기", use_container_width=True):
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    # Mifflin-St Jeor 추정식
    if gender == "남성":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity_factors[activity_level]

    st.session_state["calculated_bmi"] = bmi
    st.session_state["calculated_bmr"] = bmr
    st.session_state["calculated_tdee"] = tdee
    st.session_state["calculated_age"] = age
    st.session_state["calculated_height"] = height
    st.session_state["calculated_weight"] = weight
    st.session_state["calculated_gender"] = gender
    st.session_state["calculated_activity"] = activity_level

# ── 대시보드 결과 ──
if "calculated_tdee" in st.session_state:
    bmi = st.session_state["calculated_bmi"]
    bmr = st.session_state["calculated_bmr"]
    tdee = st.session_state["calculated_tdee"]

    st.divider()
    st.subheader("📊 나의 에너지 요약")
    st.caption("입력한 정보로 계산한 추정값이에요.")

    c1, c2, c3 = st.columns(3)

    c1.metric("BMI", f"{bmi:.1f}")
    c2.metric("기초대사량", f"{bmr:,.0f} kcal")
    c3.metric("하루 총 에너지 소비량", f"{tdee:,.0f} kcal")

    age = st.session_state["calculated_age"]

    if age < 18:
        st.info(
            "BMI는 성장 단계에 따라 해석이 달라질 수 있어요. "
            "청소년은 성인 BMI 기준만으로 건강 상태를 판단하지 않아요."
        )
    else:
        st.caption(
            "BMI는 체중과 키로 계산한 지표이며, "
            "그 자체로 건강 상태를 확정하는 진단은 아닙니다."
        )

    # 영양소별 에너지 배분 예시
    carbs_g = (tdee * 0.5) / 4
    protein_g = (tdee * 0.3) / 4
    fat_g = (tdee * 0.2) / 9

    st.divider()
    st.subheader("🥑 영양소 에너지 배분")
    st.write("에너지의 50%·30%·20%를 각각 배분한 예시입니다.")

    chart_col, info_col = st.columns([1.1, 1])

    with chart_col:
        chart_data = pd.DataFrame({
            "영양소": ["탄수화물", "단백질", "지방"],
            "에너지 비율 (%)": [50, 30, 20]
        })
        st.bar_chart(
            chart_data,
            x="영양소",
            y="에너지 비율 (%)",
            color="#75A88C",
            height=260
        )

    with info_col:
        with st.container(border=True):
            st.markdown("#### 🍚 탄수화물")
            st.metric("계산상 배분량", f"{carbs_g:.1f} g")
            st.progress(0.5)

        with st.container(border=True):
            st.markdown("#### 🥚 단백질")
            st.metric("계산상 배분량", f"{protein_g:.1f} g")
            st.progress(0.3)

        with st.container(border=True):
            st.markdown("#### 🥑 지방")
            st.metric("계산상 배분량", f"{fat_g:.1f} g")
            st.progress(0.2)

    st.caption(
        "영양소 배분은 설명을 위한 계산 예시이며 개인별 권장 섭취량은 아닙니다."
    )

    st.divider()

    st.markdown("""
    <div style="background:#E7F1E8; padding:20px; border-radius:18px;">
        <div style="font-size:19px; color:#294B3D;">
            🥗 다음 단계: 나만의 식단 살펴보기
        </div>
        <div style="color:#526D5D; margin-top:6px;">
            계산한 하루 에너지 소비량을 식단 플래너에서 활용해 보세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.page_link(
        "pages/calculate.py",
        label="식단 플래너로 이동 →",
        icon="🥗",
        use_container_width=True
    )

else:
    st.info("👆 신체 정보를 입력하고 분석 버튼을 눌러 주세요.")

st.divider()
st.caption("NUTRIDAY · 나를 이해하는 건강 관리 프로젝트 🌿")
