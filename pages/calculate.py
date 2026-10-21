import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="한 달 맞춤 식단 | NutriDay",
    page_icon="🥗",
    layout="wide"
)

# ==================================================
# Streamlit 기본 페이지 메뉴 숨기기
# ==================================================

st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

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
# 하루 에너지 참고값
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

st.markdown("### 🔥 나의 하루 에너지")

if daily_energy is not None:
    st.success(
        f"이전 페이지에서 계산한 값: "
        f"{daily_energy:,.0f} kcal"
    )
else:
    st.info(
        "이전 페이지의 계산값을 찾지 못했어요. "
        "참고값을 직접 입력해 주세요."
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
        default=["닭고기", "달걀", "채소"],
        key="preference_select"
    )

    custom_preference = []

    if "직접 입력" in preference:
        custom_preference_text = st.text_input(
            "선호하는 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타",
            key="custom_preference_text"
        )

        custom_preference = [
            item.strip()
            for item in custom_preference_text.split(",")
            if item.strip()
        ]

    all_preferences = list(dict.fromkeys(
        [
            item for item in preference
            if item != "직접 입력"
        ] + custom_preference
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
        excluded_options,
        key="excluded_food_select"
    )

    custom_excluded = []

    if "직접 입력" in excluded_foods:
        custom_excluded_text = st.text_input(
            "제외할 음식 직접 입력",
            placeholder="예: 버섯, 고구마, 파스타",
            key="custom_excluded_text"
        )

        custom_excluded = [
            item.strip()
            for item in custom_excluded_text.split(",")
            if item.strip()
        ]

    all_excluded = list(dict.fromkeys(
        [
            item for item in excluded_foods
            if item != "직접 입력"
        ] + custom_excluded
    ))

    st.caption(
        "여러 음식은 쉼표로 구분해 입력해 주세요. "
        "입력한 단어는 메뉴 이름과 음식 분류를 기준으로 확인해요."
    )

    st.caption(
        "알레르기가 있다면 메뉴 이름만으로 판단하지 말고 "
        "실제 재료와 제품의 알레르기 표시도 확인해 주세요."
    )


# ==================================================
# 영양 성분 데이터 생성 도우미
# ==================================================

def food_info(
    group,
    style,
    kcal,
    carbs,
    protein,
    fat,
    fiber=0,
    calcium=0,
    iron=0,
    potassium=0,
    sodium=0,
    vitamin_a=0,
    vitamin_c=0,
    vitamin_d=0
):
    return {
        "group": group,
        "style": style,
        "kcal": kcal,
        "carbs": carbs,
        "protein": protein,
        "fat": fat,
        "fiber": fiber,
        "calcium": calcium,
        "iron": iron,
        "potassium": potassium,
        "sodium": sodium,
        "vitamin_a": vitamin_a,
        "vitamin_c": vitamin_c,
        "vitamin_d": vitamin_d
    }


# ==================================================
# 일반 식사 메뉴
# ==================================================
# 아래 수치는 메뉴별 참고용 예시값이다.
# 실제 영양 성분은 재료의 양과 조리법에 따라 달라진다.
# ==================================================

foods = {
    "닭고기 덮밥": food_info(
        "닭고기", "한식", 450, 65, 28, 9,
        4, 45, 2.0, 430, 450, 35, 12, 0.2
    ),

    "두부 비빔밥": food_info(
        "두부", "한식", 430, 68, 18, 10,
        7, 160, 3.0, 620, 500, 180, 18, 0
    ),

    "생선구이 정식": food_info(
        "생선", "한식", 470, 65, 27, 12,
        5, 55, 2.0, 520, 480, 30, 15, 5
    ),

    "소고기 채소볶음 정식": food_info(
        "소고기", "한식", 490, 62, 29, 13,
        5, 60, 3.5, 480, 520, 100, 20, 0.2
    ),

    "돼지고기 채소볶음": food_info(
        "돼지고기", "한식", 480, 60, 25, 15,
        5, 50, 2.5, 450, 550, 90, 18, 0.5
    ),

    "달걀 채소볶음밥": food_info(
        "달걀", "한식", 420, 62, 15, 12,
        4, 65, 2.0, 350, 430, 140, 15, 1.2
    ),

    "닭고기 샐러드": food_info(
        "닭고기", "간편식", 350, 25, 30, 13,
        6, 90, 2.5, 600, 400, 250, 35, 0.2
    ),

    "두부 샐러드": food_info(
        "두부", "간편식", 320, 28, 17, 14,
        7, 180, 3.0, 520, 350, 220, 30, 0
    ),

    "통밀빵과 달걀": food_info(
        "달걀", "간편식", 330, 40, 17, 11,
        5, 100, 2.5, 280, 420, 110, 0, 1.0
    ),

    "오트밀과 우유": food_info(
        "우유", "간편식", 350, 52, 14, 9,
        7, 300, 2.5, 480, 150, 70, 2, 2.5
    ),

    "과일과 요구르트": food_info(
        "과일", "간편식", 200, 35, 7, 4,
        4, 220, 0.5, 350, 90, 30, 35, 0.5
    ),

    "밥과 두부조림": food_info(
        "두부", "한식", 400, 63, 18, 9,
        4, 170, 2.5, 400, 400, 50, 8, 0
    ),

    "고구마와 달걀": food_info(
        "달걀", "다양", 320, 48, 13, 8,
        6, 60, 1.5, 550, 180, 600, 15, 1
    ),

    "생선 샐러드": food_info(
        "생선", "간편식", 360, 25, 27, 15,
        6, 100, 2.0, 500, 420, 180, 30, 5
    ),

    "채소 비빔밥": food_info(
        "채소", "한식", 400, 70, 11, 9,
        8, 100, 3.0, 650, 430, 280, 25, 0
    ),

    "과일 오트밀": food_info(
        "과일", "간편식", 330, 55, 11, 8,
        8, 180, 2.5, 430, 120, 30, 25, 1.5
    ),

    "닭고기 채소볶음": food_info(
        "닭고기", "다양", 430, 45, 32, 12,
        6, 80, 2.5, 520, 420, 180, 35, 0.2
    ),

    "소고기 덮밥": food_info(
        "소고기", "다양", 470, 62, 27, 13,
        4, 45, 3.5, 430, 480, 25, 12, 0.2
    ),

    "돼지고기 덮밥": food_info(
        "돼지고기", "다양", 460, 63, 25, 12,
        4, 40, 2.2, 420, 500, 25, 10, 0.4
    ),

    "두부 채소덮밥": food_info(
        "두부", "다양", 420, 62, 19, 11,
        7, 180, 3.0, 560, 400, 200, 25, 0
    )
}


# ==================================================
# 간식 전용 메뉴
# ==================================================
# 일반 식사와 분리하여 간식에는 과일, 유제품,
# 견과류 등의 메뉴만 추천하도록 한다.
# ==================================================

snacks = {
    "사과": food_info(
        "과일", "간편식", 95, 25, 0.5, 0.3,
        4, 10, 0.2, 195, 2, 5, 8, 0
    ),

    "바나나": food_info(
        "과일", "간편식", 105, 27, 1.3, 0.4,
        3.1, 6, 0.3, 420, 1, 4, 10, 0
    ),

    "제철 과일": food_info(
        "과일", "간편식", 80, 20, 1, 0.3,
        2.5, 15, 0.3, 200, 2, 30, 30, 0
    ),

    "견과류": food_info(
        "견과류", "간편식", 170, 6, 5, 15,
        3, 40, 1.2, 180, 2, 0, 0, 0
    ),

    "플레인 요구르트": food_info(
        "우유", "간편식", 120, 12, 6, 5,
        0, 200, 0.1, 240, 80, 50, 1, 0.5
    ),

    "찐 고구마": food_info(
        "고구마", "간편식", 130, 30, 2, 0.2,
        4, 30, 0.6, 450, 40, 700, 15, 0
    ),

    "치즈": food_info(
        "우유", "간편식", 80, 1, 5, 6,
        0, 150, 0.1, 25, 180, 60, 0, 0.2
    )
}


# ==================================================
# 음식 이름 및 분류 검색
# ==================================================

def matches_food(name, info, terms):
    """메뉴 이름 또는 음식 분류에 검색어가 있는지 확인한다."""

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

def get_food_candidates(style, excluded):
    candidates = []

    for name, info in foods.items():

        if matches_food(name, info, excluded):
            continue

        food_style = info.get("style", "다양")

        if style == "한식 위주":
            if food_style not in ["한식", "다양"]:
                continue

        elif style == "간편식 위주":
            if food_style not in ["간편식", "다양"]:
                continue

        candidates.append(name)

    return candidates


# ==================================================
# 간식 후보 생성
# ==================================================

def get_snack_candidates(excluded):
    return [
        name
        for name, info in snacks.items()
        if not matches_food(name, info, excluded)
    ]


# ==================================================
# 선호 음식에 맞는 메뉴 선택
# ==================================================

def choose_food(
    candidates,
    food_data,
    preferences,
    used_today,
    rng,
    old_food=None
):
    """선호 메뉴를 우선 고려하면서 메뉴를 선택한다."""

    available = [
        name
        for name in candidates
        if name not in used_today
        and name != old_food
    ]

    if not available:
        available = [
            name
            for name in candidates
            if name != old_food
        ]

    if not available:
        available = candidates.copy()

    if not available:
        return None

    preferred = [
        name
        for name in available
        if matches_food(
            name,
            food_data[name],
            preferences
        )
    ]

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
    seed=None
):
    rng = random.Random(seed)

    meal_candidates = get_food_candidates(
        style,
        excluded
    )

    snack_candidates = get_snack_candidates(
        excluded
    )

    if not meal_candidates:
        return None

    if (
        meal_count == "세 끼 + 간식"
        and not snack_candidates
    ):
        return None

    meal_names = ["아침", "점심", "저녁"]

    if meal_count == "세 끼 + 간식":
        meal_names.append("간식")

    plan = []
    recent_meals = []
    recent_snacks = []

    for day in range(1, 31):
        day_plan = {"일차": day}
        used_today = set()

        for meal_name in meal_names:

            if meal_name == "간식":
                candidates = snack_candidates
                food_data = snacks
                recent = recent_snacks
            else:
                candidates = meal_candidates
                food_data = foods
                recent = recent_meals

            # 최근에 먹은 메뉴는 가능한 한 피한다.
            fresh_candidates = [
                name for name in candidates
                if name not in recent[-6:]
                and name not in used_today
            ]

            if not fresh_candidates:
                fresh_candidates = [
                    name for name in candidates
                    if name not in used_today
                ]

            if not fresh_candidates:
                fresh_candidates = candidates.copy()

            chosen = choose_food(
                candidates=fresh_candidates,
                food_data=food_data,
                preferences=preference,
                used_today=used_today,
                rng=rng
            )

            if chosen is None:
                return None

            day_plan[meal_name] = chosen
            used_today.add(chosen)

            recent.append(chosen)

            if len(recent) > 12:
                recent.pop(0)

        plan.append(day_plan)

    return plan


# ==================================================
# 영양소 계산
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

        # 일반 식사와 간식 모두 검색한다.
        info = foods.get(
            food_name,
            snacks.get(food_name, {})
        )

        for key in nutrient_keys:
            totals[key] += float(
                info.get(key, 0)
            )

    return totals


# ==================================================
# 식단 생성 버튼
# ==================================================

st.divider()
st.markdown("### 📅 30일 식단표 만들기")

st.write(
    "선호하는 음식과 제외할 음식, 식사 유형을 반영해 "
    "30일 식단을 구성해요."
)

if st.button(
    "✨ 나만의 한 달 식단 생성하기",
    use_container_width=True
):

    new_plan = generate_monthly_plan(
        style=meal_style,
        preference=all_preferences,
        excluded=all_excluded,
        meal_count=meal_count
    )

    if new_plan is None:
        st.error(
            "현재 설정으로 추천할 수 있는 메뉴가 없어요. "
            "제외할 음식 설정을 확인해 주세요."
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
        "식단과 영양 성분은 참고용 예시이며, "
        "개인에게 필요한 영양량을 자동으로 처방하지는 않아요."
    )

    # --------------------------------------------------
    # CSV 다운로드
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 날짜 선택
    # --------------------------------------------------

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

    meal_names = [
        name for name in selected_meal
        if name != "일차"
    ]

    columns = st.columns(len(meal_names))

    for column, meal_name in zip(columns, meal_names):
        with column:
            st.markdown(
                f"""
                <div class="meal-card">
                    <h4>{meal_name}</h4>
                    <p>{selected_meal[meal_name]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # --------------------------------------------------
    # 선택한 날짜 식단 다시 추천
    # --------------------------------------------------

    st.markdown("### 🔄 오늘의 식단 다시 추천")

    if st.button(
        f"{selected_day}일 차 메뉴 다시 추천하기",
        use_container_width=True
    ):

        settings = st.session_state.get(
            "monthly_plan_settings",
            {}
        )

        style_for_plan = settings.get(
            "style",
            meal_style
        )

        preferences_for_plan = settings.get(
            "preference",
            all_preferences
        )

        excluded_for_plan = settings.get(
            "excluded",
            all_excluded
        )

        meal_candidates = get_food_candidates(
            style_for_plan,
            excluded_for_plan
        )

        snack_candidates = get_snack_candidates(
            excluded_for_plan
        )

        if not meal_candidates:
            st.error(
                "추천할 수 있는 식사 메뉴가 없어요. "
                "제외 조건을 확인해 주세요."
            )

        elif (
            "간식" in meal_names
            and not snack_candidates
        ):
            st.error(
                "추천할 수 있는 간식 메뉴가 없어요. "
                "제외 조건을 확인해 주세요."
            )

        else:
            rng = random.Random()

            new_day_plan = {
                "일차": selected_day
            }

            used_today = set()

            for meal_name in meal_names:

                if meal_name == "간식":
                    candidates = snack_candidates
                    food_data = snacks
                else:
                    candidates = meal_candidates
                    food_data = foods

                new_food = choose_food(
                    candidates=candidates,
                    food_data=food_data,
                    preferences=preferences_for_plan,
                    used_today=used_today,
                    rng=rng,
                    old_food=selected_meal[meal_name]
                )

                if new_food is None:
                    continue

                new_day_plan[meal_name] = new_food
                used_today.add(new_food)

            plan[selected_day - 1] = new_day_plan

            st.session_state["monthly_plan"] = plan

            st.rerun()

    # --------------------------------------------------
    # 전체 식단표
    # --------------------------------------------------

    st.divider()
    st.markdown("### 📋 전체 식단표")

    st.dataframe(
        pd.DataFrame(
            st.session_state["monthly_plan"]
        ),
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # 선택한 날짜의 영양소 분석
    # --------------------------------------------------

    selected_meal = st.session_state[
        "monthly_plan"
    ][selected_day - 1]

    nutrients = calculate_nutrients(
        selected_meal
    )

    st.divider()

    st.markdown(
        f"### 📊 {selected_day}일 차 영양소 분석"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "에너지",
        f"{nutrients['kcal']:,.0f} kcal"
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
    # 탄수화물·단백질·지방 에너지 비율
    # --------------------------------------------------

    st.markdown("#### 🥧 주요 영양소 에너지 비율")

    carb_kcal = nutrients["carbs"] * 4
    protein_kcal = nutrients["protein"] * 4
    fat_kcal = nutrients["fat"] * 9

    macro_total = (
        carb_kcal
        + protein_kcal
        + fat_kcal
    )

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

        fig_macro = px.pie(
            macro_df,
            names="영양소",
            values="에너지량(kcal)",
            hole=0.55
        )

        fig_macro.update_traces(
            texttemplate="%{label}<br>%{percent}",
            textposition="inside"
        )

        fig_macro.update_layout(
            margin=dict(
                t=20,
                b=20,
                l=10,
                r=10
            ),
            legend_title_text="영양소"
        )

        st.plotly_chart(
            fig_macro,
            use_container_width=True
        )

    # --------------------------------------------------
    # 비타민·무기질·식이섬유
    # --------------------------------------------------

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
        "예시 함량": [
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
        nutrient_df,
        hide_index=True,
        use_container_width=True
    )

    # --------------------------------------------------
    # 30일 에너지 추이
    # --------------------------------------------------

    st.divider()
    st.markdown("### 📈 30일 식단 요약")

    daily_rows = []

    for day_plan in st.session_state["monthly_plan"]:

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

    average_energy = daily_df[
        "에너지(kcal)"
    ].mean()

    st.metric(
        "30일 식단의 하루 평균 에너지",
        f"{average_energy:,.0f} kcal"
    )

    st.caption(
        f"하루 에너지 참고값: {daily_energy:,.0f} kcal. "
        "현재 버전은 메뉴를 조합하며 음식의 분량을 자동으로 "
        "조절하지 않으므로 실제 섭취 에너지와 다를 수 있어요."
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

    # --------------------------------------------------
    # 안내
    # --------------------------------------------------

    st.divider()
    st.markdown("### 💡 알아두기")

    st.markdown("""
    - 간식은 과일, 견과류, 요구르트, 고구마, 치즈 등 간식 전용 메뉴에서 선택해요.
    - 선호 음식은 추천 확률에 반영하고, 제외 음식은 메뉴 이름과 분류를 기준으로 걸러내요.
    - 메뉴 이름이나 분류에 나타나지 않은 실제 재료까지 자동으로 확인하는 기능은 아니에요.
    - 영양 성분은 예시값이며, 실제 음식의 중량과 조리 방법에 따라 달라질 수 있어요.
    - 현재 버전은 메뉴를 자동 조합하지만 개인의 필요량에 맞춰 음식의 분량을 자동 조절하지는 않아요.
    """)
