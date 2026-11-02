import streamlit as st
import pandas as pd
import plotly.express as px
import random
import calendar
from datetime import date, timedelta

# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="한 달 맞춤 식단 | NutriDay",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# 디자인
# ==================================================

st.markdown("""
<style>
    html, body, p, label,
    h1, h2, h3, h4, h5, h6,
    .stMarkdown,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {
        font-family: 'Gowun Dodum', sans-serif !important;
    }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #377D61;
        margin-bottom: 0.3rem;
    }

    .sub-text {
        color: #777777;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .meal-card {
        background-color: #F1F8F3;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .nutriday-table-wrap {
        width: 100%;
        overflow-x: auto;
        border: 1px solid #DCEADF;
        border-radius: 12px;
        background: #FFFFFF;
        margin: 0.5rem 0 1rem;
    }

    .nutriday-table {
        width: 100%;
        border-collapse: collapse;
        color: #263B32;
        font-size: 0.92rem;
    }

    .nutriday-table th {
        background: #EEF6EF;
        color: #377D61;
        font-weight: 700;
        padding: 0.7rem;
        text-align: center;
        white-space: nowrap;
        border-bottom: 1px solid #DCEADF;
    }

    .nutriday-table td {
        padding: 0.65rem;
        text-align: center;
        border-bottom: 1px solid #EDF2ED;
    }

    .nutriday-table tr:last-child td {
        border-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


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
    "meal_plan_calories"
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

if daily_energy is None:
    daily_energy = 2000.0
    energy_from_previous_page = False
else:
    energy_from_previous_page = True


st.markdown("### 🔥 나의 하루 에너지")

if energy_from_previous_page:
    st.success(
        f"이전 페이지에서 계산한 값: "
        f"{daily_energy:,.0f} kcal"
    )
else:
    st.info(
        "이전 페이지의 계산값을 찾지 못해 "
        "2,000 kcal를 예시값으로 사용하고 있어요."
    )

    daily_energy = st.number_input(
        "하루 에너지 참고값 (kcal)",
        min_value=500,
        max_value=6000,
        value=2000,
        step=100
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
            "다양한 영양소 섭취"
        ]
    )

    meal_style = st.selectbox(
        "선호하는 식사 유형",
        [
            "한식 위주",
            "간편식 위주",
            "다양하게 구성"
        ]
    )

    meal_count = st.radio(
        "하루 식사 횟수",
        [
            "하루 세 끼",
            "세 끼 + 간식"
        ],
        horizontal=True
    )

with col2:

    preference_options = [
        "닭고기",
        "생선",
        "달걀",
        "두부",
        "소고기",
        "돼지고기",
        "채소",
        "과일",
        "직접 입력"
    ]

    preference = st.multiselect(
        "선호하는 음식",
        preference_options,
        default=["닭고기", "달걀", "채소"]
    )

    custom_preference = []

    if "직접 입력" in preference:
        custom_preference_text = st.text_input(
            "선호하는 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타 (쉼표로 구분)",
            key="custom_preference_text"
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
        "닭고기",
        "생선",
        "달걀",
        "두부",
        "소고기",
        "돼지고기",
        "우유",
        "견과류",
        "직접 입력"
    ]

    excluded_foods = st.multiselect(
        "식단에서 제외할 음식",
        excluded_options
    )

    custom_excluded = []

    if "직접 입력" in excluded_foods:
        custom_excluded_text = st.text_input(
            "제외할 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타 (쉼표로 구분)",
            key="custom_excluded_text"
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
        "직접 입력은 쉼표로 구분해 주세요. 입력한 단어는 기존 메뉴 이름이나 "
        "음식 분류와 비교해 반영돼요. 실제 메뉴의 모든 재료를 판별하는 기능은 아니에요."
    )

    st.caption(
        "알레르기가 있다면 해당 식품을 반드시 제외하고, "
        "교차접촉 위험도 별도로 확인해야 해요."
    )


# ==================================================
# 음식 데이터
# ==================================================

foods = {

    "닭고기 덮밥": {
        "group": "닭고기",
        "style": "한식",
        "kcal": 450,
        "carbs": 65,
        "protein": 28,
        "fat": 9,
        "fiber": 4,
        "calcium": 45,
        "iron": 2.0,
        "potassium": 430,
        "sodium": 450,
        "vitamin_a": 35,
        "vitamin_c": 12,
        "vitamin_d": 0.2
    },

    "두부 비빔밥": {
        "group": "두부",
        "style": "한식",
        "kcal": 430,
        "carbs": 68,
        "protein": 18,
        "fat": 10,
        "fiber": 7,
        "calcium": 160,
        "iron": 3.0,
        "potassium": 620,
        "sodium": 500,
        "vitamin_a": 180,
        "vitamin_c": 18,
        "vitamin_d": 0
    },

    "생선구이 정식": {
        "group": "생선",
        "style": "한식",
        "kcal": 470,
        "carbs": 65,
        "protein": 27,
        "fat": 12,
        "fiber": 5,
        "calcium": 55,
        "iron": 2.0,
        "potassium": 520,
        "sodium": 480,
        "vitamin_a": 30,
        "vitamin_c": 15,
        "vitamin_d": 5
    },

    "소고기 채소볶음 정식": {
        "group": "소고기",
        "style": "한식",
        "kcal": 490,
        "carbs": 62,
        "protein": 29,
        "fat": 13,
        "fiber": 5,
        "calcium": 60,
        "iron": 3.5,
        "potassium": 480,
        "sodium": 520,
        "vitamin_a": 100,
        "vitamin_c": 20,
        "vitamin_d": 0.2
    },

    "돼지고기 채소볶음": {
        "group": "돼지고기",
        "style": "한식",
        "kcal": 480,
        "carbs": 60,
        "protein": 25,
        "fat": 15,
        "fiber": 5,
        "calcium": 50,
        "iron": 2.5,
        "potassium": 450,
        "sodium": 550,
        "vitamin_a": 90,
        "vitamin_c": 18,
        "vitamin_d": 0.5
    },

    "달걀 채소볶음밥": {
        "group": "달걀",
        "style": "한식",
        "kcal": 420,
        "carbs": 62,
        "protein": 15,
        "fat": 12,
        "fiber": 4,
        "calcium": 65,
        "iron": 2.0,
        "potassium": 350,
        "sodium": 430,
        "vitamin_a": 140,
        "vitamin_c": 15,
        "vitamin_d": 1.2
    },

    "닭고기 샐러드": {
        "group": "닭고기",
        "style": "간편식",
        "kcal": 350,
        "carbs": 25,
        "protein": 30,
        "fat": 13,
        "fiber": 6,
        "calcium": 90,
        "iron": 2.5,
        "potassium": 600,
        "sodium": 400,
        "vitamin_a": 250,
        "vitamin_c": 35,
        "vitamin_d": 0.2
    },

    "두부 샐러드": {
        "group": "두부",
        "style": "간편식",
        "kcal": 320,
        "carbs": 28,
        "protein": 17,
        "fat": 14,
        "fiber": 7,
        "calcium": 180,
        "iron": 3.0,
        "potassium": 520,
        "sodium": 350,
        "vitamin_a": 220,
        "vitamin_c": 30,
        "vitamin_d": 0
    },

    "통밀빵과 달걀": {
        "group": "달걀",
        "style": "간편식",
        "kcal": 330,
        "carbs": 40,
        "protein": 17,
        "fat": 11,
        "fiber": 5,
        "calcium": 100,
        "iron": 2.5,
        "potassium": 280,
        "sodium": 420,
        "vitamin_a": 110,
        "vitamin_c": 0,
        "vitamin_d": 1.0
    },

    "오트밀과 우유": {
        "group": "우유",
        "style": "간편식",
        "kcal": 350,
        "carbs": 52,
        "protein": 14,
        "fat": 9,
        "fiber": 7,
        "calcium": 300,
        "iron": 2.5,
        "potassium": 480,
        "sodium": 150,
        "vitamin_a": 70,
        "vitamin_c": 2,
        "vitamin_d": 2.5
    },

    "과일과 요구르트": {
        "group": "과일",
        "style": "간편식",
        "kcal": 200,
        "carbs": 35,
        "protein": 7,
        "fat": 4,
        "fiber": 4,
        "calcium": 220,
        "iron": 0.5,
        "potassium": 350,
        "sodium": 90,
        "vitamin_a": 30,
        "vitamin_c": 35,
        "vitamin_d": 0.5
    },

    "밥과 두부조림": {
        "group": "두부",
        "style": "한식",
        "kcal": 400,
        "carbs": 63,
        "protein": 18,
        "fat": 9,
        "fiber": 4,
        "calcium": 170,
        "iron": 2.5,
        "potassium": 400,
        "sodium": 400,
        "vitamin_a": 50,
        "vitamin_c": 8,
        "vitamin_d": 0
    },

    "고구마와 달걀": {
        "group": "달걀",
        "style": "다양",
        "kcal": 320,
        "carbs": 48,
        "protein": 13,
        "fat": 8,
        "fiber": 6,
        "calcium": 60,
        "iron": 1.5,
        "potassium": 550,
        "sodium": 180,
        "vitamin_a": 600,
        "vitamin_c": 15,
        "vitamin_d": 1
    },

    "생선 샐러드": {
        "group": "생선",
        "style": "간편식",
        "kcal": 360,
        "carbs": 25,
        "protein": 27,
        "fat": 15,
        "fiber": 6,
        "calcium": 100,
        "iron": 2.0,
        "potassium": 500,
        "sodium": 420,
        "vitamin_a": 180,
        "vitamin_c": 30,
        "vitamin_d": 5
    },

    "채소 비빔밥": {
        "group": "채소",
        "style": "한식",
        "kcal": 400,
        "carbs": 70,
        "protein": 11,
        "fat": 9,
        "fiber": 8,
        "calcium": 100,
        "iron": 3.0,
        "potassium": 650,
        "sodium": 430,
        "vitamin_a": 280,
        "vitamin_c": 25,
        "vitamin_d": 0
    },

    "과일 오트밀": {
        "group": "과일",
        "style": "간편식",
        "kcal": 330,
        "carbs": 55,
        "protein": 11,
        "fat": 8,
        "fiber": 8,
        "calcium": 180,
        "iron": 2.5,
        "potassium": 430,
        "sodium": 120,
        "vitamin_a": 30,
        "vitamin_c": 25,
        "vitamin_d": 1.5
    },

    "닭고기 채소볶음": {
        "group": "닭고기",
        "style": "다양",
        "kcal": 430,
        "carbs": 45,
        "protein": 32,
        "fat": 12,
        "fiber": 6,
        "calcium": 80,
        "iron": 2.5,
        "potassium": 520,
        "sodium": 420,
        "vitamin_a": 180,
        "vitamin_c": 35,
        "vitamin_d": 0.2
    },

    "소고기 덮밥": {
        "group": "소고기",
        "style": "다양",
        "kcal": 470,
        "carbs": 62,
        "protein": 27,
        "fat": 13,
        "fiber": 4,
        "calcium": 45,
        "iron": 3.5,
        "potassium": 430,
        "sodium": 480,
        "vitamin_a": 25,
        "vitamin_c": 12,
        "vitamin_d": 0.2
    },

    "돼지고기 덮밥": {
        "group": "돼지고기",
        "style": "다양",
        "kcal": 460,
        "carbs": 63,
        "protein": 25,
        "fat": 12,
        "fiber": 4,
        "calcium": 40,
        "iron": 2.2,
        "potassium": 420,
        "sodium": 500,
        "vitamin_a": 25,
        "vitamin_c": 10,
        "vitamin_d": 0.4
    },

    "두부 채소덮밥": {
        "group": "두부",
        "style": "다양",
        "kcal": 420,
        "carbs": 62,
        "protein": 19,
        "fat": 11,
        "fiber": 7,
        "calcium": 180,
        "iron": 3.0,
        "potassium": 560,
        "sodium": 400,
        "vitamin_a": 200,
        "vitamin_c": 25,
        "vitamin_d": 0
    }
}


# ==================================================
# 음식 후보 생성
# ==================================================

def matches_food(name, info, terms):
    """입력한 단어가 기존 메뉴 이름 또는 음식 분류와 일치하는지 확인한다."""
    name_lower = name.casefold()
    group_lower = str(info.get("group", "")).casefold()

    return any(
        term.casefold() in name_lower or term.casefold() in group_lower
        for term in terms
        if term.strip()
    )


def get_food_candidates(style, excluded):
    candidates = []

    for name, info in foods.items():

        if matches_food(name, info, excluded):
            continue

        if style == "한식 위주":
            if info["style"] not in ["한식", "다양"]:
                continue

        elif style == "간편식 위주":
            if info["style"] not in ["간편식", "다양"]:
                continue

        candidates.append(name)

    return candidates


# ==================================================
# 식단 생성
# ==================================================

def generate_monthly_plan(
    style,
    preference,
    excluded,
    meal_count,
    seed=None
):
    """
    30일 식단 생성.

    선호 음식은 후보 선정에 우선 반영한다.
    최근 메뉴의 반복을 줄이되, 같은 음식이 무조건 제외되는
    것은 아니므로 음식 후보 수가 적을 때도 생성할 수 있다.
    """

    rng = random.Random(seed)

    candidates = get_food_candidates(style, excluded)

    if not candidates:
        return None

    preferred_candidates = [
        name for name in candidates
        if matches_food(name, foods[name], preference)
    ]

    # 선호 메뉴를 더 자주 선택하되, 식단 다양성도 유지한다.

    plan = []
    recent_meals = []

    meal_names = ["아침", "점심", "저녁"]

    if meal_count == "세 끼 + 간식":
        meal_names.append("간식")

    for day in range(1, 31):

        day_plan = {
            "일차": day
        }

        for meal_name in meal_names:

            available = [
                name for name in candidates
                if name not in recent_meals[-6:]
            ]

            if not available:
                available = candidates.copy()

            preferred_available = [
                name for name in available
                if matches_food(name, foods[name], preference)
            ]

            if preferred_available and rng.random() < 0.7:
                chosen = rng.choice(preferred_available)
            else:
                chosen = rng.choice(available)

            day_plan[meal_name] = chosen

            recent_meals.append(chosen)

            if len(recent_meals) > 12:
                recent_meals.pop(0)

        plan.append(day_plan)

    return plan


# ==================================================
# 식단 생성 버튼
# ==================================================

st.divider()
st.markdown("### 📅 30일 식단표 만들기")

st.write(
    "설정한 조건에 맞춰 30일 메뉴를 자동으로 구성해요. "
    "생성된 식단은 날짜별로 확인하고 다시 추천받을 수 있어요."
)

if st.button(
    "✨ 나만의 한 달 식단 생성하기",
    use_container_width=True
):

    new_plan = generate_monthly_plan(
        style=meal_style,
        preference=all_preferences,
        excluded=all_excluded,
        meal_count=meal_count,
        seed=None
    )

    if new_plan is None:
        st.error(
            "현재 제외 조건에 맞는 음식이 없어요. "
            "제외할 음식 설정을 조정해 주세요."
        )

    else:
        st.session_state["monthly_plan"] = new_plan
        st.session_state["monthly_plan_settings"] = {
            "style": meal_style,
            "preference": all_preferences,
            "excluded": all_excluded,
            "meal_count": meal_count,
            "goal": goal,
            "energy": daily_energy
        }
# ==================================================
# 생성된 식단 출력
# ==================================================

if "monthly_plan" in st.session_state:
    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    plan = st.session_state["monthly_plan"]

    st.success("30일 식단이 생성되었어요!")

    selected_day = st.selectbox(
        "확인할 날짜를 선택하세요.",
        options=list(range(1, 31)),
        format_func=lambda x: f"{x}일 차",
        key="selected_day"
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
            st.markdown(
                f"""
                <div class="meal-card">
                    <b>{meal_name}</b><br>
                    {selected_meal[meal_name]}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("#### 📋 전체 30일 식단표")

    plan_df = pd.DataFrame(plan)

    st.markdown(
        '<div class="nutriday-table-wrap">'
        + plan_df.to_html(
            index=False,
            border=0,
            classes="nutriday-table"
        )
        + '</div>',
        unsafe_allow_html=True
    )

    st.download_button(
        "📥 30일 식단표 다운로드",
        data=plan_df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="NutriDay_30day_meal_plan.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("식단 생성 버튼을 눌러 나만의 식단을 만들어 보세요!")
