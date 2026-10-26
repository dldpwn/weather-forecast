
import streamlit as st

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="NutriDay | 기초대사량 & 영양 가이드",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# 디자인
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    html, body, [class*="css"], p, label, h1, h2, h3, h4 {
        font-family: 'Gowun Dodum', sans-serif;
    }

    .stApp {
        background: #FBF9F1;
        color: #263B32;
    }

    [data-testid="stSidebar"] {
        background: #EEF6EF;
    }

    .main-title {
        color: #377D61;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: .25rem;
    }

    .sub-text {
        color: #69756E;
        margin-bottom: 1.2rem;
    }

    .info-card {
        background: #F0F7F0;
        border: 1px solid #DCEADF;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: .7rem;
    }

    div[data-testid="stMetric"] {
        background: #F0F7F0;
        border: 1px solid #DCEADF;
        border-radius: 14px;
        padding: 1rem;
    }

    div.stButton > button {
        background: #4D9274;
        color: white;
        border: 0;
        border-radius: 12px;
        padding: .65rem 1rem;
        font-weight: 700;
    }

    div.stButton > button:hover {
        background: #377D61;
        color: white;
        border: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")

    st.page_link(
        "main.py",
        label="🧪 기초대사량 & 영양 가이드"
    )

    st.page_link(
        "pages/calculate.py",
        label="🥗 한 달 맞춤 식단"
    )

# =========================================================
# 기초대사량 추정 함수
# =========================================================
def estimate_bmr(age, sex, height_cm, weight_kg):
    """
    연령대에 따라 기초대사량 추정식을 선택한다.

    3~9세: Schofield 체중 기반 추정식
    10~17세: Schofield 체중 기반 추정식
    18~64세: Mifflin-St Jeor 공식
    65세 이상: Schofield 고령자용 체중 기반 추정식

    계산 결과는 실제 측정값이 아닌 추정값이다.
    """

    if age < 3:
        return None, None

    if age < 10:
        if sex == "남성":
            bmr = 22.7 * weight_kg + 495
        else:
            bmr = 22.5 * weight_kg + 499

        formula_name = "Schofield (3~9세)"

    elif age < 18:
        if sex == "남성":
            bmr = 17.5 * weight_kg + 651
        else:
            bmr = 12.2 * weight_kg + 746

        formula_name = "Schofield (10~17세)"

    elif age < 65:
        if sex == "남성":
            bmr = (
                10 * weight_kg
                + 6.25 * height_cm
                - 5 * age
                + 5
            )
        else:
            bmr = (
                10 * weight_kg
                + 6.25 * height_cm
                - 5 * age
                - 161
            )

        formula_name = "Mifflin–St Jeor (18~64세)"

    else:
        if sex == "남성":
            bmr = 13.5 * weight_kg + 487
        else:
            bmr = 10.5 * weight_kg + 596

        formula_name = "Schofield (고령자용)"

    return max(0, bmr), formula_name


def age_group_label(age):
    if age < 3:
        return "영유아 (3세 미만)"
    elif age < 10:
        return "어린이 (3~9세)"
    elif age < 18:
        return "청소년 (10~17세)"
    elif age < 65:
        return "성인 (18~64세)"
    else:
        return "고령자 (65세 이상)"


# =========================================================
# 활동 수준
# =========================================================
ACTIVITY_FACTORS = {
    "낮음 (주로 앉아서 생활)": 1.2,
    "가벼움 (가벼운 활동·운동)": 1.375,
    "보통 (주 3~5회 정도 활동)": 1.55,
    "높음 (활동량이 많은 편)": 1.725,
    "매우 높음 (매우 높은 활동량)": 1.9,
}

# =========================================================
# 제목
# =========================================================
st.markdown(
    '<div class="main-title">'
    '🍎 내 몸의 에너지 균형: 기초대사량 & 영양 가이드'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-text">'
    '연령에 맞는 추정식을 사용해 기초대사량을 계산하고, '
    '활동 수준을 참고해 하루 에너지 필요량을 추정해 보세요.'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "기초대사량은 몸이 휴식 상태에서 생명 유지에 사용하는 "
    "에너지의 추정치예요. 아래 계산 결과는 장비로 직접 측정한 "
    "값이 아니며 실제 값과 차이가 날 수 있어요."
)

# =========================================================
# 사용자 입력
# =========================================================
st.markdown("### 📝 기본 정보 입력")

with st.form("bmr_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "나이 (세)",
            min_value=0,
            max_value=120,
            value=int(st.session_state.get("input_age", 25)),
            step=1,
            help="연령대에 따라 적용하는 공식이 달라져요.",
        )

        sex = st.selectbox(
            "계산 공식의 성별 구분",
            ["여성", "남성"],
            index=(
                0
                if st.session_state.get("input_sex", "여성") == "여성"
                else 1
            ),
            help="선택한 추정식에서 사용하는 성별 구분이에요.",
        )

    with col2:
        height_cm = st.number_input(
            "키 (cm)",
            min_value=30.0,
            max_value=250.0,
            value=float(
                st.session_state.get("input_height", 165.0)
            ),
            step=0.5,
        )

        weight_kg = st.number_input(
            "체중 (kg)",
            min_value=2.0,
            max_value=350.0,
            value=float(
                st.session_state.get("input_weight", 60.0)
            ),
            step=0.5,
        )

    activity = st.selectbox(
        "평소 활동 수준",
        list(ACTIVITY_FACTORS.keys()),
        index=list(ACTIVITY_FACTORS.keys()).index(
            st.session_state.get(
                "input_activity",
                "보통 (주 3~5회 정도 활동)"
            )
        ),
        help=(
            "활동 수준은 기초대사량 자체가 아니라 "
            "하루 에너지 필요량을 추정할 때 참고해요."
        ),
    )

    submitted = st.form_submit_button(
        "기초대사량 계산하기",
        use_container_width=True,
    )

# =========================================================
# 계산 실행
# =========================================================
if submitted:
    st.session_state["input_age"] = int(age)
    st.session_state["input_sex"] = sex
    st.session_state["input_height"] = float(height_cm)
    st.session_state["input_weight"] = float(weight_kg)
    st.session_state["input_activity"] = activity

    bmr, formula_name = estimate_bmr(
        int(age),
        sex,
        float(height_cm),
        float(weight_kg),
    )

    st.session_state["bmr_result"] = bmr
    st.session_state["formula_name"] = formula_name
    st.session_state["calculation_age_group"] = age_group_label(
        int(age)
    )

    if bmr is not None:
        # BMI는 참고용으로만 계산
        bmi = float(weight_kg) / (
            (float(height_cm) / 100) ** 2
        )

        # 기존 식단 페이지와 호환되는 세션 상태
        tdee = bmr * ACTIVITY_FACTORS[activity]

        st.session_state["calculated_bmi"] = round(bmi, 1)
        st.session_state["calculated_bmr"] = round(bmr)
        st.session_state["calculated_tdee"] = round(tdee)
        st.session_state["tdee"] = round(tdee)
        st.session_state["daily_calories"] = round(tdee)
        st.session_state["meal_plan_calories"] = round(tdee)

        st.session_state["calculated_age"] = int(age)
        st.session_state["calculated_height"] = float(height_cm)
        st.session_state["calculated_weight"] = float(weight_kg)
        st.session_state["calculated_gender"] = sex
        st.session_state["calculated_activity"] = activity

    else:
        # 영유아는 일반 계산식을 적용하지 않음
        for key in [
            "calculated_bmr",
            "calculated_tdee",
            "tdee",
            "daily_calories",
            "meal_plan_calories",
        ]:
            st.session_state.pop(key, None)

# =========================================================
# 결과 표시
# =========================================================
bmr_result = st.session_state.get(
    "bmr_result",
    "not_calculated"
)

if bmr_result is not None and bmr_result != "not_calculated":
    bmr_value = float(bmr_result)
    tdee_value = float(
        st.session_state.get("calculated_tdee", 0)
    )

    formula_name = st.session_state.get(
        "formula_name",
        "연령별 추정식"
    )

    age_now = int(
        st.session_state.get("calculated_age", age)
    )

    st.divider()
    st.markdown("### 📊 계산 결과")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "추정 기초대사량",
        f"{bmr_value:,.0f} kcal/일"
    )

    metric2.metric(
        "추정 하루 에너지 필요량",
        f"{tdee_value:,.0f} kcal/일"
    )

    metric3.metric(
        "적용 연령대",
        st.session_state.get(
            "calculation_age_group",
            "-"
        )
    )

    st.markdown(
        f"""
        <div class="info-card">
            <strong>적용한 계산 공식</strong><br>
            {formula_name}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if age_now < 18:
        st.warning(
            "성장기에는 성장과 발달에 필요한 에너지도 고려해야 해요. "
            "여기에 표시되는 하루 에너지 필요량은 성인용 활동계수를 "
            "활용한 단순 참고치이며, 성장기 에너지 필요량을 정확히 "
            "평가한 값이 아니에요. 체중 감량을 위한 열량 제한에 "
            "사용하지 마세요."
        )

    elif age_now >= 65:
        st.caption(
            "고령자의 에너지 필요량은 건강 상태, 활동 수준, "
            "체성분 등에 따라 달라질 수 있어요. "
            "이 값은 참고용 추정치예요."
        )

    st.markdown("#### 계산 방식")

    st.write(
        f"- 추정 기초대사량: **{bmr_value:,.0f} kcal/일**"
    )

    current_activity = st.session_state.get(
        "calculated_activity",
        activity
    )

    st.write(
        f"- 적용 활동계수: "
        f"**{ACTIVITY_FACTORS[current_activity]:.3g}**"
    )

    st.write(
        f"- 추정 하루 에너지 필요량: "
        f"기초대사량 × 활동계수 = "
        f"**{tdee_value:,.0f} kcal/일**"
    )

    st.markdown("#### 다음 단계")

    st.write(
        "계산한 하루 에너지 참고값은 한 달 맞춤 식단 페이지로 "
        "전달돼요. 식단을 구성할 때는 선호 음식, 알레르기, "
        "제외 식품도 함께 고려해 주세요."
    )

elif bmr_result is None:
    st.warning(
        "3세 미만 영유아에게는 이 화면의 일반 기초대사량 "
        "계산식을 적용하지 않아요. 성장 단계에 맞는 에너지 "
        "필요량과 식단은 소아·영양 전문가의 안내를 참고해 주세요."
    )

# =========================================================
# 공식 및 계산 한계 안내
# =========================================================
with st.expander("공식과 계산 결과에 대한 안내"):
    st.markdown(
        """
        - **Mifflin–St Jeor 공식**은 성인 연구 자료를 바탕으로
          개발된 안정 시 에너지 소비량 추정식이에요.
        - **Schofield 추정식**은 연령과 성별 구간에 따라 체중 등을
          이용해 기초대사량을 추정해요.
        - 공식은 집단 자료에 기반한 추정식이므로 개인의 실제
          기초대사량과 차이가 날 수 있어요.
        - 임신·수유 중이거나 특정 질환이 있는 경우에는 계산 결과를
          개인별 영양 처방으로 사용하지 말고 전문가와 상담해 주세요.
        - 어린이·청소년의 하루 에너지 필요량은 성장에 필요한
          에너지를 고려해야 하므로, 성인용 활동계수 곱셈만으로
          정확하게 계산할 수 없어요.
        """
    )

    st.markdown(
        """
        **참고 자료**
        
        - Mifflin et al., *A new predictive equation for resting
          energy expenditure in healthy individuals*,
          The American Journal of Clinical Nutrition, 1990.
        - Health Canada, *Dietary Reference Intakes Tables:
          Equations to Estimate Energy Requirement*.
        """
    )

st.caption(
    "NutriDay는 교육용 참고 도구이며 의료 진단이나 "
    "개인별 영양 처방을 대신하지 않아요."
)
