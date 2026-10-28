
import streamlit as st
from supabase import create_client, Client

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="NutriDay | 기초대사량 & 영양 가이드",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
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
    div.stFormSubmitButton > button {
        background: #4D9274;
        color: white;
        border: 0;
        border-radius: 12px;
        padding: .65rem 1rem;
        font-weight: 700;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: #377D61;
        color: white;
        border: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Supabase 연결
# =========================================================
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


try:
    supabase = get_supabase_client()
except Exception:
    st.error(
        "Supabase 연결 설정을 확인해 주세요. "
        "Streamlit Secrets에 SUPABASE_URL과 SUPABASE_KEY가 "
        "등록되어 있는지 확인해 주세요."
    )
    st.stop()

# =========================================================
# 세션 초기화
# =========================================================
for key in [
    "auth_access_token",
    "auth_refresh_token",
    "auth_email",
]:
    if key not in st.session_state:
        st.session_state[key] = None


# =========================================================
# 로그인 및 회원가입 화면
# =========================================================
def show_auth_page():
    st.markdown(
        '<div class="main-title">🥗 NutriDay</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-text">'
        '나에게 맞는 하루 영양 관리, 지금 시작해 보세요.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### 🌿 계정 로그인")

    login_tab, signup_tab = st.tabs(["로그인", "회원가입"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input(
                "이메일",
                placeholder="example@email.com",
            )
            login_password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호 입력",
            )
            login_submitted = st.form_submit_button(
                "로그인",
                use_container_width=True,
            )

        if login_submitted:
            if not login_email.strip() or not login_password:
                st.warning("이메일과 비밀번호를 모두 입력해 주세요.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": login_email.strip(),
                        "password": login_password,
                    })

                    if response.session:
                        st.session_state["auth_access_token"] = (
                            response.session.access_token
                        )
                        st.session_state["auth_refresh_token"] = (
                            response.session.refresh_token
                        )
                        st.session_state["auth_email"] = (
                            response.user.email
                        )

                        st.success("로그인되었습니다!")
                        st.rerun()
                    else:
                        st.error(
                            "로그인 세션을 확인할 수 없어요. "
                            "다시 시도해 주세요."
                        )
                except Exception:
                    st.error(
                        "로그인에 실패했어요. 이메일과 비밀번호를 "
                        "확인해 주세요. 이메일 인증이 필요한 계정이라면 "
                        "먼저 이메일 인증을 완료해 주세요."
                    )

    with signup_tab:
        with st.form("signup_form"):
            signup_email = st.text_input(
                "이메일",
                placeholder="example@email.com",
                key="signup_email",
            )
            signup_password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="6자 이상 권장",
                key="signup_password",
            )
            signup_password_confirm = st.text_input(
                "비밀번호 확인",
                type="password",
                placeholder="비밀번호 다시 입력",
            )
            signup_submitted = st.form_submit_button(
                "회원가입",
                use_container_width=True,
            )

        if signup_submitted:
            email = signup_email.strip()

            if not email or not signup_password:
                st.warning("이메일과 비밀번호를 입력해 주세요.")
            elif signup_password != signup_password_confirm:
                st.warning("비밀번호가 서로 일치하지 않아요.")
            elif len(signup_password) < 6:
                st.warning("비밀번호를 6자 이상으로 설정해 주세요.")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": signup_password,
                    })

                    if response.session:
                        st.session_state["auth_access_token"] = (
                            response.session.access_token
                        )
                        st.session_state["auth_refresh_token"] = (
                            response.session.refresh_token
                        )
                        st.session_state["auth_email"] = (
                            response.user.email
                        )
                        st.success("회원가입이 완료되었습니다!")
                        st.rerun()
                    else:
                        st.success(
                            "회원가입 요청이 완료되었어요. "
                            "이메일 인증 안내가 도착했다면 인증 후 로그인해 주세요."
                        )
                except Exception:
                    st.error(
                        "회원가입에 실패했어요. 이메일 형식이 올바른지, "
                        "이미 가입된 이메일인지 확인해 주세요."
                    )

    st.caption(
        "NutriDay는 교육용 영양 관리 도구이며 "
        "의료 진단이나 개인별 영양 처방을 대신하지 않아요."
    )


# =========================================================
# 로그인 세션 복원
# =========================================================
is_logged_in = False

access_token = st.session_state.get("auth_access_token")
refresh_token = st.session_state.get("auth_refresh_token")

if access_token and refresh_token:
    try:
        session_response = supabase.auth.set_session(
            access_token,
            refresh_token,
        )
        session = getattr(session_response, "session", None)

        if session:
            st.session_state["auth_access_token"] = session.access_token
            st.session_state["auth_refresh_token"] = session.refresh_token

            user = getattr(session_response, "user", None)
            if user is not None:
                st.session_state["auth_email"] = (
                    getattr(user, "email", None)
                    or st.session_state.get("auth_email")
                )

            is_logged_in = True
    except Exception:
        for key in [
            "auth_access_token",
            "auth_refresh_token",
            "auth_email",
        ]:
            st.session_state.pop(key, None)

if not is_logged_in:
    show_auth_page()
    st.stop()


# =========================================================
# 공통 사이드바
# =========================================================
with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")
    st.divider()

    email = st.session_state.get("auth_email")

    st.markdown("### 👤 내 계정")
    st.caption(email or "계정 이메일을 확인할 수 없어요.")

    st.divider()

    st.page_link(
        "main.py",
        label="🧪 기초대사량 & 영양 가이드",
    )
    st.page_link(
        "pages/calculate.py",
        label="🥗 한 달 맞춤 식단",
    )

    st.divider()

    if st.button(
        "로그아웃",
        key="main_logout",
        use_container_width=True,
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        for key in [
            "auth_access_token",
            "auth_refresh_token",
            "auth_email",
        ]:
            st.session_state.pop(key, None)

        st.rerun()


# =========================================================
# 기초대사량 추정 함수
# =========================================================
def estimate_bmr(age, sex, height_cm, weight_kg):
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
    return "고령 성인 (65세 이상)"


# =========================================================
# EER 활동 수준
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


def estimate_eer(age, sex, height_cm, weight_kg, pal_category):
    if age < 3:
        return None, None

    pal = PAL_ENGLISH[pal_category]
    h = float(height_cm)
    w = float(weight_kg)
    a = float(age)

    if age < 19:
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

        constant, age_coef, height_coef, weight_coef = coefficients[pal]

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

    else:
        if sex == "남성":
            constant = 753.07
            age_coef = -10.83
            height_coef = 6.50
            weight_coef = 14.10
            pa_factors = {
                "inactive": 1.00,
                "low_active": 1.11,
                "active": 1.25,
                "very_active": 1.48,
            }
        else:
            constant = 584.90
            age_coef = -7.01
            height_coef = 5.72
            weight_coef = 11.71
            pa_factors = {
                "inactive": 1.00,
                "low_active": 1.12,
                "active": 1.27,
                "very_active": 1.45,
            }

        pa = pa_factors[pal]
        eer = (
            constant
            + age_coef * a
            + pa * (height_coef * h + weight_coef * w)
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
            help="기초대사량과 EER은 연령대에 맞는 추정식을 사용해요.",
        )

        previous_sex = st.session_state.get("input_sex", "여성")
        sex = st.selectbox(
            "계산 공식의 성별 구분",
            ["여성", "남성"],
            index=0 if previous_sex == "여성" else 1,
            help="선택한 참고 공식에서 사용하는 성별 구분이에요.",
        )

    with col2:
        height_cm = st.number_input(
            "키 (cm)",
            min_value=30.0,
            max_value=250.0,
            value=float(st.session_state.get("input_height", 165.0)),
            step=0.5,
        )
        weight_kg = st.number_input(
            "체중 (kg)",
            min_value=2.0,
            max_value=350.0,
            value=float(st.session_state.get("input_weight", 60.0)),
            step=0.5,
        )

    st.markdown("#### 🚶 활동 수준")

    default_pal = st.session_state.get(
        "input_pal",
        "저활동적 (Low active)",
    )
    if default_pal not in PAL_OPTIONS:
        default_pal = "저활동적 (Low active)"

    pal_category = st.selectbox(
        "평소 하루 전체 활동 수준",
        PAL_OPTIONS,
        index=PAL_OPTIONS.index(default_pal),
        help=(
            "운동 횟수만이 아니라 걷기, 이동, 서 있는 시간 등 "
            "하루 전체 활동을 고려해 선택해요. "
            "선택한 수준은 EER 공식에 직접 반영돼요."
        ),
    )

    st.markdown("#### 🗓️ 개인별 활동 기록 (참고용)")

    activity_col1, activity_col2, activity_col3 = st.columns(3)

    walking_options = ["30분 미만", "30~60분", "60분 초과"]
    frequency_options = ["0~1회", "2회", "3~4회", "5회 이상"]
    intensity_options = [
        "가벼운 강도",
        "중간 강도",
        "높은 강도",
        "운동하지 않음",
    ]

    with activity_col1:
        previous_walking = st.session_state.get(
            "input_walking_time", "30~60분"
        )
        walking_time = st.selectbox(
            "하루 걷기·이동 시간",
            walking_options,
            index=(
                walking_options.index(previous_walking)
                if previous_walking in walking_options else 1
            ),
        )

    with activity_col2:
        previous_frequency = st.session_state.get(
            "input_exercise_frequency", "3~4회"
        )
        exercise_frequency = st.selectbox(
            "주당 운동 횟수",
            frequency_options,
            index=(
                frequency_options.index(previous_frequency)
                if previous_frequency in frequency_options else 2
            ),
        )

    with activity_col3:
        previous_intensity = st.session_state.get(
            "input_exercise_intensity", "중간 강도"
        )
        exercise_intensity = st.selectbox(
            "주된 운동 강도",
            intensity_options,
            index=(
                intensity_options.index(previous_intensity)
                if previous_intensity in intensity_options else 1
            ),
        )

    movement_options = [
        "주로 앉아서 생활함",
        "앉아 있는 시간과 걷기·이동이 섞여 있음",
        "하루 중 걷거나 서 있는 시간이 많은 편",
    ]
    previous_movement = st.session_state.get(
        "input_daily_movement",
        "앉아 있는 시간과 걷기·이동이 섞여 있음",
    )
    daily_movement = st.selectbox(
        "운동 외 일상 활동",
        movement_options,
        index=(
            movement_options.index(previous_movement)
            if previous_movement in movement_options else 1
        ),
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
        int(age), sex, float(height_cm), float(weight_kg)
    )
    eer, eer_formula_name = estimate_eer(
        int(age), sex, float(height_cm), float(weight_kg), pal_category
    )

    st.session_state["bmr_result"] = bmr
    st.session_state["formula_name"] = bmr_formula_name
    st.session_state["eer_formula_name"] = eer_formula_name
    st.session_state["calculation_age_group"] = age_group_label(int(age))

    if bmr is not None and eer is not None:
        bmi = float(weight_kg) / ((float(height_cm) / 100) ** 2)

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
bmr_result = st.session_state.get("bmr_result", "not_calculated")

if bmr_result is not None and bmr_result != "not_calculated":
    bmr_value = float(bmr_result)
    eer_value = float(st.session_state.get("calculated_eer", 0))

    age_now = int(st.session_state.get("calculated_age", 25))
    current_pal = st.session_state.get(
        "calculated_activity", "저활동적 (Low active)"
    )

    st.divider()
    st.markdown("### 📊 계산 결과")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("추정 기초대사량", f"{bmr_value:,.0f} kcal/일")
    metric2.metric("예상 하루 에너지 필요량", f"{eer_value:,.0f} kcal/일")
    metric3.metric(
        "적용 연령대",
        st.session_state.get("calculation_age_group", "-"),
    )

    st.markdown(
        f'<div class="info-card">'
        f'<strong>하루 에너지 필요량 계산 기준</strong><br>'
        f"{st.session_state.get('eer_formula_name', '연령별 EER 추정식')}<br>"
        f"활동 수준: {current_pal}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if age_now < 3:
        st.warning(
            "현재 앱은 3세 미만을 위한 개월 단위 입력과 "
            "별도 영유아 계산 화면을 제공하지 않아 "
            "이 연령대의 하루 에너지 필요량을 계산하지 않아요."
        )
    elif age_now < 19:
        st.warning(
            "어린이·청소년용 EER 공식에는 성장에 필요한 "
            "에너지 항이 포함되어 있어요. 개인의 실제 필요량과 "
            "차이가 날 수 있으므로, 이 값으로 섭취량을 "
            "엄격하게 제한하지 마세요."
        )
    else:
        st.caption(
            "EER은 연령·성별·키·체중·활동 수준을 바탕으로 한 "
            "추정값이며, 개인의 실제 에너지 소비량을 "
            "직접 측정한 값은 아니에요."
        )

    st.markdown("#### 🚶 활동 기록 확인")
    st.write(
        "- 하루 걷기·이동 시간: **"
        f"{st.session_state.get('calculated_walking_time', '-') }**"
    )
    st.write(
        "- 주당 운동 횟수: **"
        f"{st.session_state.get('calculated_exercise_frequency', '-') }**"
    )
    st.write(
        "- 주된 운동 강도: **"
        f"{st.session_state.get('calculated_exercise_intensity', '-') }**"
    )
    st.write(
        "- 운동 외 일상 활동: **"
        f"{st.session_state.get('calculated_daily_movement', '-') }**"
    )

    st.info(
        "활동 기록은 선택한 활동 수준이 생활 패턴과 대체로 맞는지 "
        "확인하기 위한 참고 자료예요. 이 기록만으로 EER 활동 수준을 "
        "자동 확정하지 않으며, EER에 반영된 활동을 다시 열량으로 "
        "더하지 않아요."
    )

    st.markdown("#### 🥗 계산 결과 활용")
    st.write(
        f"예상 하루 에너지 필요량 **{eer_value:,.0f} kcal/일**을 "
        "기존 한 달 맞춤 식단 페이지로 전달해요. "
        "식단은 참고 추정값뿐 아니라 식품 다양성과 영양 균형을 "
        "함께 고려해 주세요."
    )

    st.button(
        "🥗 식단 플래너로 이동하기 →",
        key="go_to_meal_planner",
        use_container_width=True,
        on_click=lambda: st.switch_page("pages/calculate.py"),
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
        - 공식은 집단 자료를 바탕으로 한 추정식이므로 개인의 실제 에너지 소비량과 차이가 날 수 있어요.
        - 임신·수유 중이거나 특정 질환이 있는 경우, 또는 개인별 식단 처방이 필요한 경우에는 전문가의 안내를 참고해 주세요.
        """
    )

st.caption(
    "NutriDay는 교육용 참고 도구이며 의료 진단이나 "
    "개인별 영양 처방을 대신하지 않아요."
)
