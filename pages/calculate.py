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
    layout="wide"
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
</style>
""", unsafe_allow_html=True)


# ==================================================
# 사이드바
# ==================================================

with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")

    st.page_link(
        "main.py",
        label="🏠 메인 페이지"
    )

    st.page_link(
        "pages/calculate.py",
        label="🥗 한 달 맞춤 식단"
    )


# ==================================================
# 제목
# ==================================================

st.markdown(
    '<div class="main-title">🥗 나만의 한 달 식단</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-text">'
    '나의 생활 습관과 음식 선호도를 반영해 '
    '30일 식단을 구성하고 영양소를 분석해 보세요.'
    '</div>',
    unsafe_allow_html=True
)


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

    # --------------------------------------------------
    # 선호 음식 설정
    # --------------------------------------------------

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
        default=["닭고기", "달걀", "채소"],
        key="preference_select"
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
        [
            item
            for item in preference
            if item != "직접 입력"
        ]
        + custom_preference
    ))

    # --------------------------------------------------
    # 제외 음식 설정
    # --------------------------------------------------

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
        excluded_options,
        key="excluded_food_select"
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
        [
            item
            for item in excluded_foods
            if item != "직접 입력"
        ]
        + custom_excluded
    ))

    st.caption(
        "직접 입력은 쉼표로 구분해 주세요. "
        "입력한 단어는 기존 메뉴 이름이나 음식 분류와 "
        "비교해 반영돼요."
    )

    st.caption(
        "알레르기가 있다면 실제 재료와 제품의 알레르기 표시도 "
        "반드시 확인해 주세요."
    )


# ==================================================
# 음식 데이터
# ==================================================
#
# 아래 영양 성분 수치는 메뉴별 참고용 예시값이다.
# 실제 음식의 재료, 중량, 조리 방법에 따라 달라질 수 있다.
#
# 비타민 A: μg RAE
# 비타민 C: mg
# 비타민 D: μg
# 기타 무기질: mg
# ==================================================

foods = {
    "닭고기 덮밥": {
        "group": "닭고기",
        "style": "한식",
        "kcal": 450,
        "carbs": 60,
        "protein": 30,
        "fat": 10,
        "fiber": 4,
        "calcium": 50,
        "iron": 2.0,
        "potassium": 450,
        "sodium": 500,
        "vitamin_a": 40,
        "vitamin_c": 10,
        "vitamin_d": 0.2
    },

    "두부 비빔밥": {
        "group": "두부 채소",
        "style": "한식",
        "kcal": 420,
        "carbs": 65,
        "protein": 18,
        "fat": 10,
        "fiber": 7,
        "calcium": 180,
        "iron": 3.0,
        "potassium": 550,
        "sodium": 450,
        "vitamin_a": 180,
        "vitamin_c": 25,
        "vitamin_d": 0.1
    },

    "생선구이 정식": {
        "group": "생선",
        "style": "한식",
        "kcal": 480,
        "carbs": 62,
        "protein": 28,
        "fat": 12,
        "fiber": 5,
        "calcium": 70,
        "iron": 2.5,
        "potassium": 520,
        "sodium": 550,
        "vitamin_a": 30,
        "vitamin_c": 15,
        "vitamin_d": 5.0
    },

    "소고기 채소볶음 정식": {
        "group": "소고기 채소",
        "style": "한식",
        "kcal": 500,
        "carbs": 60,
        "protein": 30,
        "fat": 15,
        "fiber": 5,
        "calcium": 60,
        "iron": 3.5,
        "potassium": 500,
        "sodium": 520,
        "vitamin_a": 100,
        "vitamin_c": 20,
        "vitamin_d": 0.2
    },

    "돼지고기 채소볶음": {
        "group": "돼지고기 채소",
        "style": "한식",
        "kcal": 490,
        "carbs": 58,
        "protein": 27,
        "fat": 15,
        "fiber": 5,
        "calcium": 55,
        "iron": 2.5,
        "potassium": 480,
        "sodium": 530,
        "vitamin_a": 90,
        "vitamin_c": 22,
        "vitamin_d": 0.3
    },

    "달걀 채소볶음밥": {
        "group": "달걀 채소",
        "style": "한식",
        "kcal": 430,
        "carbs": 62,
        "protein": 17,
        "fat": 11,
        "fiber": 4,
        "calcium": 65,
        "iron": 2.2,
        "potassium": 400,
        "sodium": 450,
        "vitamin_a": 120,
        "vitamin_c": 18,
        "vitamin_d": 1.5
    },

    "닭고기 샐러드": {
        "group": "닭고기 채소",
        "style": "간편식",
        "kcal": 320,
        "carbs": 20,
        "protein": 30,
        "fat": 12,
        "fiber": 6,
        "calcium": 100,
        "iron": 2.0,
        "potassium": 600,
        "sodium": 350,
        "vitamin_a": 250,
        "vitamin_c": 35,
        "vitamin_d": 0.2
    },

    "두부 샐러드": {
        "group": "두부 채소",
        "style": "간편식",
        "kcal": 300,
        "carbs": 25,
        "protein": 18,
        "fat": 14,
        "fiber": 7,
        "calcium": 220,
        "iron": 3.0,
        "potassium": 550,
        "sodium": 300,
        "vitamin_a": 200,
        "vitamin_c": 40,
        "vitamin_d": 0.1
    },

    "통밀빵과 달걀": {
        "group": "달걀",
        "style": "간편식",
        "kcal": 350,
        "carbs": 42,
        "protein": 20,
        "fat": 11,
        "fiber": 6,
        "calcium": 100,
        "iron": 2.5,
        "potassium": 300,
        "sodium": 400,
        "vitamin_a": 100,
        "vitamin_c": 2,
        "vitamin_d": 1.2
    },

    "오트밀과 우유": {
        "group": "우유",
        "style": "간편식",
        "kcal": 330,
        "carbs": 48,
        "protein": 14,
        "fat": 9,
        "fiber": 6,
        "calcium": 250,
        "iron": 2.5,
        "potassium": 420,
        "sodium": 150,
        "vitamin_a": 80,
        "vitamin_c": 2,
        "vitamin_d": 2.0
    },

    "과일과 요구르트": {
        "group": "과일 우유",
        "style": "간편식",
        "kcal": 250,
        "carbs": 42,
        "protein": 10,
        "fat": 5,
        "fiber": 4,
        "calcium": 220,
        "iron": 0.8,
        "potassium": 400,
        "sodium": 100,
        "vitamin_a": 40,
        "vitamin_c": 35,
        "vitamin_d": 0.5
    },

    "밥과 두부조림": {
        "group": "두부",
        "style": "한식",
        "kcal": 400,
        "carbs": 60,
        "protein": 18,
        "fat": 10,
        "fiber": 4,
        "calcium": 180,
        "iron": 3.0,
        "potassium": 420,
        "sodium": 420,
        "vitamin_a": 25,
        "vitamin_c": 5,
        "vitamin_d": 0.1
    },

    "고구마와 달걀": {
        "group": "고구마 달걀",
        "style": "간편식",
        "kcal": 320,
        "carbs": 45,
        "protein": 15,
        "fat": 8,
        "fiber": 6,
        "calcium": 70,
        "iron": 1.8,
        "potassium": 500,
        "sodium": 180,
        "vitamin_a": 700,
        "vitamin_c": 20,
        "vitamin_d": 1.0
    },

    "생선 샐러드": {
        "group": "생선 채소",
        "style": "간편식",
        "kcal": 340,
        "carbs": 22,
        "protein": 27,
        "fat": 14,
        "fiber": 6,
        "calcium": 100,
        "iron": 2.0,
        "potassium": 550,
        "sodium": 320,
        "vitamin_a": 220,
        "vitamin_c": 35,
        "vitamin_d": 4.0
    },

    "채소 비빔밥": {
        "group": "채소",
        "style": "한식",
        "kcal": 390,
        "carbs": 68,
        "protein": 12,
        "fat": 8,
        "fiber": 8,
        "calcium": 90,
        "iron": 2.5,
        "potassium": 520,
        "sodium": 420,
        "vitamin_a": 300,
        "vitamin_c": 40,
        "vitamin_d": 0.1
    },

    "과일 오트밀": {
        "group": "과일",
        "style": "간편식",
        "kcal": 310,
        "carbs": 52,
        "protein": 10,
        "fat": 7,
        "fiber": 8,
        "calcium": 100,
        "iron": 2.5,
        "potassium": 450,
        "sodium": 100,
        "vitamin_a": 50,
        "vitamin_c": 30,
        "vitamin_d": 0.1
    },

    "닭고기 채소볶음": {
        "group": "닭고기 채소",
        "style": "다양",
        "kcal": 380,
        "carbs": 30,
        "protein": 32,
        "fat": 13,
        "fiber": 6,
        "calcium": 90,
        "iron": 2.2,
        "potassium": 520,
        "sodium": 420,
        "vitamin_a": 200,
        "vitamin_c": 30,
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
        "vitamin_a": 180,
        "vitamin_c": 35,
        "vitamin_d": 0.1
    }
}


# ==================================================
# 사용자 입력 조건 처리
# ==================================================

def split_terms(terms):
    """검색어 목록을 정리하고 중복을 제거한다."""
    result = []

    for term in terms:
        term = str(term).strip()

        if term and term not in result:
            result.append(term)

    return result


def matches_food(food_name, info, terms):
    """
    메뉴 이름과 음식 그룹에 검색어가 포함되는지 확인한다.
    실제 메뉴의 모든 재료를 분석하는 함수는 아니다.
    """
    name = str(food_name).casefold()
    group = str(info.get("group", "")).casefold()

    for term in terms:
        term = str(term).strip().casefold()

        if not term:
            continue

        if term in name or term in group:
            return True

    return False


def get_food_candidates(style, excluded):
    """식단 유형과 제외 음식 조건에 맞는 메뉴를 반환한다."""

    candidates = []

    for name, info in foods.items():
        food_style = info.get("style", "다양")

        if style == "한식 위주":
            if food_style not in ["한식", "다양"]:
                continue

        elif style == "간편식 위주":
            if food_style not in ["간편식", "다양"]:
                continue

        if matches_food(name, info, excluded):
            continue

        candidates.append(name)

    return candidates


# ==================================================
# 30일 식단 생성 함수
# ==================================================

def generate_monthly_plan(
    style,
    preference,
    excluded,
    meal_count,
    seed=None
):
    """설정한 조건에 따라 30일 식단을 생성한다."""

    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    preference = split_terms(preference)
    excluded = split_terms(excluded)

    candidates = get_food_candidates(
        style,
        excluded
    )

    if not candidates:
        return None

    preferred_candidates = [
        name
        for name in candidates
        if matches_food(
            name,
            foods[name],
            preference
        )
    ]

    if meal_count == "하루 세 끼":
        meal_names = ["아침", "점심", "저녁"]
    else:
        meal_names = ["아침", "점심", "저녁", "간식"]

    plan = []
    recent_meals = []

    for day in range(1, 31):
        day_plan = {"일차": day}
        used_today = set()

        for meal_name in meal_names:

            available = [
                name
                for name in candidates
                if name not in recent_meals
                and name not in used_today
            ]

            if not available:
                available = [
                    name
                    for name in candidates
                    if name not in used_today
                ]

            if not available:
                available = candidates.copy()

            available_preferred = [
                name
                for name in available
                if name in preferred_candidates
            ]

            if (
                available_preferred
                and rng.random() < 0.7
            ):
                chosen = rng.choice(
                    available_preferred
                )
            else:
                chosen = rng.choice(available)

            day_plan[meal_name] = chosen
            used_today.add(chosen)

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

    # 실제 위젯에서 정의한 변수명을 사용한다.
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
            "preference": all_preferences.copy(),
            "excluded": all_excluded.copy(),
            "meal_count": meal_count,
            "goal": goal,
            "energy": daily_energy
        }

        st.session_state.pop(
            "selected_day",
            None
        )

        st.success("30일 식단표를 생성했어요!")


# ==================================================
# 생성된 식단 표시
# ==================================================

if "monthly_plan" in st.session_state:

    plan = st.session_state["monthly_plan"]

    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    st.caption(
        "식단은 입력 조건에 맞춰 자동으로 구성한 예시예요. "
        "실제 영양 성분을 검증한 전문 식단 처방은 아니에요."
    )

    # --------------------------------------------------
    # CSV 다운로드
    # --------------------------------------------------

    plan_df = pd.DataFrame(plan)

    csv_data = plan_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 식단표 CSV 다운로드",
        data=csv_data,
        file_name="NutriDay_30일_식단표.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --------------------------------------------------
    # 날짜 선택
    # --------------------------------------------------

    selected_day = st.selectbox(
        "확인할 날짜를 선택하세요.",
        options=list(range(1, 31)),
        format_func=lambda day: f"{day}일차",
        key="selected_day"
    )

    selected_day_plan = plan[selected_day - 1]

    st.markdown(
        f"#### 🍽️ {selected_day}일차 식단"
    )

    meal_columns = [
        meal
        for meal in selected_day_plan.keys()
        if meal != "일차"
    ]

    columns = st.columns(len(meal_columns))

    for column, meal in zip(columns, meal_columns):
        with column:
            st.markdown(
                f"""
                <div class="meal-card">
                    <h4>{meal}</h4>
                    <p>{selected_day_plan[meal]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------
    # 선택 날짜 식단 다시 추천
    # --------------------------------------------------

    st.markdown("### 🔄 오늘의 식단 다시 추천")

    if st.button(
        "다른 메뉴로 다시 추천하기",
        use_container_width=True
    ):

        settings = st.session_state.get(
            "monthly_plan_settings",
            {}
        )

        current_style = settings.get(
            "style",
            meal_style
        )

        current_preference = settings.get(
            "preference",
            all_preferences
        )

        current_excluded = settings.get(
            "excluded",
            all_excluded
        )

        candidates = get_food_candidates(
            current_style,
            current_excluded
        )

        if not candidates:
            st.error(
                "현재 설정으로 추천할 수 있는 메뉴가 없어요. "
                "제외 조건을 변경해 주세요."
            )

        else:
            rng = random.Random()

            preferred_candidates = [
                name
                for name in candidates
                if matches_food(
                    name,
                    foods[name],
                    current_preference
                )
            ]

            new_day_plan = {
                "일차": selected_day
            }

            used_today = set()

            for meal in meal_columns:

                old_food = selected_day_plan.get(meal)

                available = [
                    name
                    for name in candidates
                    if name != old_food
                    and name not in used_today
                ]

                if not available:
                    available = [
                        name
                        for name in candidates
                        if name not in used_today
                    ]

                if not available:
                    available = candidates.copy()

                available_preferred = [
                    name
                    for name in available
                    if name in preferred_candidates
                ]

                if (
                    available_preferred
                    and rng.random() < 0.7
                ):
                    selected_food = rng.choice(
                        available_preferred
                    )
                else:
                    selected_food = rng.choice(
                        available
                    )

                new_day_plan[meal] = selected_food
                used_today.add(selected_food)

            # 해당 날짜의 메뉴만 갱신한다.
            plan[selected_day - 1] = new_day_plan

            st.session_state["monthly_plan"] = plan

            st.rerun()

    # --------------------------------------------------
    # 전체 식단표
    # --------------------------------------------------

    st.divider()
    st.markdown("### 📋 30일 전체 식단표")

    st.dataframe(
        pd.DataFrame(
            st.session_state["monthly_plan"]
        ),
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # 영양소 계산 함수
    # ==================================================

    def calculate_nutrients(day_plan):

        nutrient_keys = [
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
            "vitamin_d"
        ]

        totals = {
            key: 0.0
            for key in nutrient_keys
        }

        for meal_name, food_name in day_plan.items():

            if meal_name == "일차":
                continue

            food_info = foods.get(
                food_name,
                {}
            )

            for key in nutrient_keys:
                totals[key] += float(
                    food_info.get(key, 0)
                )

        return totals

    # ==================================================
    # 선택 날짜 영양 정보
    # ==================================================

    st.divider()

    st.markdown(
        f"### 🧪 {selected_day}일차 영양 정보"
    )

    # 다시 추천한 경우에도 최신 식단을 사용한다.
    selected_day_plan = st.session_state[
        "monthly_plan"
    ][selected_day - 1]

    nutrients = calculate_nutrients(
        selected_day_plan
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "에너지",
        f"{nutrients['kcal']:.0f} kcal"
    )

    metric2.metric(
        "탄수화물",
        f"{nutrients['carbs']:.1f} g"
    )

    metric3.metric(
        "단백질",
        f"{nutrients['protein']:.1f} g"
    )

    metric4.metric(
        "지방",
        f"{nutrients['fat']:.1f} g"
    )

    # --------------------------------------------------
    # 주요 영양소 그래프
    # --------------------------------------------------

    st.markdown(
        "#### 🥧 탄수화물 · 단백질 · 지방"
    )

    macro_df = pd.DataFrame({
        "영양소": [
            "탄수화물",
            "단백질",
            "지방"
        ],
        "함량(g)": [
            nutrients["carbs"],
            nutrients["protein"],
            nutrients["fat"]
        ]
    })

    macro_df = macro_df[
        macro_df["함량(g)"] > 0
    ]

    if not macro_df.empty:

        fig_macro = px.pie(
            macro_df,
            names="영양소",
            values="함량(g)",
            hole=0.55,
            title="선택한 날짜의 주요 영양소 구성"
        )

        fig_macro.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )

        st.plotly_chart(
            fig_macro,
            use_container_width=True
        )

    else:
        st.info(
            "표시할 영양소 데이터가 없어요."
        )

    # --------------------------------------------------
    # 기타 영양소
    # --------------------------------------------------

    st.markdown("#### 🥦 기타 영양소")

    nutrient_table = pd.DataFrame({
        "영양소": [
            "식이섬유",
            "칼슘",
            "철",
            "칼륨",
            "나트륨",
            "비타민 A",
            "비타민 C",
            "비타민 D"
        ],

        "함량": [
            f"{nutrients['fiber']:.1f} g",
            f"{nutrients['calcium']:.1f} mg",
            f"{nutrients['iron']:.1f} mg",
            f"{nutrients['potassium']:.1f} mg",
            f"{nutrients['sodium']:.1f} mg",
            f"{nutrients['vitamin_a']:.1f} μg RAE",
            f"{nutrients['vitamin_c']:.1f} mg",
            f"{nutrients['vitamin_d']:.1f} μg"
        ]
    })

    st.dataframe(
        nutrient_table,
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # 30일 에너지 추이
    # ==================================================

    st.divider()
    st.markdown("### 📈 30일 에너지 추이")

    energy_records = []

    for day_plan in st.session_state["monthly_plan"]:

        day_nutrients = calculate_nutrients(
            day_plan
        )

        energy_records.append({
            "일차": day_plan["일차"],
            "에너지(kcal)": day_nutrients["kcal"]
        })

    energy_df = pd.DataFrame(
        energy_records
    )

    average_energy = energy_df[
        "에너지(kcal)"
    ].mean()

    st.metric(
        "30일 식단의 하루 평균 에너지",
        f"{average_energy:.0f} kcal"
    )

    fig_energy = px.line(
        energy_df,
        x="일차",
        y="에너지(kcal)",
        markers=True,
        title="날짜별 예시 식단 에너지"
    )

    fig_energy.update_layout(
        xaxis_title="날짜",
        yaxis_title="에너지(kcal)"
    )

    st.plotly_chart(
        fig_energy,
        use_container_width=True
    )

    # ==================================================
    # 안내
    # ==================================================

    st.divider()

    st.markdown("### 💡 알아두기")

    st.markdown("""
    - 식단은 입력한 선호도와 제외 조건을 반영해 구성한 예시예요.
    - 현재 버전은 메뉴를 자동 조합하지만, 목표 에너지에 맞춰 음식의 분량을 최적화하지는 않아요.
    - 영양 성분은 예시 데이터이므로 실제 음식의 중량과 조리법에 따라 달라질 수 있어요.
    - 비타민과 무기질은 에너지를 직접 제공하지 않으므로 탄수화물·단백질·지방의 에너지 비율과 별도로 표시해요.
    - 개인에게 적합한 식단은 성장 상태, 건강 상태, 활동량 등 다양한 요인에 따라 달라질 수 있어요.
    """)
