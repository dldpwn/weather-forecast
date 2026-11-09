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
        min-height: 150px;
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
    "하루 에너지와 음식 선호, 영양소 구성을 고려해 식단을 추천해요."
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

NUTRIENT_KEYS = list(NUTRIENT_COLUMNS.keys())


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


def get_basis_amount(value):
    """
    영양성분 기준량에서 숫자를 추출한다.
    예: 100g -> 100, 150ml -> 150
    """
    text = str(value).replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", text)

    if match:
        amount = float(match.group(1))

        if amount > 0:
            return amount

    return 100.0


def get_basis_unit(value):
    text = str(value).lower()

    if "ml" in text:
        return "ml"

    return "g"


# ==================================================
# 식품 분류
# ==================================================
SNACK_GROUPS = [
    "과일",
    "유제품",
    "견과류",
]

SNACK_KEYWORDS = [
    "과일", "사과", "바나나", "딸기",
    "포도", "귤", "오렌지", "배",
    "키위", "복숭아", "수박", "블루베리",
    "요거트", "요구르트", "우유",
    "견과", "아몬드", "호두", "땅콩",
]


def classify_food(name):
    """식품명에 포함된 단어를 기준으로 식품 분류를 추정한다."""
    name = str(name).casefold()

    if any(x in name for x in ["닭", "치킨"]):
        return "닭고기"

    if any(x in name for x in [
        "고등어", "연어", "참치", "갈치",
        "명태", "생선", "새우", "오징어",
        "조기", "꽁치", "삼치",
    ]):
        return "생선"

    if any(x in name for x in ["달걀", "계란"]):
        return "달걀"

    if "두부" in name:
        return "두부"

    if any(x in name for x in ["소고기", "쇠고기"]):
        return "소고기"

    if any(x in name for x in ["돼지고기", "돈육"]):
        return "돼지고기"

    if any(x in name for x in [
        "우유", "요거트", "요구르트", "치즈"
    ]):
        return "유제품"

    if any(x in name for x in [
        "사과", "바나나", "딸기", "포도",
        "귤", "오렌지", "배", "과일",
        "키위", "복숭아", "수박", "블루베리",
    ]):
        return "과일"

    if any(x in name for x in [
        "견과", "아몬드", "호두", "땅콩"
    ]):
        return "견과류"

    if any(x in name for x in [
        "채소", "나물", "샐러드", "시금치",
        "브로콜리", "당근", "양배추", "김치",
        "오이", "상추", "콩나물", "무침",
    ]):
        return "채소"

    return "기타"


def classify_style(name):
    """식품명에 따라 식사 유형을 대략적으로 분류한다."""
    name = str(name)

    korean_keywords = [
        "밥", "국", "찌개", "구이", "볶음",
        "조림", "비빔밥", "죽", "나물",
        "전골", "찜", "반찬",
    ]

    simple_keywords = [
        "샐러드", "샌드위치", "오트밀",
        "빵", "요거트", "요구르트",
        "시리얼", "토스트",
    ]

    if any(x in name for x in korean_keywords):
        return "한식"

    if any(x in name for x in simple_keywords):
        return "간편식"

    return "다양"


def classify_meal_role(name, info):
    """
    식품명과 식품군을 바탕으로 한 끼에서 맡는 역할을 분류한다.
    일반 식사는 주식·단백질 반찬·채소 반찬·국물로 구성하고,
    간식은 과일·견과류·간단한 유제품으로 제한한다.
    """
    name = str(name).casefold()
    group = info.get("group", "")

    # 간식: 유제품 전체가 아니라 간식으로 먹기 쉬운 품목만 분류
    snack_keywords = [
        "사과", "바나나", "딸기", "포도", "귤", "오렌지", "배",
        "키위", "복숭아", "수박", "블루베리", "과일",
        "아몬드", "호두", "땅콩", "견과",
        "요거트", "요구르트", "요구르트", "플레인요구르트",
        "우유", "두유",
    ]
    if group in ["과일", "견과류"] or any(word in name for word in snack_keywords):
        return "간식"

    # 한 가지 음식만으로 한 끼가 되는 메뉴는 밥·반찬과 구분
    complete_keywords = [
        "비빔밥", "볶음밥", "덮밥", "김밥", "카레", "파스타",
        "샌드위치", "햄버거", "도시락", "주먹밥",
    ]
    if any(word in name for word in complete_keywords):
        return "완성식"

    # 주식: 밥·빵·면처럼 한 끼의 중심이 되는 음식
    staple_keywords = [
        "쌀밥", "현미밥", "잡곡밥", "보리밥", "흰밥",
        "찹쌀밥", "콩밥", "밥", "죽", "오트밀",
        "식빵", "토스트", "빵", "국수", "냉면", "칼국수",
    ]
    if any(word in name for word in staple_keywords):
        return "주식"

    # 단백질 반찬
    protein_keywords = [
        "닭", "치킨", "소고기", "쇠고기", "돼지고기", "돈육",
        "불고기", "제육", "장조림", "갈비", "생선", "고등어",
        "연어", "참치", "갈치", "새우", "오징어", "조기",
        "꽁치", "삼치", "멸치", "어묵", "달걀", "계란",
        "두부", "콩자반", "콩조림",
    ]
    if (
        group in ["닭고기", "생선", "달걀", "두부", "소고기", "돼지고기"]
        or any(word in name for word in protein_keywords)
    ):
        return "단백질 반찬"

    # 국·찌개·탕
    soup_keywords = ["국", "찌개", "탕", "전골", "수프", "스프"]
    if any(word in name for word in soup_keywords):
        return "국물"

    # 채소 반찬
    vegetable_keywords = [
        "나물", "샐러드", "시금치", "브로콜리", "당근", "양배추",
        "김치", "오이", "상추", "콩나물", "무침", "채소",
        "버섯", "애호박", "호박", "가지", "무생채", "깻잎",
        "감자볶음", "감자조림", "고구마줄기",
    ]
    if group == "채소" or any(word in name for word in vegetable_keywords):
        return "채소 반찬"

    return "기타"


# ==================================================
# foods 딕셔너리 생성
# ==================================================
foods = {}

for _, row in food_db.iterrows():
    name = str(row.get("식품명", "")).strip()

    if not name or name.lower() == "nan":
        continue

    basis_text = row.get("영양성분함량기준량", "100g")

    info = {
        "group": classify_food(name),
        "style": classify_style(name),
        "role": "",
        "unit": get_basis_unit(basis_text),
        "basis": str(basis_text),
        "basis_amount": get_basis_amount(basis_text),
    }

    for key, column in NUTRIENT_COLUMNS.items():
        info[key] = safe_number(row.get(column, 0))

    info["role"] = classify_meal_role(name, info)

    foods[name] = info


if not foods:
    st.error("사용할 수 있는 식품 데이터가 없어요.")
    st.stop()


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
# 간식 후보 생성
# ==================================================
def is_snack(name, info):
    return info.get("role") == "간식"


# ==================================================
# 식사 유형 필터
# ==================================================
def matches_style(info, style):
    if style == "다양하게 구성":
        return True

    if style == "한식 위주":
        return info.get("style") in ["한식", "다양"]

    if style == "간편식 위주":
        return info.get("style") in ["간편식", "다양"]

    return True


# ==================================================
# 음식 후보 생성
# ==================================================
def get_candidates(style, excluded, role=None):
    candidates = []

    for name, info in foods.items():

        if matches_food(name, info, excluded):
            continue

        if not matches_style(info, style):
            continue

        if role is not None and info.get("role") != role:
            continue

        candidates.append(name)

    return candidates


# ==================================================
# 영양소 기반 음식 점수
# ==================================================
def nutrient_score(name, goal, used_groups):
    """
    식단 목표에 따라 음식 선택 점수를 다르게 계산한다.
    점수는 데이터베이스에 등록된 영양성분을 활용한
    상대적인 선택 기준이며, 의학적 평가 점수는 아니다.
    """
    info = foods[name]

    score = 0.0

    protein = info.get("protein", 0)
    fiber = info.get("fiber", 0)
    calcium = info.get("calcium", 0)
    iron = info.get("iron", 0)
    potassium = info.get("potassium", 0)
    vitamin_a = info.get("vitamin_a", 0)
    vitamin_c = info.get("vitamin_c", 0)
    vitamin_d = info.get("vitamin_d", 0)
    carbs = info.get("carbs", 0)
    kcal = info.get("kcal", 0)

    if goal == "균형 잡힌 식사":
        score += min(protein, 20) * 0.25
        score += min(fiber, 8) * 0.5
        score += min(calcium, 300) * 0.01
        score += min(iron, 5) * 0.2
        score += min(vitamin_a, 300) * 0.005
        score += min(vitamin_c, 30) * 0.05

    elif goal == "활동량을 고려한 식사":
        score += min(carbs, 60) * 0.08
        score += min(protein, 25) * 0.35
        score += min(kcal, 300) * 0.015

    elif goal == "다양한 영양소 섭취":
        score += min(fiber, 8) * 0.4
        score += min(calcium, 300) * 0.01
        score += min(iron, 5) * 0.2
        score += min(potassium, 400) * 0.01
        score += min(vitamin_a, 300) * 0.005
        score += min(vitamin_c, 30) * 0.05
        score += min(vitamin_d, 5) * 0.1

    # 이미 선택한 식품군과 다른 식품군에 추가 점수
    if info.get("group") not in used_groups:
        score += 1.5

    return score


# ==================================================
# 음식 선택
# ==================================================
def choose_food(
    candidates,
    preference,
    recent_foods,
    used_groups,
    goal,
    rng,
):
    if not candidates:
        return None

    recent_set = set(recent_foods[-8:])

    available = [
        name for name in candidates
        if name not in recent_set
    ]

    if not available:
        available = candidates.copy()

    scored = []

    for name in available:
        score = nutrient_score(
            name=name,
            goal=goal,
            used_groups=used_groups,
        )

        # 선호 음식에 가중치 부여
        if matches_food(name, foods[name], preference):
            score += 3.0

        # 무작위 요소를 조금 넣어 매번 같은 메뉴가 나오지 않도록 함
        score += rng.uniform(0, 2)

        scored.append((score, name))

    scored.sort(reverse=True)

    # 상위 후보 중 무작위로 선택
    top_candidates = scored[:min(5, len(scored))]

    if not top_candidates:
        return None

    return rng.choice(top_candidates)[1]


# ==================================================
# 음식별 기본 섭취량
# ==================================================
def get_standard_amount(role):
    """한 끼 구성 요소별 기본 섭취량."""
    portions = {
        "주식": 150,
        "단백질 반찬": 80,
        "채소 반찬": 60,
        "국물": 150,
        "완성식": 250,
        "기타": 0,
        "간식": 100,
    }
    return portions.get(role, 100)


# ==================================================
# 영양성분 계산
# ==================================================
def calculate_food_nutrition(food_name, amount):
    """기준량에 맞춰 실제 섭취량의 영양성분을 환산한다."""
    info = foods[food_name]

    basis_amount = info.get("basis_amount", 100)

    if basis_amount <= 0:
        basis_amount = 100

    ratio = amount / basis_amount

    return {
        nutrient: info.get(nutrient, 0) * ratio
        for nutrient in NUTRIENT_KEYS
    }


def calculate_meal_energy(meal_items):
    total = 0.0

    for item in meal_items:
        nutrition = calculate_food_nutrition(
            item["음식"],
            item["섭취량"],
        )
        total += nutrition["kcal"]

    return total


# ==================================================
# 한 끼 구성
# ==================================================
def build_meal(
    meal_name,
    target_energy,
    style,
    preference,
    excluded,
    recent_foods,
    goal,
    rng,
):
    """
    일반적인 한 끼를 밥(주식) + 단백질 반찬 + 채소 반찬 1~2개로 구성한다.
    국이나 찌개가 데이터베이스에 있으면 추가한다.
    반찬만으로 한 끼가 만들어지는 것을 막기 위해 주식이 없으면
    완성식 후보를 확인하고, 적절한 후보가 없으면 생성 실패로 처리한다.
    """
    meal_items = []
    used_groups = set()

    def add_role(role, count=1, required=False):
        candidates = get_candidates(
            style=style,
            excluded=excluded,
            role=role,
        )
        added = 0

        for _ in range(count):
            chosen = choose_food(
                candidates=candidates,
                preference=preference,
                recent_foods=recent_foods,
                used_groups=used_groups,
                goal=goal,
                rng=rng,
            )
            if not chosen:
                continue

            info = foods[chosen]
            meal_items.append({
                "음식": chosen,
                "역할": role,
                "섭취량": get_standard_amount(role),
                "단위": info["unit"],
            })
            used_groups.add(info["group"])
            recent_foods.append(chosen)
            candidates = [food for food in candidates if food != chosen]
            added += 1

        return added

    # 밥이나 빵 등 주식은 반드시 포함
    staple_count = add_role("주식", count=1, required=True)

    if staple_count == 0:
        # 데이터에 주식 후보가 없는 경우에만 한 그릇 완성 메뉴로 대체
        complete_candidates = get_candidates(
            style=style,
            excluded=excluded,
            role="완성식",
        )
        chosen = choose_food(
            candidates=complete_candidates,
            preference=preference,
            recent_foods=recent_foods,
            used_groups=used_groups,
            goal=goal,
            rng=rng,
        )
        if chosen:
            info = foods[chosen]
            meal_items.append({
                "음식": chosen,
                "역할": "완성식",
                "섭취량": get_standard_amount("완성식"),
                "단위": info["unit"],
            })
            recent_foods.append(chosen)
        else:
            return None

    else:
        # 단백질 반찬 1종은 기본으로 구성
        protein_count = add_role("단백질 반찬", count=1)
        if protein_count == 0:
            return None

        # 채소 반찬은 가능하면 서로 다른 종류로 2종 구성
        vegetable_count = add_role("채소 반찬", count=2)
        if vegetable_count == 0:
            return None

        # 국이나 찌개는 데이터에 후보가 있을 때 선택적으로 추가
        add_role("국물", count=1)

    if not meal_items:
        return None

    # 목표 열량에 맞춰 음식별 섭취량을 함께 조정
    base_energy = calculate_meal_energy(meal_items)

    if base_energy > 0 and target_energy > 0:
        adjustment = target_energy / base_energy
        adjustment = max(0.75, min(adjustment, 1.35))

        for item in meal_items:
            item["섭취량"] = round(
                item["섭취량"] * adjustment / 10
            ) * 10
            item["섭취량"] = max(20, item["섭취량"])

    return meal_items


# ==================================================
# 간식 구성
# ==================================================
def build_snack(
    target_energy,
    preference,
    excluded,
    recent_foods,
    goal,
    rng,
):
    """간식은 과일·견과류·우유·요거트 등 간단한 음식 한 가지로 구성한다."""
    candidates = get_candidates(
        style="다양하게 구성",
        excluded=excluded,
        role="간식",
    )

    chosen = choose_food(
        candidates=candidates,
        preference=preference,
        recent_foods=recent_foods,
        used_groups=set(),
        goal=goal,
        rng=rng,
    )

    if not chosen:
        return None

    info = foods[chosen]
    amount = get_standard_amount("간식")

    base_energy = calculate_food_nutrition(chosen, amount)["kcal"]

    if base_energy > 0 and target_energy > 0:
        adjustment = target_energy / base_energy
        adjustment = max(0.75, min(adjustment, 1.25))
        amount = round(amount * adjustment / 10) * 10
        amount = max(20, amount)

    recent_foods.append(chosen)

    return [{
        "음식": chosen,
        "역할": "간식",
        "섭취량": amount,
        "단위": info["unit"],
    }]



# ==================================================
# 하루 식단 생성
# ==================================================
def generate_daily_plan(
    day,
    daily_energy,
    style,
    preference,
    excluded,
    meal_count,
    goal,
    seed=None,
    recent_foods=None,
):
    rng = random.Random(seed)

    if recent_foods is None:
        recent_foods = []

    day_plan = {
        "일차": day,
    }

    # 끼니별 에너지 배분
    if meal_count == "세 끼 + 간식":
        energy_ratio = {
            "아침": 0.25,
            "점심": 0.35,
            "저녁": 0.30,
            "간식": 0.10,
        }
    else:
        energy_ratio = {
            "아침": 0.30,
            "점심": 0.40,
            "저녁": 0.30,
        }

    for meal_name, ratio in energy_ratio.items():
        target_energy = daily_energy * ratio

        if meal_name == "간식":
            meal_items = build_snack(
                target_energy=target_energy,
                preference=preference,
                excluded=excluded,
                recent_foods=recent_foods,
                goal=goal,
                rng=rng,
            )
        else:
            meal_items = build_meal(
                meal_name=meal_name,
                target_energy=target_energy,
                style=style,
                preference=preference,
                excluded=excluded,
                recent_foods=recent_foods,
                goal=goal,
                rng=rng,
            )

        if not meal_items:
            return None, meal_name

        day_plan[meal_name] = meal_items

    return day_plan, None


# ==================================================
# 30일 식단 생성
# ==================================================
def generate_monthly_plan(
    daily_energy,
    style,
    preference,
    excluded,
    meal_count,
    goal,
    seed=None,
):
    rng = random.Random(seed)

    plan = []
    recent_foods = []

    for day in range(1, 31):
        day_plan, failed_meal = generate_daily_plan(
            day=day,
            daily_energy=daily_energy,
            style=style,
            preference=preference,
            excluded=excluded,
            meal_count=meal_count,
            goal=goal,
            seed=rng.randint(0, 999999),
            recent_foods=recent_foods,
        )

        if day_plan is None:
            return None, failed_meal

        plan.append(day_plan)

    return plan, None


# ==================================================
# 하루 영양소 합계
# ==================================================
def calculate_daily_nutrition(day_plan):
    totals = {
        nutrient: 0.0
        for nutrient in NUTRIENT_KEYS
    }

    meal_nutrition = {}

    for meal_name, meal_items in day_plan.items():
        if meal_name == "일차":
            continue

        meal_total = {
            nutrient: 0.0
            for nutrient in NUTRIENT_KEYS
        }

        for item in meal_items:
            nutrition = calculate_food_nutrition(
                item["음식"],
                item["섭취량"],
            )

            for nutrient in NUTRIENT_KEYS:
                meal_total[nutrient] += nutrition[nutrient]
                totals[nutrient] += nutrition[nutrient]

        meal_nutrition[meal_name] = meal_total

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


# ==================================================
# 식단 표시용 문자열
# ==================================================
def format_meal_items(meal_items):
    result = []

    for item in meal_items:
        result.append(
            f"{item['음식']} ({item['섭취량']:,.0f}{item['단위']})"
        )

    return ", ".join(result)


# ==================================================
# 식단 생성 버튼
# ==================================================
st.divider()
st.markdown("### 📅 30일 식단표 만들기")

st.write(
    "설정한 식단 목표와 음식 선호, 하루 에너지를 참고해 "
    "30일 식단을 구성해요."
)

if st.button(
    "✨ 나만의 한 달 식단 생성하기",
    use_container_width=True,
):
    new_plan, failed_meal = generate_monthly_plan(
        daily_energy=daily_energy,
        style=meal_style,
        preference=all_preferences,
        excluded=all_excluded,
        meal_count=meal_count,
        goal=goal,
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

    plan = st.session_state["monthly_plan"]

    # 이전 버전의 식단 데이터와 구조가 다르면 새로 생성하도록 안내
    if (
        not plan
        or not isinstance(plan[0].get("아침"), list)
    ):
        st.warning(
            "이전에 생성한 식단 데이터가 있어요. "
            "새로운 식단 생성 버튼을 눌러 다시 만들어 주세요."
        )
        st.stop()

    st.divider()
    st.markdown("### 🗓️ 나의 30일 식단표")

    saved_settings = st.session_state.get(
        "monthly_plan_settings",
        {},
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
            meal_items = selected_meal[meal_name]
            meal_energy = calculate_meal_energy(meal_items)

            food_html = "<br>".join([
                f"{item['음식']} "
                f"<small>({item['섭취량']:,.0f}{item['단위']})</small>"
                for item in meal_items
            ])

            st.markdown(
                f"""
                <div class="meal-card">
                    <b>{meal_name}</b><br><br>
                    {food_html}<br><br>
                    <small>약 {meal_energy:,.0f} kcal</small>
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
            {},
        )

        new_day, failed_meal = generate_daily_plan(
            day=selected_day,
            daily_energy=settings.get("energy", daily_energy),
            style=settings.get("style", meal_style),
            preference=settings.get("preference", all_preferences),
            excluded=settings.get("excluded", all_excluded),
            meal_count=settings.get("meal_count", meal_count),
            goal=settings.get("goal", goal),
            seed=random.randint(0, 999999),
        )

        if new_day is None:
            st.error(
                f"{failed_meal} 메뉴 후보가 부족해요. "
                "설정을 조정해 주세요."
            )
        else:
            plan[selected_day - 1] = new_day
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
            "하루 에너지",
            f"{totals['kcal']:,.0f} kcal",
        )

    with metric2:
        st.metric(
            "탄수화물",
            f"{totals['carbs']:.1f} g",
        )

    with metric3:
        st.metric(
            "단백질",
            f"{totals['protein']:.1f} g",
        )

    with metric4:
        st.metric(
            "지방",
            f"{totals['fat']:.1f} g",
        )

    target_energy = saved_settings.get(
        "energy",
        daily_energy,
    )

    energy_difference = totals["kcal"] - target_energy

    st.markdown("#### 🔥 하루 에너지 목표와 비교")

    energy_col1, energy_col2 = st.columns(2)

    with energy_col1:
        st.metric(
            "하루 에너지 참고값",
            f"{target_energy:,.0f} kcal",
        )

    with energy_col2:
        st.metric(
            "추천 식단 에너지",
            f"{totals['kcal']:,.0f} kcal",
            delta=f"{energy_difference:+,.0f} kcal",
        )

    if target_energy > 0:
        energy_percent = min(
            totals["kcal"] / target_energy * 100,
            100,
        )

        st.progress(energy_percent / 100)

        st.caption(
            f"하루 에너지 참고값의 약 "
            f"{totals['kcal'] / target_energy * 100:.1f}%에 해당해요."
        )

    st.caption(
        "영양성분은 CSV에 등록된 기준량을 실제 설정 섭취량에 맞춰 환산한 값이에요. "
        "식품의 조리법과 실제 섭취량에 따라 달라질 수 있어요."
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
            use_container_width=True,
        )

        st.caption(
            "이 그래프는 탄수화물·단백질·지방에서 얻는 에너지끼리 비교한 비율이에요. "
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
        "함량(mg)": list(mineral_values.values()),
    })

    fig_mineral = px.bar(
        mineral_df,
        x="영양소",
        y="함량(mg)",
        text="함량(mg)",
        title="무기질 함량",
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
        use_container_width=True,
    )

    # --------------------------------------------------
    # 비타민 및 식이섬유
    # --------------------------------------------------
    st.markdown("#### 🍊 비타민 및 식이섬유")

    vitamin_col1, vitamin_col2, vitamin_col3 = st.columns(3)

    with vitamin_col1:
        st.metric(
            "비타민 A",
            f"{totals['vitamin_a']:.1f} μg RAE",
        )

    with vitamin_col2:
        st.metric(
            "비타민 C",
            f"{totals['vitamin_c']:.1f} mg",
        )

    with vitamin_col3:
        st.metric(
            "비타민 D",
            f"{totals['vitamin_d']:.1f} μg",
        )

    st.metric(
        "식이섬유",
        f"{totals['fiber']:.1f} g",
    )

    # --------------------------------------------------
    # 끼니별 에너지
    # --------------------------------------------------
    st.markdown("#### 🍽️ 끼니별 에너지 구성")

    meal_energy_rows = []

    for meal_name, meal_items in selected_meal.items():
        if meal_name == "일차":
            continue

        meal_energy_rows.append({
            "끼니": meal_name,
            "에너지(kcal)": calculate_meal_energy(meal_items),
        })

    meal_energy_df = pd.DataFrame(meal_energy_rows)

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

    st.plotly_chart(
        fig_meal,
        use_container_width=True,
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

    table_rows = []

    for day in plan:
        row = {
            "일차": day["일차"],
        }

        for meal_name, meal_items in day.items():
            if meal_name == "일차":
                continue

            row[meal_name] = format_meal_items(meal_items)

        table_rows.append(row)

    plan_df = pd.DataFrame(table_rows)

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
