import streamlit as st
import pandas as pd
import plotly.express as px
import random

from supabase import create_client


# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="한 달 맞춤 식단 | NutriDay",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# Supabase 및 로그인 확인
# ==================================================

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


try:
    supabase = get_supabase()
except Exception:
    st.error(
        "Supabase 연결에 실패했어요. "
        "secrets.toml의 설정을 확인해 주세요."
    )
    st.stop()


access_token = st.session_state.get("auth_access_token")
refresh_token = st.session_state.get("auth_refresh_token")
user_email = st.session_state.get("auth_email")

if not access_token or not refresh_token:
    st.warning("로그인이 필요해요.")
    if st.button("로그인 페이지로 이동"):
        st.switch_page("main.py")
    st.stop()

try:
    auth_response = supabase.auth.set_session(
        access_token,
        refresh_token
    )

    auth_session = getattr(auth_response, "session", None)
    auth_user = getattr(auth_response, "user", None)

    if auth_session is None:
        auth_session = getattr(
            getattr(auth_response, "data", None),
            "session",
            None
        )

    if auth_user is None:
        auth_user = getattr(
            getattr(auth_response, "data", None),
            "user",
            None
        )

    if auth_session is None:
        st.session_state.pop("auth_access_token", None)
        st.session_state.pop("auth_refresh_token", None)
        st.session_state.pop("auth_email", None)

        st.warning("로그인 세션이 만료되었어요.")
        if st.button("로그인 페이지로 이동"):
            st.switch_page("main.py")
        st.stop()

    if auth_user is not None:
        user_email = getattr(auth_user, "email", None) or user_email
        st.session_state["auth_email"] = user_email

    new_access_token = getattr(
        auth_session, "access_token", None
    )
    new_refresh_token = getattr(
        auth_session, "refresh_token", None
    )

    if new_access_token:
        st.session_state["auth_access_token"] = new_access_token

    if new_refresh_token:
        st.session_state["auth_refresh_token"] = new_refresh_token

except Exception:
    st.session_state.pop("auth_access_token", None)
    st.session_state.pop("auth_refresh_token", None)
    st.session_state.pop("auth_email", None)

    st.warning("로그인 세션을 확인할 수 없어요.")
    if st.button("로그인 페이지로 이동"):
        st.switch_page("main.py")
    st.stop()


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

    .stApp {
        background-color: #FBF9F1;
        color: #263B32;
    }

    [data-testid="stSidebar"] {
        background-color: #EEF6EF;
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
        color: #263B32;
    }

    div.stButton > button {
        background-color: #4D9274;
        color: white;
        border-radius: 10px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #377D61;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 공통 사이드바
# ==================================================

with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")

    st.divider()

    st.markdown("### 👤 내 계정")
    st.caption(user_email or "로그인 사용자")

    st.divider()

    st.page_link(
        "main.py",
        label="🧪 기초대사량 & 영양 가이드"
    )

    st.page_link(
        "pages/calculate.py",
        label="🥗 한 달 맞춤 식단"
    )

    st.divider()

    if st.button(
        "🚪 로그아웃",
        use_container_width=True,
        key="sidebar_logout"
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        for key in [
            "auth_access_token",
            "auth_refresh_token",
            "auth_email",
            "is_logged_in"
        ]:
            st.session_state.pop(key, None)

        st.rerun()


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

energy_from_previous_page = daily_energy is not None

if daily_energy is None:
    daily_energy = 2000.0

st.markdown("### 🔥 나의 하루 에너지")

if energy_from_previous_page:
    st.success(
        f"이전 페이지에서 계산한 값: {daily_energy:,.0f} kcal"
    )
else:
    st.info(
        "이전 페이지의 계산값을 찾지 못해 "
        "2,000 kcal를 예시값으로 사용하고 있어요."
    )

    daily_energy = float(
        st.number_input(
            "하루 에너지 참고값 (kcal)",
            min_value=500,
            max_value=6000,
            value=2000,
            step=100
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
        ["하루 세 끼", "세 끼 + 간식"],
        horizontal=True
    )

with col2:
    preference = st.multiselect(
        "선호하는 음식",
        [
            "닭고기", "생선", "달걀", "두부",
            "소고기", "돼지고기", "채소", "과일"
        ],
        default=["닭고기", "달걀", "채소"]
    )

    excluded_foods = st.multiselect(
        "식단에서 제외할 음식",
        [
            "닭고기", "생선", "달걀", "두부",
            "소고기", "돼지고기", "우유", "견과류"
        ]
    )

    custom_excluded = st.text_input(
        "추가로 제외할 음식 (쉼표로 구분)",
        placeholder="예: 버섯, 새우"
    )

    custom_preferences = st.text_input(
        "추가로 선호하는 음식 (쉼표로 구분)",
        placeholder="예: 브로콜리, 고구마"
    )

    excluded_foods += [
        item.strip()
        for item in custom_excluded.split(",")
        if item.strip()
    ]

    preference += [
        item.strip()
        for item in custom_preferences.split(",")
        if item.strip()
    ]

    st.caption(
        "알레르기가 있다면 해당 식품을 제외하고, "
        "교차접촉 위험도 별도로 확인해 주세요."
    )


# ==================================================
# 음식 영양 데이터
# 1회 분량 기준 예시값
# ==================================================

def food_info(
    group, style, kcal, carbs, protein, fat,
    fiber=0, calcium=0, iron=0, potassium=0,
    sodium=0, vitamin_a=0, vitamin_c=0, vitamin_d=0
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


foods = {
    "닭고기 덮밥": food_info(
        "닭고기", "한식", 450, 65, 28, 9,
        4, 45, 2, 430, 450, 35, 12, 0.2
    ),
    "두부 비빔밥": food_info(
        "두부", "한식", 430, 68, 18, 10,
        7, 160, 3, 620, 500, 180, 18, 0
    ),
    "생선구이 정식": food_info(
        "생선", "한식", 470, 65, 27, 12,
        5, 55, 2, 520, 480, 30, 15, 5
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
        4, 65, 2, 350, 430, 140, 15, 1.2
    ),
    "닭고기 샐러드": food_info(
        "닭고기", "간편식", 350, 25, 30, 13,
        6, 90, 2.5, 600, 400, 250, 35, 0.2
    ),
    "두부 샐러드": food_info(
        "두부", "간편식", 320, 28, 17, 14,
        7, 180, 3, 520, 350, 220, 30, 0
    ),
    "통밀빵과 달걀": food_info(
        "달걀", "간편식", 330, 40, 17, 11,
        5, 100, 2.5, 280, 420, 110, 0, 1
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
        6, 100, 2, 500, 420, 180, 30, 5
    ),
    "채소 비빔밥": food_info(
        "채소", "한식", 400, 70, 11, 9,
        8, 100, 3, 650, 430, 280, 25, 0
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
        7, 180, 3, 560, 400, 200, 25, 0
    )
}


# ==================================================
# 간식 데이터
# ==================================================

snacks = {
    "사과": food_info(
        "과일", "간식", 95, 25, 0.5, 0.3,
        4.4, 11, 0.2, 195, 2, 5, 8, 0
    ),
    "바나나": food_info(
        "과일", "간식", 105, 27, 1.3, 0.4,
        3.1, 6, 0.3, 422, 1, 3, 10, 0
    ),
    "제철 과일": food_info(
        "과일", "간식", 80, 20, 1, 0.3,
        3, 15, 0.3, 200, 2, 30, 25, 0
    ),
    "견과류": food_info(
        "견과류", "간식", 170, 6, 5, 15,
        3, 40, 1.2, 200, 2, 0, 1, 0
    ),
    "플레인 요구르트": food_info(
        "우유", "간식", 100, 12, 6, 3,
        0, 200, 0.1, 240, 70, 30, 1, 0.5
    ),
    "찐 고구마": food_info(
        "고구마", "간식", 130, 30, 2, 0.2,
        4, 30, 0.6, 450, 20, 700, 15, 0
    ),
    "치즈": food_info(
        "우유", "간식", 110, 1, 7, 9,
        0, 200, 0.2, 30, 180, 80, 0, 0.5
    )
}


# ==================================================
# 음식 후보
# ==================================================

def matches_excluded(name, info, excluded):
    searchable = f"{name} {info['group']}".lower()

    return any(
        term.lower() in searchable
        for term in excluded
        if term.strip()
    )


def get_food_candidates(style, excluded):
    candidates = []

    for name, info in foods.items():
        if matches_excluded(name, info, excluded):
            continue

        if style == "한식 위주":
            if info["style"] not in ["한식", "다양"]:
                continue

        elif style == "간편식 위주":
            if info["style"] not in ["간편식", "다양"]:
                continue

        candidates.append(name)

    return candidates


def get_snack_candidates(excluded):
    return [
        name for name, info in snacks.items()
        if not matches_excluded(name, info, excluded)
    ]


def choose_food(candidates, preference, used_today, recent, rng):
    if not candidates:
        return None

    available = [
        name for name in candidates
        if name not in used_today and name not in recent[-6:]
    ]

    if not available:
        available = [
            name for name in candidates
            if name not in used_today
        ]

    if not available:
        available = candidates[:]

    preferred = [
        name for name in available
        if foods[name]["group"] in preference
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

    candidates = get_food_candidates(style, excluded)
    snack_candidates = get_snack_candidates(excluded)

    if not candidates:
        return None

    plan = []
    recent_meals = []

    for day in range(1, 31):
        day_plan = {"일차": day}
        used_today = set()

        for meal_name in ["아침", "점심", "저녁"]:
            chosen = choose_food(
                candidates,
                preference,
                used_today,
                recent_meals,
                rng
            )

            if chosen is None:
                return None

            day_plan[meal_name] = chosen
            used_today.add(chosen)
            recent_meals.append(chosen)

        if meal_count == "세 끼 + 간식":
            available_snacks = [
                name for name in snack_candidates
                if not matches_excluded(
                    name, snacks[name], excluded
                )
            ]

            if available_snacks:
                day_plan["간식"] = rng.choice(available_snacks)

        recent_meals = recent_meals[-12:]
        plan.append(day_plan)

    return plan


# ==================================================
# 영양소 계산
# ==================================================

def calculate_nutrients(meal):
    nutrient_keys = [
        "kcal", "carbs", "protein", "fat", "fiber",
        "calcium", "iron", "potassium", "sodium",
        "vitamin_a", "vitamin_c", "vitamin_d"
    ]

    total = {key: 0.0 for key in nutrient_keys}

    for meal_name, food_name in meal.items():
        if meal_name == "일차":
            continue

        info = foods.get(food_name)

        if info is None:
            info = snacks.get(food_name)

        if info is None:
            continue

        for nutrient in nutrient_keys:
            total[nutrient] += info[nutrient]

    return total


# ==================================================
# 식단 생성
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
        meal_count=meal_count
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
        st.session_state.pop("selected_day", None)

        st.success("30일 식단표를 생성했어요!")


# ==================================================
# 생성된 식단 표시
# ==================================================

if "monthly_plan" in st.session_state:
    plan = st.session_state["monthly_plan"]
    settings = st.session_state.get(
        "monthly_plan_settings", {}
    )

    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    st.caption(
        "식단은 입력 조건에 맞춰 자동으로 구성한 예시예요. "
        "실제 영양 성분을 검증한 전문 식단 처방은 아니에요."
    )

    # CSV 다운로드
    plan_df = pd.DataFrame(plan)

    st.download_button(
        label="📥 한 달 식단표 CSV 다운로드",
        data=plan_df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="NutriDay_30day_meal_plan.csv",
        mime="text/csv",
        use_container_width=True
    )

    # 날짜 선택
    selected_day = st.selectbox(
        "자세히 확인할 날짜",
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

    meal_columns = st.columns(len(meal_names))

    for idx, meal_name in enumerate(meal_names):
        with meal_columns[idx]:
            st.markdown(
                f'<div class="meal-card">'
                f'<b>{meal_name}</b><br>'
                f'{selected_meal[meal_name]}'
                f'</div>',
                unsafe_allow_html=True
            )

    # 특정 날짜 다시 추천
    if st.button(
        f"🔄 {selected_day}일 차 식단 다시 추천",
        use_container_width=True
    ):
        candidates = get_food_candidates(
            settings.get("style", meal_style),
            settings.get("excluded", excluded_foods)
        )

        snack_candidates = get_snack_candidates(
            settings.get("excluded", excluded_foods)
        )

        if not candidates:
            st.error("추천 가능한 음식이 없어요.")
        else:
            updated_meal = dict(selected_meal)

            for meal_name in meal_names:
                if meal_name == "간식":
                    available = [
                        item for item in snack_candidates
                        if item != updated_meal[meal_name]
                    ]

                    if available:
                        updated_meal[meal_name] = random.choice(
                            available
                        )
                else:
                    available = [
                        item for item in candidates
                        if item != updated_meal[meal_name]
                    ]

                    if not available:
                        available = candidates

                    updated_meal[meal_name] = random.choice(
                        available
                    )

            st.session_state["monthly_plan"][
                selected_day - 1
            ] = updated_meal

            st.rerun()

    # 전체 식단표
    st.markdown("#### 📋 전체 식단표")

    st.dataframe(
        pd.DataFrame(plan),
        hide_index=True,
        use_container_width=True
    )

    # ==================================================
    # 선택한 날짜 영양소 분석
    # ==================================================

    nutrients = calculate_nutrients(selected_meal)

    st.divider()
    st.markdown(f"### 📊 {selected_day}일 차 영양소 분석")

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

    # 탄단지 에너지 비율
    carb_kcal = nutrients["carbs"] * 4
    protein_kcal = nutrients["protein"] * 4
    fat_kcal = nutrients["fat"] * 9

    macro_total = carb_kcal + protein_kcal + fat_kcal

    st.markdown("#### 🥧 탄수화물·단백질·지방 에너지 비율")

    if macro_total > 0:
        macro_df = pd.DataFrame({
            "영양소": ["탄수화물", "단백질", "지방"],
            "에너지량(kcal)": [
                carb_kcal, protein_kcal, fat_kcal
            ]
        })

        macro_df["비율(%)"] = (
            macro_df["에너지량(kcal)"] / macro_total * 100
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

    # 비타민·무기질·식이섬유
    st.markdown("#### 🧬 비타민·무기질·식이섬유")

    nutrient_df = pd.DataFrame({
        "영양소": [
            "식이섬유", "칼슘", "철", "칼륨",
            "나트륨", "비타민 A", "비타민 C", "비타민 D"
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
        "음식별 영양 성분은 예시값이며, "
        "실제 음식의 영양 성분과 다를 수 있어요."
    )

    # ==================================================
    # 30일 식단 요약
    # ==================================================

    st.divider()
    st.markdown("### 📈 30일 식단 요약")

    daily_rows = []

    for day_plan in plan:
        day_nutrients = calculate_nutrients(day_plan)

        daily_rows.append({
            "일차": day_plan["일차"],
            "에너지(kcal)": day_nutrients["kcal"],
            "탄수화물(g)": day_nutrients["carbs"],
            "단백질(g)": day_nutrients["protein"],
            "지방(g)": day_nutrients["fat"],
            "식이섬유(g)": day_nutrients["fiber"]
        })

    daily_df = pd.DataFrame(daily_rows)

    avg_energy = daily_df["에너지(kcal)"].mean()

    st.metric(
        "30일 식단의 하루 평균 에너지",
        f"{avg_energy:,.0f} kcal"
    )

    st.caption(
        f"하루 에너지 참고값: {daily_energy:,.0f} kcal. "
        "현재 메뉴 조합은 참고 에너지에 맞춰 분량을 "
        "자동 조정하지 않아요."
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

    # ==================================================
    # 안내
    # ==================================================

    st.divider()
    st.markdown("### 💡 알아두기")

    st.markdown("""
    - 식단은 입력한 선호도와 제외 조건을 반영해 구성한 예시예요.
    - 현재 버전은 메뉴를 자동 조합하지만, 목표 에너지에 맞춰
      음식의 분량을 최적화하지는 않아요.
    - 영양 성분은 예시 데이터이므로 실제 음식의 중량과
      조리법에 따라 달라질 수 있어요.
    - 비타민과 무기질은 에너지를 직접 제공하지 않으므로
      탄수화물·단백질·지방의 에너지 비율과 별도로 표시해요.
    - 개인에게 적합한 식단은 성장 상태, 건강 상태,
      활동량 등 다양한 요인에 따라 달라질 수 있어요.
    """)
