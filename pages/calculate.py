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

    st.page_link("main.py", label="🏠 메인 페이지")
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

# 모든 영양 성분 수치는 1회 분량 기준의 예시값이다.
# 실제 제품 및 조리법에 따른 영양 성분과 다를 수 있다.

foods = {
    "닭고기 덮밥": {
        "group": "닭고기", "style": "한식",
        "kcal": 450, "carbs": 65, "protein": 28, "fat": 9,
        "fiber": 4, "calcium": 45, "iron": 2.0,
        "potassium": 430, "sodium": 450,
        "vitamin_a": 35, "vitamin_c": 12, "vitamin_d": 0.2
    },
    "두부 비빔밥": {
        "group": "두부", "style": "한식",
        "kcal": 430, "carbs": 68, "protein": 18, "fat": 10,
        "fiber": 7, "calcium": 160, "iron": 3.0,
        "potassium": 620, "sodium": 500,
        "vitamin_a": 180, "vitamin_c": 18, "vitamin_d": 0
    },
    "생선구이 정식": {
        "group": "생선", "style": "한식",
        "kcal": 470, "carbs": 65, "protein": 27, "fat": 12,
        "fiber": 5, "calcium": 55, "iron": 2.0,
        "potassium": 520, "sodium": 480,
        "vitamin_a": 30, "vitamin_c": 15, "vitamin_d": 5
    },
    "소고기 채소볶음 정식": {
        "group": "소고기", "style": "한식",
        "kcal": 490, "carbs": 62, "protein": 29, "fat": 13,
        "fiber": 5, "calcium": 60, "iron": 3.5,
        "potassium": 480, "sodium": 520,
        "vitamin_a": 100, "vitamin_c": 20, "vitamin_d": 0.2
    },
    "돼지고기 채소볶음": {
        "group": "돼지고기", "style": "한식",
        "kcal": 480, "carbs": 60, "protein": 25, "fat": 15,
        "fiber": 5, "calcium": 50, "iron": 2.5,
        "potassium": 450, "sodium": 550,
        "vitamin_a": 90, "vitamin_c": 18, "vitamin_d": 0.5
    },
    "달걀 채소볶음밥": {
        "group": "달걀", "style": "한식",
        "kcal": 420, "carbs": 62, "protein": 15, "fat": 12,
        "fiber": 4, "calcium": 65, "iron": 2.0,
        "potassium": 350, "sodium": 430,
        "vitamin_a": 140, "vitamin_c": 15, "vitamin_d": 1.2
    },
    "닭고기 샐러드": {
        "group": "닭고기", "style": "간편식",
        "kcal": 350, "carbs": 25, "protein": 30, "fat": 13,
        "fiber": 6, "calcium": 90, "iron": 2.5,
        "potassium": 600, "sodium": 400,
        "vitamin_a": 250, "vitamin_c": 35, "vitamin_d": 0.2
    },
    "두부 샐러드": {
        "group": "두부", "style": "간편식",
        "kcal": 320, "carbs": 28, "protein": 17, "fat": 14,
        "fiber": 7, "calcium": 180, "iron": 3.0,
        "potassium": 520, "sodium": 350,
        "vitamin_a": 220, "vitamin_c": 30, "vitamin_d": 0
    },
    "통밀빵과 달걀": {
        "group": "달걀", "style": "간편식",
        "kcal": 330, "carbs": 40, "protein": 17, "fat": 11,
        "fiber": 5, "calcium": 100, "iron": 2.5,
        "potassium": 280, "sodium": 420,
        "vitamin_a": 110, "vitamin_c": 0, "vitamin_d": 1.0
    },
    "오트밀과 우유": {
        "group": "우유", "style": "간편식",
        "kcal": 350, "carbs": 52, "protein": 14, "fat": 9,
        "fiber": 7, "calcium": 300, "iron": 2.5,
        "potassium": 480, "sodium": 150,
        "vitamin_a": 70, "vitamin_c": 2, "vitamin_d": 2.5
    },
    "과일과 요구르트": {
        "group": "과일", "style": "간편식",
        "kcal": 200, "carbs": 35, "protein": 7, "fat": 4,
        "fiber": 4, "calcium": 220, "iron": 0.5,
        "potassium": 350, "sodium": 90,
        "vitamin_a": 30, "vitamin_c": 35, "vitamin_d": 0.5
    },
    "밥과 두부조림": {
        "group": "두부", "style": "한식",
        "kcal": 400, "carbs": 63, "protein": 18, "fat": 9,
        "fiber": 4, "calcium": 170, "iron": 2.5,
        "potassium": 400, "sodium": 400,
        "vitamin_a": 50, "vitamin_c": 8, "vitamin_d": 0
    },
    "고구마와 삶은 달걀": {
        "group": "달걀", "style": "간편식",
        "kcal": 280, "carbs": 43, "protein": 13, "fat": 6,
        "fiber": 6, "calcium": 55, "iron": 1.5,
        "potassium": 520, "sodium": 180,
        "vitamin_a": 20, "vitamin_c": 15, "vitamin_d": 1.0
    },
    "과일 견과류": {
        "group": "과일", "style": "간편식",
        "kcal": 220, "carbs": 28, "protein": 5, "fat": 11,
        "fiber": 5, "calcium": 45, "iron": 1.2,
        "potassium": 300, "sodium": 20,
        "vitamin_a": 10, "vitamin_c": 25, "vitamin_d": 0
    },
    "바나나와 우유": {
        "group": "우유", "style": "간편식",
        "kcal": 210, "carbs": 34, "protein": 8, "fat": 5,
        "fiber": 3, "calcium": 240, "iron": 0.3,
        "potassium": 500, "sodium": 100,
        "vitamin_a": 60, "vitamin_c": 10, "vitamin_d": 2.0
    },
    "채소 주먹밥": {
        "group": "채소", "style": "간편식",
        "kcal": 300, "carbs": 52, "protein": 7, "fat": 7,
        "fiber": 4, "calcium": 50, "iron": 1.5,
        "potassium": 250, "sodium": 300,
        "vitamin_a": 80, "vitamin_c": 15, "vitamin_d": 0
    },
    "참치 샌드위치": {
        "group": "생선", "style": "간편식",
        "kcal": 370, "carbs": 42, "protein": 22, "fat": 12,
        "fiber": 5, "calcium": 100, "iron": 2.0,
        "potassium": 330, "sodium": 520,
        "vitamin_a": 35, "vitamin_c": 8, "vitamin_d": 1.5
    },
    "채소 달걀말이": {
        "group": "달걀", "style": "한식",
        "kcal": 180, "carbs": 5, "protein": 13, "fat": 12,
        "fiber": 2, "calcium": 65, "iron": 1.5,
        "potassium": 180, "sodium": 250,
        "vitamin_a": 150, "vitamin_c": 10, "vitamin_d": 1.2
    },
    "사과와 땅콩버터": {
        "group": "과일", "style": "간편식",
        "kcal": 190, "carbs": 25, "protein": 5, "fat": 9,
        "fiber": 4, "calcium": 20, "iron": 0.5,
        "potassium": 220, "sodium": 80,
        "vitamin_a": 5, "vitamin_c": 5, "vitamin_d": 0
    },
    "그릭요거트와 과일": {
        "group": "우유", "style": "간편식",
        "kcal": 230, "carbs": 30, "protein": 15, "fat": 5,
        "fiber": 4, "calcium": 180, "iron": 0.3,
        "potassium": 300, "sodium": 70,
        "vitamin_a": 40, "vitamin_c": 20, "vitamin_d": 0.5
    },
    "채소와 후무스": {
        "group": "채소", "style": "간편식",
        "kcal": 170, "carbs": 20, "protein": 6, "fat": 8,
        "fiber": 6, "calcium": 50, "iron": 1.5,
        "potassium": 250, "sodium": 180,
        "vitamin_a": 100, "vitamin_c": 20, "vitamin_d": 0
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

        st.session_state.pop(
            "selected_day",
            None
        )

        st.success("30일 식단표를 생성했어요!")


# ==================================================
# 식단이 생성된 경우에만 표시
# ==================================================

if "monthly_plan" in st.session_state:

    plan = st.session_state["monthly_plan"]

    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    st.caption(
        "각 날짜의 메뉴를 확인할 수 있어요. "
        "식단을 다시 생성하면 새로운 메뉴 조합이 만들어져요."
    )

    plan_df = pd.DataFrame(plan)

    # DataFrame 전용 렌더링 대신 HTML 표 사용
    plan_html = plan_df.to_html(
        index=False,
        border=0,
        classes="nutriday-table",
        escape=True
    )

    st.markdown(
        f'<div class="nutriday-table-wrap">{plan_html}</div>',
        unsafe_allow_html=True
    )

    st.divider()
    st.markdown("### 🔍 날짜별 식단 확인")

    selected_day = st.selectbox(
        "확인할 날짜를 선택하세요.",
        options=list(range(1, 31)),
        format_func=lambda x: f"{x}일차",
        key="selected_day"
    )

    selected_plan = next(
        item for item in plan
        if item["일차"] == selected_day
    )

meal_names = [
    (meal_name, food_name)
    for meal_name, food_name in selected_plan.items()
    if meal_name != "일차"
]

meal_columns = st.columns(len(meal_names))

for index, (meal_name, food_name) in enumerate(meal_names):

    with meal_columns[index]:

        st.markdown(
            f"""
            <div class="meal-card">
                <h4>{meal_name}</h4>
                <p>{food_name}</p>
                <small>{foods[food_name]["kcal"]} kcal</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ==============================================
    # 영양소 계산
    # ==============================================

    st.markdown("### 📊 식단 영양소 분석")

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

    nutrient_names = {
        "kcal": "에너지(kcal)",
        "carbs": "탄수화물(g)",
        "protein": "단백질(g)",
        "fat": "지방(g)",
        "fiber": "식이섬유(g)",
        "calcium": "칼슘(mg)",
        "iron": "철(mg)",
        "potassium": "칼륨(mg)",
        "sodium": "나트륨(mg)",
        "vitamin_a": "비타민 A(μg)",
        "vitamin_c": "비타민 C(mg)",
        "vitamin_d": "비타민 D(μg)"
    }

    selected_foods = [
        food_name
        for meal_name, food_name in selected_plan.items()
        if meal_name != "일차"
    ]

    daily_nutrients = {
        key: sum(
            foods[food_name].get(key, 0)
            for food_name in selected_foods
        )
        for key in nutrient_keys
    }

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            "에너지",
            f'{daily_nutrients["kcal"]:,.0f} kcal'
        )

    with metric2:
        st.metric(
            "탄수화물",
            f'{daily_nutrients["carbs"]:.1f} g'
        )

    with metric3:
        st.metric(
            "단백질",
            f'{daily_nutrients["protein"]:.1f} g'
        )

    with metric4:
        st.metric(
            "지방",
            f'{daily_nutrients["fat"]:.1f} g'
        )

    # ==============================================
    # 탄단지 에너지 비율
    # ==============================================

    st.markdown("#### 🍚 탄수화물·단백질·지방 에너지 비율")

    macro_energy = {
        "탄수화물": daily_nutrients["carbs"] * 4,
        "단백질": daily_nutrients["protein"] * 4,
        "지방": daily_nutrients["fat"] * 9
    }

    total_macro_energy = sum(macro_energy.values())

    if total_macro_energy > 0:

        macro_df = pd.DataFrame({
            "영양소": list(macro_energy.keys()),
            "에너지": list(macro_energy.values())
        })

        fig_macro = px.pie(
            macro_df,
            names="영양소",
            values="에너지",
            hole=0.45,
            title="탄단지 에너지 구성 비율"
        )

        fig_macro.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )
        st.plotly_chart(
            fig_macro,
            use_container_width=True,
            key="macro_chart"
        )

    else:
        st.info("영양소 데이터가 없어 비율을 계산할 수 없어요.")

    # ==============================================
    # 영양소 분석표
    # ==============================================

    st.markdown("#### 🥦 상세 영양소")

    nutrient_rows = []

    for key in nutrient_keys:

        nutrient_rows.append({
            "영양소": nutrient_names[key],
            "섭취량": round(daily_nutrients[key], 2)
        })

    nutrient_df = pd.DataFrame(nutrient_rows)

    # DataFrame 전용 렌더링 대신 HTML 표 사용
    nutrient_html = nutrient_df.to_html(
        index=False,
        border=0,
        classes="nutriday-table",
        escape=True
    )

    st.markdown(
        f'<div class="nutriday-table-wrap">{nutrient_html}</div>',
        unsafe_allow_html=True
    )

    # ==============================================
    # 30일 전체 에너지 분석
    # ==============================================

    st.divider()
    st.markdown("### 📈 30일 식단 에너지 분석")

    monthly_energy = []

    for day_plan in plan:

        day_energy = sum(
            foods[food_name]["kcal"]
            for meal_name, food_name in day_plan.items()
            if meal_name != "일차"
        )

        monthly_energy.append({
            "날짜": f'{day_plan["일차"]}일차',
            "에너지(kcal)": day_energy
        })

    monthly_energy_df = pd.DataFrame(monthly_energy)

    fig_energy = px.line(
        monthly_energy_df,
        x="날짜",
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
        key="monthly_energy_chart"
    )

    # ==============================================
    # 안내
    # ==============================================

    st.divider()

    st.markdown("### 💡 알아두기")

    st.markdown("""
    - 영양 성분은 예시 데이터이므로 실제 음식의 중량과 조리법에 따라 달라질 수 있어요.
    - 비타민과 무기질은 에너지를 직접 제공하지 않으므로 탄수화물·단백질·지방의 에너지 비율과 별도로 표시해요.
    - 개인에게 적합한 식단은 성장 상태, 건강 상태, 활동량 등 다양한 요인에 따라 달라질 수 있어요.
    """)
