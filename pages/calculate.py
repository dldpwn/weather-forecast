import streamlit as st
import pandas as pd
import plotly.express as px
import random
import re

from food_data import load_food_database


# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="NutriDay | 한 달 맞춤 식단",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# 디자인
# ==================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    html, body, [class*="css"], p, label,
    h1, h2, h3, h4, span, div {
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
    }

    .meal-card, .info-card {
        background: #F0F7F0;
        border: 1px solid #DCEADF;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: .7rem;
    }

    .meal-card {
        min-height: 120px;
        text-align: center;
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
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] > div {
        background: white;
        border-radius: 10px;
        border-color: #DCEADF;
    }

    button[data-baseweb="tab"] {
        color: #69756E;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #377D61;
        border-bottom-color: #4D9274;
    }

    hr {
        border-color: #DCEADF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 식품 데이터 불러오기
# ==================================================
@st.cache_data
def get_food_data():
    return load_food_database()


try:
    food_db = get_food_data()
    food_db_error = None
except Exception as e:
    food_db = pd.DataFrame()
    food_db_error = str(e)


# ==================================================
# 사이드바
# ==================================================
with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")
    st.divider()

    email = st.session_state.get("auth_email")

    st.markdown("### 👤 내 계정")
    st.caption(email or "계정 이메일을 확인할 수 없어요.")

    st.divider()

    st.page_link("main.py", label="🧪 기초대사량 & 영양 가이드")
    st.page_link("pages/calculate.py", label="🥗 한 달 맞춤 식단")
    st.page_link("pages/record.py", label="🍽️ 식사 기록 & 영양 관리")

    st.divider()

    if st.button(
        "로그아웃",
        key="calculate_logout",
        use_container_width=True
    ):
        # 인증 모듈이 연결되어 있는 경우에만 로그아웃 처리
        try:
            from supabase_client import supabase
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


# ==================================================
# 하루 에너지 참고값
# ==================================================
energy_keys = [
    "calculated_tdee",
    "tdee",
    "daily_calories",
    "meal_plan_calories",
]

daily_energy = None

for key in energy_keys:
    value = st.session_state.get(key)

    if value is not None:
        try:
            value = float(value)
            if value > 0:
                daily_energy = value
                break
        except (ValueError, TypeError):
            continue

energy_from_previous_page = daily_energy is not None

if daily_energy is None:
    daily_energy = 2000.0


# ==================================================
# 페이지 제목
# ==================================================
st.markdown(
    '<div class="main-title">🥗 나에게 맞는 한 달 식단</div>',
    unsafe_allow_html=True,
)

st.caption(
    "하루 에너지와 음식 선호를 참고해 다양한 식단을 구성해 보세요."
)

st.markdown("### 🔥 나의 하루 에너지")

if energy_from_previous_page:
    st.success(
        f"이전 페이지에서 계산한 하루 에너지 참고값: "
        f"{daily_energy:,.0f} kcal"
    )
else:
    st.info(
        "이전 페이지의 계산값을 찾지 못해 예시값을 사용하고 있어요."
    )

    daily_energy = float(
        st.number_input(
            "하루 에너지 참고값 (kcal)",
            min_value=500,
            max_value=6000,
            value=2000,
            step=100,
        )
    )


# ==================================================
# 식단 설정
# ==================================================
st.divider()
st.markdown("### ⚙️ 나에게 맞는 식단 설정")

col1, col2 = st.columns(2)

with col1:
    goal = st.selectbox(
        "식단 목표",
        [
            "균형 잡힌 식사",
            "활동량을 고려한 식사",
            "다양한 영양소 섭취",
        ],
    )

    meal_style = st.selectbox(
        "선호하는 식사 유형",
        [
            "한식 위주",
            "간편식 위주",
            "다양하게 구성",
        ],
    )

    meal_count = st.radio(
        "하루 식사 횟수",
        ["하루 세 끼", "세 끼 + 간식"],
        horizontal=True,
    )

with col2:
    preference_options = [
        "닭고기", "생선", "달걀", "두부",
        "소고기", "돼지고기", "채소", "과일",
        "우유", "직접 입력",
    ]

    preference = st.multiselect(
        "선호하는 음식",
        preference_options,
        default=["닭고기", "달걀", "채소"],
        key="preference_select",
    )

    custom_preference = []

    if "직접 입력" in preference:
        custom_preference_text = st.text_input(
            "선호하는 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타",
            key="custom_preference_text",
        )

        custom_preference = [
            item.strip()
            for item in custom_preference_text.split(",")
            if item.strip()
        ]

    all_preferences = list(dict.fromkeys(
        [x for x in preference if x != "직접 입력"]
        + custom_preference
    ))

    excluded_options = [
        "닭고기", "생선", "달걀", "두부",
        "소고기", "돼지고기", "우유",
        "견과류", "직접 입력",
    ]

    excluded_foods = st.multiselect(
        "식단에서 제외할 음식",
        excluded_options,
        key="excluded_select",
    )

    custom_excluded = []

    if "직접 입력" in excluded_foods:
        custom_excluded_text = st.text_input(
            "제외할 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타",
            key="custom_excluded_text",
        )

        custom_excluded = [
            item.strip()
            for item in custom_excluded_text.split(",")
            if item.strip()
        ]

    all_excluded = list(dict.fromkeys(
        [x for x in excluded_foods if x != "직접 입력"]
        + custom_excluded
    ))

    st.caption(
        "직접 입력은 쉼표로 구분해 주세요. "
        "입력한 단어는 식품명과 분류를 기준으로 비교해요."
    )

    st.caption(
        "알레르기가 있다면 해당 식품과 교차접촉 가능성도 별도로 확인해 주세요."
    )


# ==================================================
# CSV 데이터 확인
# ==================================================
if food_db_error:
    st.error(f"식품 데이터 불러오기 오류: {food_db_error}")
    st.stop()

if food_db.empty:
    st.error(
        "식품 데이터가 비어 있어요. "
        "CSV 파일의 위치와 내용을 확인해 주세요."
    )
    st.stop()

required_columns = [
    "식품명",
    "에너지(kcal)",
    "탄수화물(g)",
    "단백질(g)",
    "지방(g)",
]

missing_columns = [
    col for col in required_columns
    if col not in food_db.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ==================================================
# 영양성분 데이터 정리
# ==================================================
NUTRIENT_COLUMNS = {
    "kcal": "에너지(kcal)",
    "carbs": "탄수화물(g)",
    "protein": "단백질(g)",
    "fat": "지방(g)",
    "fiber": "식이섬유(g)",
    "calcium": "칼슘(mg)",
    "iron": "철(mg)",
    "potassium": "칼륨(mg)",
    "sodium": "나트륨(mg)",
    "vitamin_a": "비타민 A(μg RAE)",
    "vitamin_c": "비타민 C(mg)",
    "vitamin_d": "비타민 D(μg)",
}


def safe_number(value):
    """숫자 변환이 불가능하거나 결측값이면 0을 반환한다."""
    try:
        if pd.isna(value):
            return 0.0

        result = float(value)

        if pd.isna(result):
            return 0.0

        return result

    except (ValueError, TypeError):
        return 0.0


def classify_food(name):
    """식품명에 포함된 단어를 기준으로 식품 분류를 추정한다."""
    name = str(name).casefold()

    if any(x in name for x in [
        "닭", "치킨"
    ]):
        return "닭고기"

    if any(x in name for x in [
        "고등어", "연어", "참치", "갈치",
        "명태", "생선", "새우", "오징어"
    ]):
        return "생선"

    if any(x in name for x in [
        "달걀", "계란"
    ]):
        return "달걀"

    if "두부" in name:
        return "두부"

    if any(x in name for x in [
        "소고기", "쇠고기"
    ]):
        return "소고기"

    if any(x in name for x in [
        "돼지고기", "돈육"
    ]):
        return "돼지고기"

    if any(x in name for x in [
        "우유", "요거트", "요구르트", "치즈"
    ]):
        return "유제품"

    if any(x in name for x in [
        "사과", "바나나", "딸기", "포도",
        "귤", "오렌지", "배", "과일"
    ]):
        return "과일"

    if any(x in name for x in [
        "채소", "나물", "샐러드", "시금치",
        "브로콜리", "당근", "양배추", "김치"
    ]):
        return "채소"

    if any(x in name for x in [
        "견과", "아몬드", "호두", "땅콩"
    ]):
        return "견과류"

    return "기타"


def classify_style(name):
    """식품명에 따라 식사 유형을 대략적으로 분류한다."""
    name = str(name)

    korean_keywords = [
        "밥", "국", "찌개", "구이", "볶음",
        "조림", "비빔밥", "죽", "나물"
    ]

    simple_keywords = [
        "샐러드", "샌드위치", "오트밀",
        "빵", "요거트", "요구르트"
    ]

    if any(x in name for x in korean_keywords):
        return "한식"

    if any(x in name for x in simple_keywords):
        return "간편식"

    return "다양"


def get_basis_unit(row):
    """CSV의 영양성분 기준량에서 g/ml 단위를 확인한다."""
    basis_text = str(
        row.get("영양성분함량기준량", "")
    ).lower()

    if "ml" in basis_text:
        return "ml"

    if "g" in basis_text:
        return "g"

    return "g"


# foods 딕셔너리 생성
foods = {}

for _, row in food_db.iterrows():
    name = str(row.get("식품명", "")).strip()

    if not name or name.lower() == "nan":
        continue

    info = {
        "group": classify_food(name),
        "style": classify_style(name),
        "unit": get_basis_unit(row),
        "basis": str(row.get("영양성분함량기준량", "100g")),
    }

    for key, column in NUTRIENT_COLUMNS.items():
        info[key] = safe_number(row.get(column, 0))

    foods[name] = info


if not foods:
    st.error("사용할 수 있는 식품 데이터가 없어요.")
    st.stop()


# ==================================================
# 음식 분류
# ==================================================
SNACK_GROUPS = [
    "과일",
    "유제품",
    "견과류",
]

SNACK_KEYWORDS = [
    "과일", "사과", "바나나", "딸기",
    "포도", "귤", "오렌지", "배",
    "요거트", "요구르트", "우유",
    "견과", "아몬드", "호두", "땅콩",
]


def is_snack(name, info):
    return (
        info.get("group") in SNACK_GROUPS
        or any(word in name for word in SNACK_KEYWORDS)
    )


# ==================================================
# 선호 및 제외 음식 확인
# ==================================================
def matches_food(name, info, terms):
    name_lower = str(name).casefold()
    group_lower = str(info.get("group", "")).casefold()

    for term in terms:
        term_lower = str(term).strip().casefold()

        if not term_lower:
            continue

        if (
            term_lower in name_lower
            or term_lower in group_lower
        ):
            return True

    return False


# ==================================================
# 식사 후보 생성
# ==================================================
def get_food_candidates(style, excluded, meal_name):
    candidates = []

    for name, info in foods.items():

        # 간식은 일반 식사 후보에서 제외
        if is_snack(name, info):
            continue

        if matches_food(name, info, excluded):
            continue

        if style == "한식 위주":
            if info.get("style") not in ["한식", "다양"]:
                continue

        elif style == "간편식 위주":
            if info.get("style") not in ["간편식", "다양"]:
                continue

        candidates.append(name)

    return candidates


# ==================================================
# 간식 후보 생성
# ==================================================
def get_snack_candidates(excluded):
    candidates = []

    for name, info in foods.items():
        if not is_snack(name, info):
            continue

        if matches_food(name, info, excluded):
            continue

        candidates.append(name)

    return candidates


# ==================================================
# 메뉴 선택
# ==================================================
def choose_food(
    candidates,
    preference,
    recent_meals,
    rng,
):
    if not candidates:
        return None

    recent_set = set(recent_meals[-6:])

    available = [
        name for name in candidates
        if name not in recent_set
    ]

    if not available:
        available = candidates.copy()

    preferred = [
        name for name in available
        if matches_food(name, foods[name], preference)
    ]

    # 선호 음식이 있으면 우선적으로 반영
    if preferred and rng.random() < 0.7:
        return rng.choice(preferred)

    return rng.choice(available)


# ==================================================
# 30일 식단 생성
# ==================================================
def generate_monthly_plan(
    style,
    preference,
    excluded,
    meal_count,
    seed=None,
):
    rng = random.Random(seed)

    meal_names = ["아침", "점심", "저녁"]

    if meal_count == "세 끼 + 간식":
        meal_names.append("간식")

    meal_candidates = get_food_candidates(
        style,
        excluded,
        "식사"
    )

    snack_candidates = get_snack_candidates(
        excluded
    )

    if not meal_candidates:
        return None, "식사"

    if (
        meal_count == "세 끼 + 간식"
        and not snack_candidates
    ):
        return None, "간식"

    plan = []
    recent_meals = []
    recent_snacks = []

    for day in range(1, 31):
        day_plan = {"일차": day}

        used_today = set()

        for meal_name in meal_names:

            if meal_name == "간식":
                candidates = snack_candidates
                recent = recent_snacks
            else:
                candidates = meal_candidates
                recent = recent_meals

            available = [
                name for name in candidates
                if name not in used_today
            ]

            if not available:
                available = candidates.copy()

            chosen = choose_food(
                candidates=available,
                preference=preference,
                recent_meals=recent,
                rng=rng,
            )

            if chosen is None:
                return None, meal_name

            day_plan[meal_name] = chosen
            used_today.add(chosen)

            recent.append(chosen)

        plan.append(day_plan)

    return plan, None


# ==================================================
# 영양소 계산
# ==================================================
NUTRIENT_KEYS = [
    "kcal",
    "carbs",
    "protein",
    "fat",
    "fiber",
    "calcium",
    "iron",
    "potassium",
    "sodium",
    "vitamin_a",
    "vitamin_c",
    "vitamin_d",
]


def calculate_daily_nutrition(day_plan):
    """
    CSV에 저장된 각 음식의 영양성분 기준값을 합산한다.

    주의:
    CSV의 기준량이 100g 또는 100ml인 경우,
    이 함수의 합계는 실제 1회 섭취량이 아닌 기준량 합산 참고값이다.
    """

    totals = {
        nutrient: 0.0
        for nutrient in NUTRIENT_KEYS
    }

    meal_nutrition = {}

    for meal_name, food_name in day_plan.items():

        if meal_name == "일차":
            continue

        info = foods.get(food_name)

        if info is None:
            continue

        meal_nutrition[meal_name] = info.copy()

        for nutrient in NUTRIENT_KEYS:
            totals[nutrient] += safe_number(
                info.get(nutrient, 0)
            )

    # 탄단지 에너지 계산
    macro_energy = {
        "탄수화물": totals["carbs"] * 4,
        "단백질": totals["protein"] * 4,
        "지방": totals["fat"] * 9,
    }

    macro_total = sum(macro_energy.values())

    if macro_total > 0:
        macro_percent = {
            name: value / macro_total * 100
            for name, value in macro_energy.items()
        }
    else:
        macro_percent = {
            "탄수화물": 0.0,
            "단백질": 0.0,
            "지방": 0.0,
        }

    return totals, meal_nutrition, macro_energy, macro_percent


def calculate_nutrients(day_plan):
    """30일 요약에서 사용하는 영양소 합계 함수."""
    totals, _, _, _ = calculate_daily_nutrition(day_plan)
    return totals


# ==================================================
# 식단 생성 버튼
# ==================================================
st.divider()
st.markdown("### 📅 30일 식단표 만들기")

st.write(
    "설정한 조건에 맞춰 30일 메뉴를 자동으로 구성해요. "
    "생성된 식단은 날짜별로 확인할 수 있어요."
)

if st.button(
    "✨ 나만의 한 달 식단 생성하기",
    use_container_width=True
):
    new_plan, failed_meal = generate_monthly_plan(
        style=meal_style,
        preference=all_preferences,
        excluded=all_excluded,
        meal_count=meal_count,
    )

    if new_plan is None:
        st.error(
            f"{failed_meal} 메뉴 후보가 부족해요. "
            "제외 음식이나 식사 유형을 조정해 주세요."
        )

    else:
        st.session_state["monthly_plan"] = new_plan

        st.session_state["monthly_plan_settings"] = {
            "style": meal_style,
            "preference": all_preferences,
            "excluded": all_excluded,
            "meal_count": meal_count,
            "goal": goal,
            "energy": daily_energy,
        }

        st.session_state["selected_day"] = 1

        st.success("30일 식단이 생성되었어요!")


# ==================================================
# 생성된 식단 출력
# ==================================================
if "monthly_plan" in st.session_state:

    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    plan = st.session_state["monthly_plan"]

    saved_settings = st.session_state.get(
        "monthly_plan_settings",
        {}
    )

    st.success("30일 식단이 준비되었어요!")

    st.caption(
        f"식사 유형: {saved_settings.get('style', '-')}"
        f" · 목표: {saved_settings.get('goal', '-')}"
        f" · 하루 에너지 참고값: "
        f"{saved_settings.get('energy', 0):,.0f} kcal"
    )

    # --------------------------------------------------
    # 날짜 선택
    # --------------------------------------------------
    selected_day = st.selectbox(
        "확인할 날짜를 선택하세요.",
        options=list(range(1, len(plan) + 1)),
        format_func=lambda x: f"{x}일 차",
        key="selected_day",
    )

    selected_meal = plan[selected_day - 1]

    st.markdown(f"#### 🍽️ {selected_day}일 차 식단")

    meal_names = [
        key for key in selected_meal
        if key != "일차"
    ]

    columns = st.columns(len(meal_names))

    for index, meal_name in enumerate(meal_names):
        with columns[index]:
            food_name = selected_meal[meal_name]
            food_info = foods.get(food_name, {})
            food_kcal = safe_number(
                food_info.get("kcal", 0)
            )

            st.markdown(
                f"""
                <div class="meal-card">
                    <b>{meal_name}</b><br>
                    {food_name}<br>
                    <small>기준량 에너지: {food_kcal:,.1f} kcal</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------
    # 선택한 날짜 다시 추천
    # --------------------------------------------------
    st.markdown("### 🔄 오늘의 식단 다시 추천")

    if st.button(
        f"{selected_day}일 차 메뉴 다시 추천하기",
        use_container_width=True,
    ):
        settings = st.session_state.get(
            "monthly_plan_settings",
            {}
        )

        new_plan, failed_meal = generate_monthly_plan(
            style=settings.get("style", meal_style),
            preference=settings.get("preference", all_preferences),
            excluded=settings.get("excluded", all_excluded),
            meal_count=settings.get("meal_count", meal_count),
        )

        if new_plan is None:
            st.error(
                f"{failed_meal} 메뉴 후보가 부족해요. "
                "설정을 조정해 주세요."
            )
        else:
            # 새로 생성한 전체 식단 중 선택한 날짜만 교체
            plan[selected_day - 1] = new_plan[selected_day - 1]
            st.session_state["monthly_plan"] = plan
            st.success(f"{selected_day}일 차 식단을 새로 추천했어요!")
            st.rerun()

    # --------------------------------------------------
    # 하루 영양 분석
    # --------------------------------------------------
    st.divider()
    st.markdown("### 📊 하루 영양 분석")

    totals, meal_nutrition, macro_energy, macro_percent = (
        calculate_daily_nutrition(selected_meal)
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            "기준량 에너지 합계",
            f"{totals['kcal']:,.1f} kcal"
        )

    with metric2:
        st.metric(
            "탄수화물",
            f"{totals['carbs']:.1f} g"
        )

    with metric3:
        st.metric(
            "단백질",
            f"{totals['protein']:.1f} g"
        )

    with metric4:
        st.metric(
            "지방",
            f"{totals['fat']:.1f} g"
        )

    st.caption(
        "아래 영양성분은 CSV에 등록된 음식별 기준량(예: 100g 또는 100ml)을 "
        "합산한 참고값이에요. 실제 섭취량을 측정한 값은 아니며, "
        "조리법과 섭취 중량에 따라 달라질 수 있어요."
    )

    # --------------------------------------------------
    # 탄단지 에너지 구성 그래프
    # --------------------------------------------------
    st.markdown("#### 🍚 탄수화물·단백질·지방의 에너지 구성")

    macro_df = pd.DataFrame({
        "영양소": list(macro_energy.keys()),
        "에너지(kcal)": list(macro_energy.values()),
        "비율(%)": [
            macro_percent[name]
            for name in macro_energy
        ],
    })

    if macro_df["에너지(kcal)"].sum() > 0:
        fig_macro = px.pie(
            macro_df,
            names="영양소",
            values="에너지(kcal)",
            hole=0.55,
            title="탄단지에서 얻는 에너지 비율",
        )

        fig_macro.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent}",
        )

        fig_macro.update_layout(
            paper_bgcolor="#FBF9F1",
            plot_bgcolor="#FBF9F1",
            font=dict(family="Gowun Dodum"),
            legend_title_text="영양소",
        )

        st.plotly_chart(
            fig_macro,
            use_container_width=True
        )

        st.caption(
            "이 그래프는 전체 영양소의 비율이 아니라, "
            "탄수화물·단백질·지방에서 얻는 에너지끼리 비교한 비율이에요. "
            "탄수화물과 단백질은 1g당 약 4kcal, 지방은 1g당 약 9kcal로 계산했어요."
        )
    else:
        st.info("탄단지 에너지 데이터를 계산할 수 없어요.")

    # --------------------------------------------------
    # 무기질 그래프
    # --------------------------------------------------
    st.markdown("#### 🧂 무기질 기준량 합계")

    mineral_values = {
        "칼슘": totals["calcium"],
        "철분": totals["iron"],
        "칼륨": totals["potassium"],
        "나트륨": totals["sodium"],
    }

    mineral_df = pd.DataFrame({
        "영양소": list(mineral_values.keys()),
        "함량(mg)": list(mineral_values.values()),
    })

    fig_mineral = px.bar(
        mineral_df,
        x="영양소",
        y="함량(mg)",
        text="함량(mg)",
        title="무기질 함량 합계",
    )

    fig_mineral.update_layout(
        paper_bgcolor="#FBF9F1",
        plot_bgcolor="#FBF9F1",
        font=dict(family="Gowun Dodum"),
        showlegend=False,
        yaxis_title="함량 (mg)",
        xaxis_title="",
    )

    st.plotly_chart(
        fig_mineral,
        use_container_width=True
    )

    # --------------------------------------------------
    # 비타민 및 식이섬유
    # --------------------------------------------------
    st.markdown("#### 🍊 비타민 및 식이섬유")

    vitamin_col1, vitamin_col2, vitamin_col3 = st.columns(3)

    with vitamin_col1:
        st.metric(
            "비타민 A",
            f"{totals['vitamin_a']:.1f} μg RAE"
        )

    with vitamin_col2:
        st.metric(
            "비타민 C",
            f"{totals['vitamin_c']:.1f} mg"
        )

    with vitamin_col3:
        st.metric(
            "비타민 D",
            f"{totals['vitamin_d']:.1f} μg"
        )

    st.metric(
        "식이섬유",
        f"{totals['fiber']:.1f} g"
    )

    # --------------------------------------------------
    # 끼니별 에너지
    # --------------------------------------------------
    st.markdown("#### 🍽️ 끼니별 에너지 구성")

    meal_energy_rows = []

    for meal_name, food_name in selected_meal.items():
        if meal_name == "일차":
            continue

        info = foods.get(food_name, {})

        meal_energy_rows.append({
            "끼니": meal_name,
            "에너지(kcal)": safe_number(
                info.get("kcal", 0)
            ),
        })

    meal_energy_df = pd.DataFrame(meal_energy_rows)

    fig_meal = px.bar(
        meal_energy_df,
        x="끼니",
        y="에너지(kcal)",
        text="에너지(kcal)",
        title="끼니별 기준량 에너지",
    )

    fig_meal.update_layout(
        paper_bgcolor="#FBF9F1",
        plot_bgcolor="#FBF9F1",
        font=dict(family="Gowun Dodum"),
        showlegend=False,
        xaxis_title="",
        yaxis_title="에너지 (kcal)",
    )

    st.plotly_chart(
        fig_meal,
        use_container_width=True
    )

    # --------------------------------------------------
    # 영양소 상세표
    # --------------------------------------------------
    with st.expander("영양소별 합계 자세히 보기"):

        detail_df = pd.DataFrame([
            ["에너지", f"{totals['kcal']:.1f}", "kcal"],
            ["탄수화물", f"{totals['carbs']:.1f}", "g"],
            ["단백질", f"{totals['protein']:.1f}", "g"],
            ["지방", f"{totals['fat']:.1f}", "g"],
            ["식이섬유", f"{totals['fiber']:.1f}", "g"],
            ["칼슘", f"{totals['calcium']:.1f}", "mg"],
            ["철분", f"{totals['iron']:.1f}", "mg"],
            ["칼륨", f"{totals['potassium']:.1f}", "mg"],
            ["나트륨", f"{totals['sodium']:.1f}", "mg"],
            ["비타민 A", f"{totals['vitamin_a']:.1f}", "μg RAE"],
            ["비타민 C", f"{totals['vitamin_c']:.1f}", "mg"],
            ["비타민 D", f"{totals['vitamin_d']:.1f}", "μg"],
        ], columns=["영양소", "합계", "단위"])

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------
    # 전체 30일 식단표
    # --------------------------------------------------
    st.divider()
    st.markdown("#### 📋 전체 30일 식단표")

    plan_df = pd.DataFrame(plan)

    st.dataframe(
        plan_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "📥 30일 식단표 다운로드",
        data=plan_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="NutriDay_30day_meal_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # --------------------------------------------------
    # 식사 기록 페이지 이동
    # --------------------------------------------------
    st.button(
        "🍽️ 식사 기록 & 영양 관리로 이동하기 →",
        key="go_to_record",
        use_container_width=True,
        on_click=lambda: st.switch_page("pages/record.py"),
    )

else:
    st.info(
        "식단 생성 버튼을 눌러 나만의 식단을 만들어 보세요!"
    )
