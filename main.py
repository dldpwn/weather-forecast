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

    [data-testid="stSidebarNav"] {
        display: none;
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

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: #4D9274;
        color: white;
        border: 0;
        border-radius: 12px;
        padding: .65rem 1rem;
        font-weight: 700;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
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
    기존 기초대사량 추정식을 유지한다.

    3~9세: Schofield 체중 기반 추정식
    10~17세: Schofield 체중 기반 추정식
    18~64세: Mifflin-St Jeor 공식
    65세 이상: 기존 고령자용 체중 기반 추정식

    실제 측정값이 아닌 추정값이다.
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
        return "3세 미만"
    elif age < 10:
        return "어린이 (3~9세)"
    elif age < 19:
        return "청소년 (10~18세)"
    elif age < 65:
        return "성인 (19~64세)"
    else:
        return "고령 성인 (65세 이상)"


# =========================================================
# EER 신체활동 수준
# =========================================================
PAL_OPTIONS = [
    "비활동적 (Inactive)",
    "저활동적 (Low active)",
    "활동적 (Active)",
    "매우 활동적 (Very active)",
]

PAL_ENGLISH = {
    "비활동적 (Inactive)": "inactive",
    "저활동적 (Low active)": "low_active",
    "활동적 (Active)": "active",
    "매우 활동적 (Very active)": "very_active",
}


# =========================================================
# 하루 에너지 필요량(EER) 추정 함수
# =========================================================
def estimate_eer(age, sex, height_cm, weight_kg, pal_category):
    """
    National Academies / Health Canada 2023 EER 공식.

    3~18세: 성장 에너지 항을 포함한 연령별 공식
    19세 이상: 성인 연령별 공식

    걷기·운동 기록을 열량으로 별도 합산하지 않는다.
    활동 수준은 사용자가 선택한 PAL 분류를 사용한다.
    """
    if age < 3:
        return None, None

    pal = PAL_ENGLISH[pal_category]
    h = float(height_cm)
    w = float(weight_kg)
    a = float(age)

    # -----------------------------------------------------
    # 어린이 및 청소년: 3~18세
    # -----------------------------------------------------
    if age < 19:

        # 성장에 필요한 에너지 항
        if age < 4:
            growth = 20 if sex == "남성" else 15
            age_band = "3세 이상~4세 미만"

        elif age < 9:
            growth = 15
            age_band = "4~8세"

        elif age < 14:
            growth = 25 if sex == "남성" else 30
            age_band = "9~13세"

        else:
            growth = 20
            age_band = "14~18세"

        if sex == "남성":
            coefficients = {
                "inactive": (-447.51, 3.68, 13.01, 13.15),
                "low_active": (19.12, 3.68, 8.62, 20.28),
                "active": (-388.19, 3.68, 12.66, 20.46),
                "very_active": (-671.75, 3.68, 15.38, 23.25),
            }
        else:
            coefficients = {
                "inactive": (55.59, -22.25, 8.43, 17.07),
                "low_active": (-297.54, -22.25, 12.77, 14.73),
                "active": (-189.55, -22.25, 11.74, 18.34),
                "very_active": (-709.59, -22.25, 18.22, 14.25),
            }

        constant, age_coef, height_coef, weight_coef = (
            coefficients[pal]
        )

        eer = (
            constant
            + age_coef * a
            + height_coef * h
            + weight_coef * w
            + growth
        )

        formula = (
            f"NASEM/Health Canada 2023 EER "
            f"({age_band}, 성장 에너지 포함)"
        )

    # -----------------------------------------------------
    # 성인: 19세 이상
    # -----------------------------------------------------
    else:
        if sex == "남성":
            coefficients = {
                "inactive": (753.07, -10.83, 6.50, 14.10),
                "low_active": (581.47, -10.83, 8.30, 14.94),
                "active": (1004.82, -10.83, 6.52, 15.91),
                "very_active": (-517.88, -10.83, 15.61, 19.11),
            }
        else:
            coefficients = {
                "inactive": (584.90, -7.01, 5.72, 11.71),
                "low_active": (575.77, -7.01, 6.60, 12.14),
                "active": (710.25, -7.01, 6.54, 12.34),
                "very_active": (511.83, -7.01, 9.07, 12.56),
            }

        constant, age_coef, height_coef, weight_coef = (
            coefficients[pal]
        )

        eer = (
            constant
            + age_coef * a
            + height_coef * h
            + weight_coef * w
        )

        formula = "NASEM/Health Canada 2023 EER (19세 이상 성인)"

    return max(0, eer), formula


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
    '활동 수준과 개인별 활동 기록을 참고해 '
    '하루 에너지 필요량을 추정해 보세요.'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "기초대사량과 하루 에너지 필요량은 입력 정보를 바탕으로 "
    "계산한 추정치예요. 실제 에너지 소비량을 직접 측정한 값은 "
    "아니며 개인차가 있을 수 있어요."
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
            help="연령대에 따라 적용하는 추정식이 달라져요.",
        )

        sex = st.selectbox(
            "계산 공식의 성별 구분",
            ["여성", "남성"],
            index=(
                0
                if st.session_state.get("input_sex", "여성") == "여성"
                else 1
            ),
            help="선택한 참고 공식에서 사용하는 성별 구분이에요.",
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

    # -----------------------------------------------------
    # 공식에 적용할 활동 수준
    # -----------------------------------------------------
    st.markdown("#### 🚶 활동 수준")

    default_pal = st.session_state.get(
        "input_pal",
        "저활동적 (Low active)"
    )

    if default_pal not in PAL_OPTIONS:
        default_pal = "저활동적 (Low active)"

    pal_category = st.selectbox(
        "평소 하루 전체 활동 수준",
        PAL_OPTIONS,
        index=PAL_OPTIONS.index(default_pal),
        help=(
            "운동 횟수뿐 아니라 걷기, 이동, 서 있는 시간 등 "
            "하루 전체 활동을 고려해 선택해요. "
            "이 선택은 EER 공식에 직접 반영돼요."
        ),
    )

    # -----------------------------------------------------
    # 개인별 활동 기록
    # -----------------------------------------------------
    st.markdown("#### 🗓️ 개인별 활동 기록 (참고용)")

    activity_col1, activity_col2, activity_col3 = st.columns(3)

    walking_options = [
        "30분 미만",
        "30~60분",
        "60분 초과",
    ]

    exercise_frequency_options = [
        "0~1회",
        "2회",
        "3~4회",
        "5회 이상",
    ]

    intensity_options = [
        "가벼운 강도",
        "중간 강도",
        "높은 강도",
        "운동하지 않음",
    ]

    with activity_col1:
        walking_time = st.selectbox(
            "하루 걷기·이동 시간",
            walking_options,
            index=walking_options.index(
                st.session_state.get(
                    "input_walking_time",
                    "30~60분"
                )
            ) if st.session_state.get(
                "input_walking_time", "30~60분"
            ) in walking_options else 1,
        )

    with activity_col2:
        exercise_frequency = st.selectbox(
            "주당 운동 횟수",
            exercise_frequency_options,
            index=exercise_frequency_options.index(
                st.session_state.get(
                    "input_exercise_frequency",
                    "3~4회"
                )
            ) if st.session_state.get(
                "input_exercise_frequency", "3~4회"
            ) in exercise_frequency_options else 2,
        )

    with activity_col3:
        exercise_intensity = st.selectbox(
            "주된 운동 강도",
            intensity_options,
            index=intensity_options.index(
                st.session_state.get(
                    "input_exercise_intensity",
                    "중간 강도"
                )
            ) if st.session_state.get(
                "input_exercise_intensity", "중간 강도"
            ) in intensity_options else 1,
        )

    daily_movement_options = [
        "주로 앉아서 생활함",
        "앉아 있는 시간과 걷기·이동이 섞여 있음",
        "하루 중 걷거나 서 있는 시간이 많은 편",
    ]

    daily_movement = st.selectbox(
        "운동 외 일상 활동",
        daily_movement_options,
        index=daily_movement_options.index(
            st.session_state.get(
                "input_daily_movement",
                "앉아 있는 시간과 걷기·이동이 섞여 있음"
            )
        ) if st.session_state.get(
            "input_daily_movement",
            "앉아 있는 시간과 걷기·이동이 섞여 있음"
        ) in daily_movement_options else 1,
        help=(
            "활동 기록을 해석할 때 참고해요. "
            "이 항목들이 자동으로 열량을 더하거나 "
            "활동 수준을 확정하지는 않아요."
        ),
    )

    submitted = st.form_submit_button(
        "기초대사량과 하루 에너지 필요량 계산하기",
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
    st.session_state["input_pal"] = pal_category

    st.session_state["input_walking_time"] = walking_time
    st.session_state["input_exercise_frequency"] = exercise_frequency
    st.session_state["input_exercise_intensity"] = exercise_intensity
    st.session_state["input_daily_movement"] = daily_movement

    bmr, bmr_formula_name = estimate_bmr(
        int(age),
        sex,
        float(height_cm),
        float(weight_kg),
    )

    eer, eer_formula_name = estimate_eer(
        int(age),
        sex,
        float(height_cm),
        float(weight_kg),
        pal_category,
    )

    st.session_state["bmr_result"] = bmr
    st.session_state["formula_name"] = bmr_formula_name
    st.session_state["eer_formula_name"] = eer_formula_name

    st.session_state["calculation_age_group"] = age_group_label(
        int(age)
    )

    if bmr is not None and eer is not None:
        bmi = float(weight_kg) / (
            (float(height_cm) / 100) ** 2
        )

        # 기존 식단 페이지와 호환되도록 기존 키를 유지한다.
        # EER에는 선택한 활동 수준이 이미 반영되어 있다.
        # 따라서 BMR에 활동계수를 곱하거나 운동 열량을 다시 더하지 않는다.
        st.session_state["calculated_bmi"] = round(bmi, 1)
        st.session_state["calculated_bmr"] = round(bmr)

        st.session_state["calculated_eer"] = round(eer)
        st.session_state["calculated_tdee"] = round(eer)
        st.session_state["tdee"] = round(eer)
        st.session_state["daily_calories"] = round(eer)
        st.session_state["meal_plan_calories"] = round(eer)

        st.session_state["calculated_age"] = int(age)
        st.session_state["calculated_height"] = float(height_cm)
        st.session_state["calculated_weight"] = float(weight_kg)
        st.session_state["calculated_gender"] = sex
        st.session_state["calculated_activity"] = pal_category

        st.session_state["calculated_walking_time"] = walking_time
        st.session_state["calculated_exercise_frequency"] = exercise_frequency
        st.session_state["calculated_exercise_intensity"] = exercise_intensity
        st.session_state["calculated_daily_movement"] = daily_movement

    else:
        # 3세 미만은 현재 UI에서 계산하지 않는다.
        for key in [
            "calculated_bmr",
            "calculated_eer",
            "calculated_tdee",
            "tdee",
            "daily_calories",
            "meal_plan_calories",
            "calculated_bmi",
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
    eer_value = float(
        st.session_state.get("calculated_eer", 0)
    )

    age_now = int(
        st.session_state.get("calculated_age", age)
    )

    current_pal = st.session_state.get(
        "calculated_activity",
        pal_category
    )

    st.divider()
    st.markdown("### 📊 계산 결과")

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "추정 기초대사량",
        f"{bmr_value:,.0f} kcal/일"
    )

    metric2.metric(
        "예상 하루 에너지 필요량",
        f"{eer_value:,.0f} kcal/일"
    )

    metric3.metric(
        "적용 연령대",
        st.session_state.get(
            "calculation_age_group",
            "-"
        )
    )

    st.markdown(
        f'<div class="info-card">'
        f'<strong>하루 에너지 필요량 계산 기준</strong><br>'
        f"{st.session_state.get('eer_formula_name', '연령별 EER 추정식')}<br>"
        f"활동 수준: {current_pal}</div>",
        unsafe_allow_html=True,
    )

    if age_now < 19:
        st.warning(
            "어린이·청소년용 EER 공식에는 성장에 필요한 에너지 항이 "
            "포함되어 있어요. 그래도 개인의 실제 필요량과 차이가 날 수 "
            "있으므로, 이 값으로 섭취량을 엄격하게 제한하지 마세요."
        )
    else:
        st.caption(
            "EER은 연령·성별·키·체중·활동 수준을 바탕으로 한 추정값이며, "
            "개인의 실제 에너지 소비량을 직접 측정한 값은 아니에요."
        )

    # -----------------------------------------------------
    # 활동 기록 표시
    # -----------------------------------------------------
    st.markdown("#### 🚶 활동 기록 확인")

    st.write(
        f"- 하루 걷기·이동 시간: "
        f"**{st.session_state.get('calculated_walking_time', walking_time)}**"
    )

    st.write(
        f"- 주당 운동 횟수: "
        f"**{st.session_state.get('calculated_exercise_frequency', exercise_frequency)}**"
    )

    st.write(
        f"- 주된 운동 강도: "
        f"**{st.session_state.get('calculated_exercise_intensity', exercise_intensity)}**"
    )

    st.write(
        f"- 운동 외 일상 활동: "
        f"**{st.session_state.get('calculated_daily_movement', daily_movement)}**"
    )

    st.info(
        "활동 기록은 선택한 활동 수준이 생활 패턴과 대체로 맞는지 "
        "확인하기 위한 참고 자료예요. 이 기록만으로 EER 활동 수준을 "
        "자동 확정하지 않으며, EER에 반영된 활동을 다시 열량으로 더하지 않아요."
    )

    st.markdown("#### 계산 결과 활용")

    st.write(
        f"예상 하루 에너지 필요량 **{eer_value:,.0f} kcal/일**을 "
        "기존 한 달 맞춤 식단 페이지로 전달해요. 식단은 참고 추정값뿐 "
        "아니라 식품 다양성과 영양 균형을 함께 고려해 주세요."
    )

elif bmr_result is None:
    st.warning(
        "3세 미만은 개월 단위 나이와 별도 영유아 입력이 필요해 "
        "현재 화면에서 계산하지 않아요. 영유아의 에너지 필요량과 "
        "식단은 소아·영양 전문가의 안내를 참고해 주세요."
    )


# =========================================================
# 공식 및 계산 한계 안내
# =========================================================
with st.expander("공식과 계산 결과에 대한 안내"):
    st.markdown(
        """
        - **기초대사량(BMR)** 은 기존의 연령별 추정식을 이용한 참고값이에요.
        - **예상 하루 에너지 필요량(EER)** 은 National Academies of
          Sciences, Engineering, and Medicine의 2023년 에너지 DRI 자료와
          Health Canada가 공개한 공식을 바탕으로 계산해요.
        - 3~18세 공식은 성장에 필요한 에너지를 포함하며,
          19세 이상은 성인 EER 공식을 사용해요.
        - 활동 기록(걷기 시간, 운동 횟수, 강도)은 활동 수준을 검토하는
          참고 자료예요. 기록만으로 공식의 활동 수준을 자동 판정하지 않아요.
        - EER 공식에는 선택한 활동 수준이 이미 반영되므로,
          운동 열량을 별도로 더하거나 BMR에 활동계수를 곱하지 않아요.
        - 공식은 집단 자료를 바탕으로 한 추정식이므로 개인의 실제
          에너지 소비량과 차이가 날 수 있어요.
        - 이 자료는 미국·캐나다의 DRI 기준을 바탕으로 하며,
          한국인에게 적용할 때는 한국인 영양소 섭취기준과의 적합성도
          별도로 검토할 필요가 있어요.
        - 임신·수유 중이거나 특정 질환이 있는 경우, 또는 개인별 식단
          처방이 필요한 경우에는 전문가의 안내를 참고해 주세요.
        """
    )

st.caption(
    "NutriDay는 교육용 참고 도구이며 의료 진단이나 "
    "개인별 영양 처방을 대신하지 않아요."
)
