import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="맞춤형 식단 플래너 | NutriDay",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 디자인 설정
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, p, label,
h1, h2, h3, h4, h5, h6,
.stMarkdown,
[data-testid="stMetricValue"],
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

.stButton > button {
    background-color: #4F8069;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1rem;
}

.stButton > button:hover {
    background-color: #294B3D;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# 사이드바 메뉴
with st.sidebar:
    st.title("🥗 NutriDay")

    st.page_link(
        "main.py",
        label="내 영양 대시보드",
        icon="🏠"
    )

    st.page_link(
        "pages/calculate.py",
        label="맞춤형 식단 플래너",
        icon="🍽️"
    )


# 페이지 제목
st.title("🍽️ 맞춤형 식단 플래너")
st.caption("나의 목표와 에너지 필요량을 참고해 식단을 살펴보세요.")

# 상단 배너
st.markdown("""
<div style="
    background: linear-gradient(120deg, #DDEFE5, #F1F4E8);
    padding: 28px;
    border-radius: 22px;
    margin-bottom: 24px;
">
    <h2 style="margin: 0; color: #294B3D;">
        오늘의 식단 계획
    </h2>
    <p style="margin: 8px 0 0; color: #496858;">
        목표에 맞는 에너지와 영양소 구성을 확인해 보세요.
    </p>
</div>
""", unsafe_allow_html=True)


# 식단 목표 설정
st.subheader("📝 나의 식단 목표")

# 메인 페이지에서 계산한 에너지 소비 추정량 가져오기
default_tdee = st.session_state.get(
    "calculated_tdee",
    2000.0
)

default_tdee = max(
    1000.0,
    min(4000.0, float(default_tdee))
)

with st.container(border=True):
    target_tdee = st.number_input(
        "하루 에너지 소비 추정량 (kcal)",
        min_value=1000,
        max_value=4000,
        value=int(default_tdee),
        step=50
    )

    goal = st.selectbox(
        "식단 목표 선택",
        [
            "에너지 균형 참고하기",
            "체중 감량 목표 참고 (-500 kcal)",
            "근육 증가 목표 참고 (+300 kcal)"
        ]
    )

    st.caption(
        "계산 결과는 참고용입니다. 특히 성장기에는 "
        "체중 감량이나 증량을 위한 열량 조절을 임의로 하지 마세요."
    )


# 목표에 따른 에너지 계산
if "감량" in goal:
    final_calories = target_tdee - 500

elif "증가" in goal:
    final_calories = target_tdee + 300

else:
    final_calories = target_tdee


# 식단 계산 버튼
if st.button("식단 구성 확인하기", use_container_width=True):
    st.session_state["meal_plan_calories"] = final_calories
    st.session_state["meal_plan_goal"] = goal


# 계산 결과 표시
if "meal_plan_calories" in st.session_state:

    calories = st.session_state["meal_plan_calories"]

    st.divider()
    st.subheader("📊 영양소 에너지 비율")

    # 영양소별 에너지 비율
    carb_ratio = 50
    protein_ratio = 30
    fat_ratio = 20

    # 에너지 비율을 기준으로 한 영양소별 양 계산
    carb_grams = calories * carb_ratio / 100 / 4
    protein_grams = calories * protein_ratio / 100 / 4
    fat_grams = calories * fat_ratio / 100 / 9

    # 주요 수치 카드
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "하루 에너지 참고값",
            f"{calories:,.0f} kcal"
        )

    with col2:
        st.metric(
            "탄수화물",
            f"{carb_grams:.0f} g"
        )

    with col3:
        st.metric(
            "단백질",
            f"{protein_grams:.0f} g"
        )

    st.metric(
        "지방",
        f"{fat_grams:.0f} g"
    )

    # 도넛형 원형 그래프
    chart_data = pd.DataFrame({
        "영양소": ["탄수화물", "단백질", "지방"],
        "에너지 비율": [
            carb_ratio,
            protein_ratio,
            fat_ratio
        ]
    })

    fig = px.pie(
        chart_data,
        names="영양소",
        values="에너지 비율",
        hole=0.55,
        color="영양소",
        color_discrete_map={
            "탄수화물": "#75A88C",
            "단백질": "#B7DCC8",
            "지방": "#E9CFA6"
        }
    )

    fig.update_traces(
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="%{label}: %{percent}<extra></extra>",
        marker=dict(
            line=dict(
                color="#FAF9F3",
                width=3
            )
        )
    )

    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(
            t=40,
            b=40,
            l=40,
            r=40
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Gowun Dodum, sans-serif",
            color="#294B3D"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "탄수화물 50%, 단백질 30%, 지방 20%로 설정한 예시입니다. "
        "개인에게 필요한 영양소 비율은 성장 상태와 활동량 등에 따라 달라질 수 있습니다."
    )

    # 식단 예시
    st.divider()
    st.subheader("🥣 하루 식단 예시")

    breakfast, lunch, dinner = st.tabs([
        "🌞 아침",
        "☀️ 점심",
        "🌙 저녁"
    ])

    with breakfast:
        st.markdown("### 아침 식사")
        st.write("- 통곡물빵 또는 오트밀")
        st.write("- 달걀이나 두부")
        st.write("- 과일과 우유 또는 두유")

        st.progress(
            0.30,
            text="하루 에너지의 약 30%를 배분한 예시"
        )

    with lunch:
        st.markdown("### 점심 식사")
        st.write("- 밥")
        st.write("- 생선, 닭고기 또는 콩류")
        st.write("- 다양한 채소 반찬")

        st.progress(
            0.40,
            text="하루 에너지의 약 40%를 배분한 예시"
        )

    with dinner:
        st.markdown("### 저녁 식사")
        st.write("- 밥 또는 감자 등 곡류·전분 식품")
        st.write("- 단백질 식품")
        st.write("- 채소와 과일")

        st.progress(
            0.30,
            text="하루 에너지의 약 30%를 배분한 예시"
        )

    st.caption(
        "식단 예시는 참고용이며, 실제 필요한 식사량과 구성은 개인마다 다릅니다."
    )


# 하단 안내
st.divider()

st.markdown("""
<div style="
    background-color: #EAF3EC;
    padding: 20px;
    border-radius: 16px;
">
    <h3 style="margin-top: 0;">🌿 건강한 식생활을 위한 안내</h3>
    <p style="margin-bottom: 0;">
        한 끼의 영양소 비율에만 집중하기보다 다양한 식품을 골고루 먹고,
        규칙적인 식사와 충분한 휴식을 함께 챙기는 것이 중요합니다.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

st.page_link(
    "main.py",
    label="🏠 메인 페이지로 돌아가기",
    use_container_width=True
)
