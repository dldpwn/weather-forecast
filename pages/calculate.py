import streamlit as st
import pandas as pd
import plotly.express as px
import random

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

    .info-card, .meal-card {
        background: #F0F7F0;
        border: 1px solid #DCEADF;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: .7rem;
    }

    .meal-card {
        min-height: 100px;
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

    [data-testid="stDataFrame"] {
        border: 1px solid #DCEADF;
        border-radius: 12px;
    }

    hr {
        border-color: #DCEADF;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

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

    if st.button("로그아웃", key="calculate_logout", use_container_width=True):
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


# ==================================================
# 하루 에너지 참고값 불러오기
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
            pass

energy_from_previous_page = daily_energy is not None

if daily_energy is None:
    daily_energy = 2000.0


st.markdown(
    '<div class="main-title">🥗 나에게 맞는 한 달 식단</div>',
    unsafe_allow_html=True,
)
st.caption("하루 에너지와 음식 선호를 참고해 다양한 식단을 구성해 보세요.")

st.markdown("### 🔥 나의 하루 에너지")

if energy_from_previous_page:
    st.success(f"이전 페이지에서 계산한 하루 에너지 참고값: {daily_energy:,.0f} kcal")
else:
    st.info("이전 페이지의 계산값을 찾지 못해 예시값을 사용하고 있어요.")

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
        [item for item in preference if item != "직접 입력"]
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
        [item for item in excluded_foods if item != "직접 입력"]
        + custom_excluded
    ))

    st.caption(
        "직접 입력은 쉼표로 구분해 주세요. 입력한 단어는 메뉴 이름과 음식 분류를 "
        "기준으로 비교하며, 실제 메뉴의 모든 재료를 판별하지는 않아요."
    )
    st.caption(
        "알레르기가 있다면 해당 식품과 교차접촉 가능성도 별도로 확인해 주세요."
    )


# ==================================================
# 음식 데이터
# 기존 사용자가 제공한 메뉴별 영양 정보 유지
# ==================================================
foods = {
    "닭고기 덮밥": {
        "group": "닭고기", "style": "한식",
        "kcal": 450, "carbs": 65, "protein": 28, "fat": 9,
        "fiber": 4, "calcium": 45, "iron": 2.0, "potassium": 430,
        "sodium": 450, "vitamin_a": 35, "vitamin_c": 12, "vitamin_d": 0.2
    },
    "두부 비빔밥": {
        "group": "두부", "style": "한식",
        "kcal": 430, "carbs": 68, "protein": 18, "fat": 10,
        "fiber": 7, "calcium": 160, "iron": 3.0, "potassium": 620,
        "sodium": 500, "vitamin_a": 180, "vitamin_c": 18, "vitamin_d": 0
    },
    "생선구이 정식": {
        "group": "생선", "style": "한식",
        "kcal": 470, "carbs": 65, "protein": 27, "fat": 12,
        "fiber": 5, "calcium": 55, "iron": 2.0, "potassium": 520,
        "sodium": 480, "vitamin_a": 30, "vitamin_c": 15, "vitamin_d": 5
    },
    "소고기 채소볶음 정식": {
        "group": "소고기", "style": "한식",
        "kcal": 490, "carbs": 62, "protein": 29, "fat": 13,
        "fiber": 5, "calcium": 60, "iron": 3.5, "potassium": 480,
        "sodium": 520, "vitamin_a": 100, "vitamin_c": 20, "vitamin_d": 0.2
    },
    "돼지고기 채소볶음": {
        "group": "돼지고기", "style": "한식",
        "kcal": 480, "carbs": 60, "protein": 25, "fat": 15,
        "fiber": 5, "calcium": 50, "iron": 2.5, "potassium": 450,
        "sodium": 550, "vitamin_a": 90, "vitamin_c": 18, "vitamin_d": 0.5
    },
    "달걀 채소볶음밥": {
        "group": "달걀", "style": "한식",
        "kcal": 420, "carbs": 62, "protein": 15, "fat": 12,
        "fiber": 4, "calcium": 65, "iron": 2.0, "potassium": 350,
        "sodium": 430, "vitamin_a": 140, "vitamin_c": 15, "vitamin_d": 1.2
    },
    "닭고기 샐러드": {
        "group": "닭고기", "style": "간편식",
        "kcal": 350, "carbs": 25, "protein": 30, "fat": 13,
        "fiber": 6, "calcium": 90, "iron": 2.5, "potassium": 600,
        "sodium": 400, "vitamin_a": 250, "vitamin_c": 35, "vitamin_d": 0.2
    },
    "두부 샐러드": {
        "group": "두부", "style": "간편식",
        "kcal": 320, "carbs": 28, "protein": 17, "fat": 14,
        "fiber": 7, "calcium": 180, "iron": 3.0, "potassium": 520,
        "sodium": 350, "vitamin_a": 220, "vitamin_c": 30, "vitamin_d": 0
    },
    "통밀빵과 달걀": {
        "group": "달걀", "style": "간편식",
        "kcal": 330, "carbs": 40, "protein": 17, "fat": 11,
        "fiber": 5, "calcium": 100, "iron": 2.5, "potassium": 280,
        "sodium": 420, "vitamin_a": 110, "vitamin_c": 0, "vitamin_d": 1.0
    },
    "오트밀과 우유": {
        "group": "우유", "style": "간편식",
        "kcal": 350, "carbs": 52, "protein": 14, "fat": 9,
        "fiber": 7, "calcium": 300, "iron": 2.5, "potassium": 480,
        "sodium": 150, "vitamin_a": 70, "vitamin_c": 2, "vitamin_d": 2.5
    },
    "과일과 요구르트": {
        "group": "과일", "style": "간편식",
        "kcal": 200, "carbs": 35, "protein": 7, "fat": 4,
        "fiber": 4, "calcium": 220, "iron": 0.5, "potassium": 350,
        "sodium": 90, "vitamin_a": 30, "vitamin_c": 35, "vitamin_d": 0.5
    },
    "밥과 두부조림": {
        "group": "두부", "style": "한식",
        "kcal": 400, "carbs": 63, "protein": 18, "fat": 9,
        "fiber": 4, "calcium": 170, "iron": 2.5, "potassium": 400,
        "sodium": 400, "vitamin_a": 50, "vitamin_c": 8, "vitamin_d": 0
    },
    "고구마와 달걀": {
        "group": "달걀", "style": "다양",
        "kcal": 320, "carbs": 48, "protein": 13, "fat": 8,
        "fiber": 6, "calcium": 60, "iron": 1.5, "potassium": 550,
        "sodium": 180, "vitamin_a": 600, "vitamin_c": 15, "vitamin_d": 1
    },
    "생선 샐러드": {
        "group": "생선", "style": "간편식",
        "kcal": 360, "carbs": 25, "protein": 27, "fat": 15,
        "fiber": 6, "calcium": 100, "iron": 2.0, "potassium": 500,
        "sodium": 420, "vitamin_a": 180, "vitamin_c": 30, "vitamin_d": 5
    },
    "채소 비빔밥": {
        "group": "채소", "style": "한식",
        "kcal": 400, "carbs": 70, "protein": 11, "fat": 9,
        "fiber": 8, "calcium": 100, "iron": 3.0, "potassium": 650,
        "sodium": 430, "vitamin_a": 280, "vitamin_c": 25, "vitamin_d": 0
    },
    "과일 오트밀": {
        "group": "과일", "style": "간편식",
        "kcal": 330, "carbs": 55, "protein": 11, "fat": 8,
        "fiber": 8, "calcium": 180, "iron": 2.5, "potassium": 430,
        "sodium": 120, "vitamin_a": 30, "vitamin_c": 25, "vitamin_d": 1.5
    },
    "닭고기 채소볶음": {
        "group": "닭고기", "style": "다양",
        "kcal": 430, "carbs": 45, "protein": 32, "fat": 12,
        "fiber": 6, "calcium": 80, "iron": 2.5, "potassium": 520,
        "sodium": 420, "vitamin_a": 180, "vitamin_c": 35, "vitamin_d": 0.2
    },
    "소고기 덮밥": {
        "group": "소고기", "style": "다양",
        "kcal": 470, "carbs": 62, "protein": 27, "fat": 13,
        "fiber": 4, "calcium": 45, "iron": 3.5, "potassium": 430,
        "sodium": 480, "vitamin_a": 25, "vitamin_c": 12, "vitamin_d": 0.2
    },
    "돼지고기 덮밥": {
        "group": "돼지고기", "style": "다양",
        "kcal": 460, "carbs": 63, "protein": 25, "fat": 12,
        "fiber": 4, "calcium": 40, "iron": 2.2, "potassium": 420,
        "sodium": 500, "vitamin_a": 25, "vitamin_c": 10, "vitamin_d": 0.4
    },
    "두부 채소덮밥": {
        "group": "두부", "style": "다양",
        "kcal": 420, "carbs": 62, "protein": 19, "fat": 11,
        "fiber": 7, "calcium": 180, "iron": 3.0, "potassium": 560,
        "sodium": 400, "vitamin_a": 200, "vitamin_c": 25, "vitamin_d": 0
    },
}


# ==================================================
# 음식 분류
# ==================================================
BREAKFAST_FOODS = [
    "통밀빵과 달걀",
    "오트밀과 우유",
    "고구마와 달걀",
    "과일 오트밀",
    "달걀 채소볶음밥",
]

SNACK_FOODS = [
    "과일과 요구르트",
]

MAIN_MEAL_FOODS = [
    name for name in foods
    if name not in BREAKFAST_FOODS + SNACK_FOODS
]


# ==================================================
# 음식 검색 및 제외 조건
# ==================================================
def matches_food(name, info, terms):
    name_lower = name.casefold()
    group_lower = str(info.get("group", "")).casefold()

    return any(
        term.casefold() in name_lower
        or term.casefold() in group_lower
        for term in terms
        if term.strip()
    )


def get_food_candidates(style, excluded, meal_name):
    if meal_name == "아침":
        source = BREAKFAST_FOODS
    elif meal_name == "간식":
        source = SNACK_FOODS
    else:
        source = MAIN_MEAL_FOODS

    candidates = []

    for name in source:
        info = foods[name]

        if matches_food(name, info, excluded):
            continue

        if style == "한식 위주" and info["style"] not in ["한식", "다양"]:
            continue

        if style == "간편식 위주" and info["style"] not in ["간편식", "다양"]:
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
    target_kcal,
    rng,
):
    if not candidates:
        return None

    recent_set = set(recent_meals[-5:])

    # 최근 메뉴를 우선 제외하되, 후보가 부족하면 다시 허용
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

    # 목표 에너지에 가까운 메뉴를 우선 고려하되,
    # 선호 메뉴와 다양성도 함께 반영
    scored = []

    for name in available:
        info = foods[name]

        energy_difference = abs(info["kcal"] - target_kcal)
        score = energy_difference

        if preferred and name in preferred:
            score -= 35

        score += rng.uniform(0, 45)

        scored.append((score, name))

    scored.sort(key=lambda item: item[0])

    # 상위 후보 중 무작위 선택해 매번 같은 식단이 되지 않게 함
    top_candidates = [name for _, name in scored[:min(3, len(scored))]]

    return rng.choice(top_candidates)


# ==================================================
# 30일 식단 생성
# ==================================================
def generate_monthly_plan(
    style,
    preference,
    excluded,
    meal_count,
    daily_energy,
    goal,
    seed=None,
):
    rng = random.Random(seed)

    meal_names = ["아침", "점심", "저녁"]

    if meal_count == "세 끼 + 간식":
        meal_names.append("간식")

    plan = []
    recent_meals = []

    if len(meal_names) == 4:
        energy_ratios = {
            "아침": 0.25,
            "점심": 0.30,
            "저녁": 0.30,
            "간식": 0.15,
        }
    else:
        energy_ratios = {
            "아침": 0.30,
            "점심": 0.35,
            "저녁": 0.35,
        }

    candidate_map = {
        meal: get_food_candidates(style, excluded, meal)
        for meal in meal_names
    }

    # 하나라도 후보가 없으면 식단 생성 중단
    for meal, candidates in candidate_map.items():
        if not candidates:
            return None, meal

    for day in range(1, 31):
        day_plan = {"일차": day}

        for meal in meal_names:
            target_kcal = daily_energy * energy_ratios[meal]

            chosen = choose_food(
                candidates=candidate_map[meal],
                preference=preference,
                recent_meals=recent_meals,
                target_kcal=target_kcal,
                rng=rng,
            )

            day_plan[meal] = chosen
            recent_meals.append(chosen)

        plan.append(day_plan)

    return plan, None


# ==================================================
# 영양소 합산
# ==================================================
NUTRIENT_LABELS = {
    "carbs": "탄수화물",
    "protein": "단백질",
    "fat": "지방",
    "fiber": "식이섬유",
    "calcium": "칼슘",
    "iron": "철분",
    "potassium": "칼륨",
    "sodium": "나트륨",
    "vitamin_a": "비타민 A",
    "vitamin_c": "비타민 C",
    "vitamin_d": "비타민 D",
}


def calculate_daily_nutrition(day_plan):
    totals = {
        "kcal": 0,
        "carbs": 0,
        "protein": 0,
        "fat": 0,
        "fiber": 0,
        "calcium": 0,
        "iron": 0,
        "potassium": 0,
        "sodium": 0,
        "vitamin_a": 0,
        "vitamin_c": 0,
        "vitamin_d": 0,
    }

    meal_nutrition = {}

    for meal_name, food_name in day_plan.items():
        if meal_name == "일차":
            continue

        info = foods[food_name]
        meal_nutrition[meal_name] = info.copy()

        for nutrient in totals:
            totals[nutrient] += info.get(nutrient, 0)

    # 탄단지에서 얻는 에너지 계산
    macro_energy = {
        "탄수화물": totals["carbs"] * 4,
        "단백질": totals["protein"] * 4,
        "지방": totals["fat"] * 9,
    }

    macro_energy_total = sum(macro_energy.values())

    if macro_energy_total > 0:
        macro_percent = {
            name: value / macro_energy_total * 100
            for name, value in macro_energy.items()
        }
    else:
        macro_percent = {
            "탄수화물": 0,
            "단백질": 0,
            "지방": 0,
        }

    return totals, meal_nutrition, macro_energy, macro_percent


# ==================================================
# 식단 생성 버튼
# ==================================================
st.divider()
st.markdown("### 📅 30일 식단표 만들기")

st.write(
    "설정한 조건에 맞춰 30일 메뉴를 자동으로 구성해요. "
    "생성된 식단은 날짜별로 확인할 수 있어요."
)

if st.button("✨ 나만의 한 달 식단 생성하기", use_container_width=True):
    new_plan, failed_meal = generate_monthly_plan(
        style=meal_style,
        preference=all_preferences,
        excluded=all_excluded,
        meal_count=meal_count,
        daily_energy=daily_energy,
        goal=goal,
        seed=None,
    )

    if new_plan is None:
        st.error(
            f"{failed_meal} 메뉴 후보가 없어요. "
            "선호하는 식사 유형이나 제외 음식 설정을 조정해 주세요."
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

    st.success("30일 식단이 준비되었어요!")

    saved_settings = st.session_state.get("monthly_plan_settings", {})

    st.caption(
        f"식사 유형: {saved_settings.get('style', '-')}"
        f" · 목표: {saved_settings.get('goal', '-')}"
        f" · 하루 에너지 참고값: "
        f"{saved_settings.get('energy', 0):,.0f} kcal"
    )

    selected_day = st.selectbox(
        "확인할 날짜를 선택하세요.",
        options=list(range(1, 31)),
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
            food_kcal = foods[food_name]["kcal"]

            st.markdown(
                f"""
                <div class="meal-card">
                    <b>{meal_name}</b><br>
                    {food_name}<br>
                    <small>{food_kcal:,} kcal</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------
    # 하루 영양 분석
    # --------------------------------------------------
    st.divider()
    st.markdown("### 📊 하루 영양 분석")

    totals, meal_nutrition, macro_energy, macro_percent = (
        calculate_daily_nutrition(selected_meal)
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("하루 에너지", f"{totals['kcal']:,} kcal")

    with metric2:
        st.metric("탄수화물", f"{totals['carbs']:.1f} g")

    with metric3:
        st.metric("단백질", f"{totals['protein']:.1f} g")

    st.caption(
        "에너지와 영양소는 현재 코드에 저장된 메뉴별 기준값을 합산한 참고 정보예요. "
        "실제 섭취량이나 조리법에 따라 달라질 수 있어요."
    )

    # 탄단지 에너지 구성 그래프
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

        st.plotly_chart(fig_macro, use_container_width=True)

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
    st.markdown("#### 🧂 무기질 섭취량")

    mineral_values = {
        "칼슘": totals["calcium"],
        "철분": totals["iron"],
        "칼륨": totals["potassium"],
        "나트륨": totals["sodium"],
    }

    mineral_df = pd.DataFrame({
        "영양소": list(mineral_values.keys()),
        "섭취량(mg)": list(mineral_values.values()),
    })

    fig_mineral = px.bar(
        mineral_df,
        x="영양소",
        y="섭취량(mg)",
        text="섭취량(mg)",
        title="하루 무기질 합계",
    )

    fig_mineral.update_layout(
        paper_bgcolor="#FBF9F1",
        plot_bgcolor="#FBF9F1",
        font=dict(family="Gowun Dodum"),
        showlegend=False,
        yaxis_title="섭취량 (mg)",
        xaxis_title="",
    )

    st.plotly_chart(fig_mineral, use_container_width=True)

    # --------------------------------------------------
    # 비타민 및 식이섬유
    # --------------------------------------------------
    st.markdown("#### 🍊 비타민 및 식이섬유")

    vitamin_col1, vitamin_col2, vitamin_col3 = st.columns(3)

    with vitamin_col1:
        st.metric("비타민 A", f"{totals['vitamin_a']:.1f} μg")

    with vitamin_col2:
        st.metric("비타민 C", f"{totals['vitamin_c']:.1f} mg")

    with vitamin_col3:
        st.metric("비타민 D", f"{totals['vitamin_d']:.1f} μg")

    st.metric("식이섬유", f"{totals['fiber']:.1f} g")

    # --------------------------------------------------
    # 끼니별 에너지
    # --------------------------------------------------
    st.markdown("#### 🍽️ 끼니별 에너지 구성")

    meal_energy_df = pd.DataFrame([
        {
            "끼니": meal_name,
            "에너지(kcal)": foods[food_name]["kcal"],
        }
        for meal_name, food_name in selected_meal.items()
        if meal_name != "일차"
    ])

    fig_meal = px.bar(
        meal_energy_df,
        x="끼니",
        y="에너지(kcal)",
        text="에너지(kcal)",
        title="끼니별 에너지",
    )

    fig_meal.update_layout(
        paper_bgcolor="#FBF9F1",
        plot_bgcolor="#FBF9F1",
        font=dict(family="Gowun Dodum"),
        showlegend=False,
        xaxis_title="",
        yaxis_title="에너지 (kcal)",
    )

    st.plotly_chart(fig_meal, use_container_width=True)

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
            ["비타민 A", f"{totals['vitamin_a']:.1f}", "μg"],
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

    st.button(
        "🍽️ 식사 기록 & 영양 관리로 이동하기 →",
        key="go_to_record",
        use_container_width=True,
        on_click=lambda: st.switch_page("pages/record.py"),
    )

else:
    st.info("식단 생성 버튼을 눌러 나만의 식단을 만들어 보세요!")
