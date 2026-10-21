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

# 첫 번째 페이지에서 사용하는 세션 상태 키가 다를 수 있으므로
# 여러 후보를 확인하고, 값이 없으면 2000 kcal를 예시로 사용한다.

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

    preference = st.multiselect(
        "선호하는 음식",
        [
            "닭고기",
            "생선",
            "달걀",
            "두부",
            "소고기",
            "돼지고기",
            "채소",
            "과일"
        ],
        default=["닭고기", "달걀", "채소"]
    )

    excluded_foods = st.multiselect(
        "식단에서 제외할 음식",
        [
            "닭고기",
            "생선",
            "달걀",
            "두부",
            "소고기",
            "돼지고기",
            "우유",
            "견과류"
        ]
    )

    st.caption(
        "알레르기가 있다면 해당 식품을 반드시 제외하고, "
        "교차접촉 위험도 별도로 확인해야 해요."
    )


# ==================================================
# 음식 데이터
# ==================================================
#
# 모든 영양 성분 수치는 1회 분량 기준의 예시값이다.
# 실제 제품 및 조리법에 따른 영양 성분과 다를 수 있다.
#
# 영양소:
# kcal, carbs, protein, fat, fiber,
# calcium, iron, potassium, sodium,
# vitamin_a, vitamin_c, vitamin_d
#
# 비타민 A 단위: µg RAE
# 비타민 D 단위: µg
# 나머지 미량영양소: mg

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

def get_food_candidates(style, excluded):
    candidates = []

    for name, info in foods.items():

        if info["group"] in excluded:
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
        if foods[name]["group"] in preference
    ]

    # 선호 음식이 있으면 일부 후보에 포함한다.
    # 선호 음식만 사용하지는 않아 식단 다양성을 유지한다.
    if preferred_candidates:
        candidates = list(dict.fromkeys(
            preferred_candidates + candidates
        ))

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
        preference=preference,
        excluded=excluded_foods,
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
            "preference": preference,
            "excluded": excluded_foods,
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
        "식단은 입력 조건에 맞춰 자동으로 구성한 예시예요. "
        "실제 영양 성분을 검증한 전문 식단 처방은 아니에요."
    )

    # ----------------------------------------------
    # CSV 다운로드
    # ----------------------------------------------

    plan_df = pd.DataFrame(plan)

    csv_data = plan_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 한 달 식단표 CSV 다운로드",
        data=csv_data,
        file_name="NutriDay_30day_meal_plan.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ----------------------------------------------
    # 날짜 선택
    # ----------------------------------------------

    selected_day = st.selectbox(
        "자세히 확인할 날짜",
        options=list(range(1, 31)),
        format_func=lambda x: f"{x}일 차",
        key="selected_day"
    )

    selected_meal = plan[selected_day - 1]

    st.markdown(
        f"#### 🍽️ {selected_day}일 차 식단"
    )

    meal_columns = st.columns(
        len(selected_meal) - 1
    )

    meal_names = [
        key for key in selected_meal
        if key != "일차"
    ]

    for idx, meal_name in enumerate(meal_names):

        with meal_columns[idx]:

            st.markdown(
                f'<div class="meal-card">'
                f'<b>{meal_name}</b><br>'
                f'{selected_meal[meal_name]}'
                f'</div>',
                unsafe_allow_html=True
            )

    # ----------------------------------------------
    # 특정 날짜 식단 다시 추천
    # ----------------------------------------------

    if st.button(
        f"🔄 {selected_day}일 차 식단 다시 추천",
        use_container_width=True
    ):

        settings = st.session_state[
            "monthly_plan_settings"
        ]

        candidates = get_food_candidates(
            settings["style"],
            settings["excluded"]
        )

        preferred_candidates = [
            name for name in candidates
            if foods[name]["group"] in settings["preference"]
        ]

        if preferred_candidates:
            candidates = list(dict.fromkeys(
                preferred_candidates + candidates
            ))

        meal_names = [
            key for key in selected_meal
            if key != "일차"
        ]

        if not candidates:
            st.error(
                "추천 가능한 음식이 없어요. "
                "제외 조건을 조정해 주세요."
            )

        else:

            old_meals = [
                selected_meal[name]
                for name in meal_names
            ]

            for meal_name in meal_names:

                available = [
                    name for name in candidates
                    if name != selected_meal[meal_name]
                ]

                if not available:
                    available = candidates

                selected_meal[meal_name] = random.choice(
                    available
                )

            st.session_state["monthly_plan"][
                selected_day - 1
            ] = selected_meal

            st.rerun()

    # ----------------------------------------------
    # 전체 30일 표
    # ----------------------------------------------

    st.markdown("#### 📋 전체 식단표")

    st.dataframe(
        pd.DataFrame(plan),
        hide_index=True,
        use_container_width=True
    )

    # ==============================================
    # 영양소 계산
    # ==============================================

    def calculate_nutrients(meal):
        total = {
            "kcal": 0.0,
            "carbs": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "fiber": 0.0,
            "calcium": 0.0,
            "iron": 0.0,
            "potassium": 0.0,
            "sodium": 0.0,
            "vitamin_a": 0.0,
            "vitamin_c": 0.0,
            "vitamin_d": 0.0
        }

        for meal_name, food_name in meal.items():

            if meal_name == "일차":
                continue

            info = foods[food_name]

            for nutrient in total:
                total[nutrient] += info[nutrient]

        return total

    # ==============================================
    # 선택한 날짜 영양소 분석
    # ==============================================

    nutrients = calculate_nutrients(
        selected_meal
    )

    st.divider()
    st.markdown(
        f"### 📊 {selected_day}일 차 영양소 분석"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            "예시 식단 에너지",
            f"{nutrients['kcal']:,.0f} kcal"
        )

    with metric2:
        st.metric(
            "탄수화물",
            f"{nutrients['carbs']:.1f} g"
        )

    with metric3:
        st.metric(
            "단백질",
            f"{nutrients['protein']:.1f} g"
        )

    with metric4:
        st.metric(
            "지방",
            f"{nutrients['fat']:.1f} g"
        )

    # ----------------------------------------------
    # 탄단지 에너지 비율
    # ----------------------------------------------

    carb_kcal = nutrients["carbs"] * 4
    protein_kcal = nutrients["protein"] * 4
    fat_kcal = nutrients["fat"] * 9

    macro_total = (
        carb_kcal + protein_kcal + fat_kcal
    )

    st.markdown("#### 🥧 탄수화물·단백질·지방 에너지 비율")

    if macro_total > 0:

        macro_df = pd.DataFrame({
            "영양소": [
                "탄수화물",
                "단백질",
                "지방"
            ],
            "에너지량(kcal)": [
                carb_kcal,
                protein_kcal,
                fat_kcal
            ]
        })

        macro_df["비율(%)"] = (
            macro_df["에너지량(kcal)"]
            / macro_total * 100
        )

        fig = px.pie(
            macro_df,
            names="영양소",
            values="에너지량(kcal)",
            hole=0.55
        )

        fig.update_traces(
            texttemplate="%{label}<br>%{percent}",
            textposition="inside"
        )

        fig.update_layout(
            margin=dict(t=20, b=20, l=10, r=10),
            legend_title_text="영양소"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"macro_chart_{selected_day}"
        )

    # ----------------------------------------------
    # 비타민과 무기질
    # ----------------------------------------------

    st.markdown("#### 🧬 비타민·무기질·식이섬유")

    nutrient_df = pd.DataFrame({
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
        "예시 식단 함량": [
            f"{nutrients['fiber']:.1f} g",
            f"{nutrients['calcium']:.1f} mg",
            f"{nutrients['iron']:.1f} mg",
            f"{nutrients['potassium']:.1f} mg",
            f"{nutrients['sodium']:.1f} mg",
            f"{nutrients['vitamin_a']:.1f} µg RAE",
            f"{nutrients['vitamin_c']:.1f} mg",
            f"{nutrients['vitamin_d']:.1f} µg"
        ]
    })

    st.dataframe(
        nutrient_df,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "음식별 영양 성분은 구현 시험을 위한 예시값이며, "
        "실제 음식의 영양 성분과 다를 수 있어요."
    )

    # ==============================================
    # 30일 식단 요약
    # ==============================================

    st.divider()
    st.markdown("### 📈 30일 식단 요약")

    daily_rows = []

    for day_plan in plan:

        day_nutrients = calculate_nutrients(
            day_plan
        )

        daily_rows.append({
            "일차": day_plan["일차"],
            "에너지(kcal)": day_nutrients["kcal"],
            "탄수화물(g)": day_nutrients["carbs"],
            "단백질(g)": day_nutrients["protein"],
            "지방(g)": day_nutrients["fat"],
            "식이섬유(g)": day_nutrients["fiber"]
        })

    daily_df = pd.DataFrame(daily_rows)

    avg_energy = daily_df[
        "에너지(kcal)"
    ].mean()

    st.metric(
        "30일 식단의 하루 평균 에너지",
        f"{avg_energy:,.0f} kcal"
    )

    st.caption(
        f"하루 에너지 참고값: {daily_energy:,.0f} kcal. "
        "현재는 메뉴 조합을 생성하는 단계이므로 "
        "실제 식단 에너지가 참고값과 일치하지 않을 수 있어요."
    )

    fig_energy = px.line(
        daily_df,
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

    # ==============================================
    # 안내
    # ==============================================

    st.divider()

    st.markdown("### 💡 알아두기")

    st.markdown("""
    - 식단은 입력한 선호도와 제외 조건을 반영해 구성한 예시예요.
    - 현재 버전은 메뉴를 자동 조합하지만, 목표 에너지에 맞춰 음식의 분량을 최적화하지는 않아요.
    - 영양 성분은 예시 데이터이므로 실제 음식의 중량과 조리법에 따라 달라질 수 있어요.
    - 비타민과 무기질은 에너지를 직접 제공하지 않으므로 탄수화물·단백질·지방의 에너지 비율과 별도로 표시해요.
    - 개인에게 적합한 식단은 성장 상태, 건강 상태, 활동량 등 다양한 요인에 따라 달라질 수 있어요.
    """)
