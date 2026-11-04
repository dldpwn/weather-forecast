
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import date, timedelta

from food_data import load_food_database

# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="식사 기록 | NutriDay",
    page_icon="🍽️",
    layout="wide"
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
    div[data-baseweb="select"] > div {
        background: white;
        border-radius: 10px;
        border-color: #DCEADF;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        border: 1px solid #DCEADF;
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #DCEADF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 기본 설정
# ==================================================

st.title("🍽️ 식사 기록 & 영양 관리")
st.markdown(
    "매일 먹은 음식을 기록하고 나의 영양 섭취 현황을 관리해 보세요."
)
st.divider()

MEALS = ["아침", "점심", "저녁", "간식"]

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "meal_records.json"
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

    if st.button("로그아웃", key="record_logout", use_container_width=True):
        for key in [
            "auth_access_token",
            "auth_refresh_token",
            "auth_email"
        ]:
            st.session_state.pop(key, None)

        st.rerun()

# ==================================================
# 식품 데이터베이스 불러오기
# ==================================================

@st.cache_data
def get_food_database():
    return load_food_database()

try:
    food_db = get_food_database()

    if food_db is None or food_db.empty:
        st.error("식품영양성분 데이터베이스를 불러오지 못했습니다.")
        st.stop()

except Exception as e:
    st.error(f"식품 데이터베이스 오류: {e}")
    st.stop()

REQUIRED_COLUMNS = [
    "식품명",
    "영양성분함량기준량",
    "에너지(kcal)",
    "탄수화물(g)",
    "단백질(g)",
    "지방(g)"
]

missing_columns = [
    col for col in REQUIRED_COLUMNS
    if col not in food_db.columns
]

if missing_columns:
    st.error(
        "CSV에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()

# ==================================================
# 영양소 항목
# ==================================================

NUTRIENT_COLUMNS = {
    "열량(kcal)": "에너지(kcal)",
    "탄수화물(g)": "탄수화물(g)",
    "단백질(g)": "단백질(g)",
    "지방(g)": "지방(g)",
    "당류(g)": "당류(g)",
    "식이섬유(g)": "식이섬유(g)",
    "칼슘(mg)": "칼슘(mg)",
    "철(mg)": "철(mg)",
    "인(mg)": "인(mg)",
    "칼륨(mg)": "칼륨(mg)",
    "나트륨(mg)": "나트륨(mg)",
    "비타민 A(μg RAE)": "비타민 A(μg RAE)",
    "티아민(mg)": "티아민(mg)",
    "리보플라빈(mg)": "리보플라빈(mg)",
    "니아신(mg)": "니아신(mg)",
    "비타민 C(mg)": "비타민 C(mg)",
    "비타민 D(μg)": "비타민 D(μg)",
    "콜레스테롤(mg)": "콜레스테롤(mg)",
    "포화지방산(g)": "포화지방산(g)",
    "트랜스지방산(g)": "트랜스지방산(g)"
}

# 숫자로 변환
def to_number(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


# ==================================================
# 식품 데이터 정리
# ==================================================

food_db = food_db.copy()

food_db["식품명"] = (
    food_db["식품명"]
    .astype(str)
    .str.strip()
)

food_db = food_db[
    food_db["식품명"].ne("")
    & food_db["식품명"].ne("nan")
].copy()

for column in NUTRIENT_COLUMNS.values():
    if column in food_db.columns:
        food_db[column] = food_db[column].apply(to_number)
    else:
        food_db[column] = 0.0

# 기준량에서 숫자 추출
def get_basis(row):
    raw = str(row.get("영양성분함량기준량", "100g")).lower()

    digits = "".join(
        ch for ch in raw
        if ch.isdigit() or ch == "."
    )

    basis = to_number(digits)

    if basis <= 0:
        basis = 100.0

    unit = "ml" if "ml" in raw else "g"

    return basis, unit


food_db[["_기준량", "_단위"]] = food_db.apply(
    lambda row: pd.Series(get_basis(row)),
    axis=1
)

# 같은 음식명이 여러 개면 첫 번째 항목을 기본 선택
food_db = food_db.drop_duplicates(
    subset=["식품명"],
    keep="first"
)

food_names = sorted(food_db["식품명"].unique().tolist())

food_lookup = {
    row["식품명"]: row
    for _, row in food_db.iterrows()
}

# ==================================================
# 영양소 계산 함수
# ==================================================

NUTRIENT_KEYS = list(NUTRIENT_COLUMNS.keys())


def calculate_food_nutrients(food_name, amount, unit):
    """
    CSV의 기준량에 맞춰 실제 섭취량의 영양소를 계산한다.
    """

    result = {
        key: 0.0
        for key in NUTRIENT_KEYS
    }

    if food_name not in food_lookup:
        return result

    row = food_lookup[food_name]

    basis = to_number(row["_기준량"])
    basis_unit = str(row["_단위"])

    if amount <= 0 or basis <= 0:
        return result

    if unit != basis_unit:
        return None

    ratio = amount / basis

    for display_name, csv_column in NUTRIENT_COLUMNS.items():
        result[display_name] = (
            to_number(row.get(csv_column, 0)) * ratio
        )

    return result


def normalize_foods(food_list):
    normalized = []

    for food in food_list:
        if not isinstance(food, dict):
            continue

        name = str(food.get("음식 이름", "")).strip()

        if not name:
            continue

        try:
            amount = float(
                food.get("섭취량", food.get("섭취량(g)", 0)) or 0
            )
        except (ValueError, TypeError):
            amount = 0.0

        unit = str(food.get("단위", "g"))

        if unit not in ["g", "ml"]:
            unit = "g"

        normalized.append({
            "음식 이름": name,
            "섭취량": amount,
            "단위": unit
        })

    return normalized


def calculate_meal_total(food_list):
    totals = {
        key: 0.0
        for key in NUTRIENT_KEYS
    }

    unmatched = []

    for food in food_list:
        name = food["음식 이름"]
        amount = food["섭취량"]
        unit = food["단위"]

        nutrients = calculate_food_nutrients(
            name,
            amount,
            unit
        )

        if nutrients is None:
            unmatched.append(name)
            continue

        for key in NUTRIENT_KEYS:
            totals[key] += nutrients[key]

    return totals, unmatched


def get_day_foods(day_record):
    result = []

    for meal in MEALS:
        result.extend(
            normalize_foods(day_record.get(meal, []))
        )

    return result


# ==================================================
# 기록 저장 및 불러오기
# ==================================================

def load_records():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

        except (json.JSONDecodeError, OSError):
            st.warning("저장된 기록을 불러오지 못했습니다.")

    return {}


def save_records(records):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4
        )


if "meal_records" not in st.session_state:
    st.session_state["meal_records"] = load_records()

records = st.session_state["meal_records"]

# ==================================================
# 날짜 선택
# ==================================================

st.subheader("📅 기록할 날짜")

selected_date = st.date_input(
    "식사 기록 날짜를 선택하세요.",
    value=date.today(),
    key="record_date"
)

date_key = selected_date.isoformat()

st.caption(
    f"선택한 날짜: {selected_date.strftime('%Y년 %m월 %d일')}"
)

# ==================================================
# 음식 입력
# ==================================================

st.divider()
st.subheader("🥗 오늘 먹은 음식 입력")

st.info(
    "CSV에 등록된 음식 이름을 입력하고 섭취량과 단위를 선택하면 "
    "영양소가 자동으로 계산됩니다."
)

st.caption(
    f"현재 데이터베이스에서 검색할 수 있는 음식: {len(food_names):,}개"
)

tabs = st.tabs(MEALS)
meal_data = {}

for index, meal in enumerate(MEALS):
    with tabs[index]:
        st.markdown(f"### 🍴 {meal}")

        saved_foods = normalize_foods(
            records.get(date_key, {}).get(meal, [])
        )

        default_df = pd.DataFrame(
            saved_foods,
            columns=["음식 이름", "섭취량", "단위"]
        )

        edited_df = st.data_editor(
            default_df,
            key=f"editor_{date_key}_{meal}",
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "음식 이름": st.column_config.SelectboxColumn(
                    "음식 이름",
                    options=food_names,
                    help="식품 데이터베이스에 등록된 음식명을 선택하세요.",
                    required=True
                ),
                "섭취량": st.column_config.NumberColumn(
                    "섭취량",
                    min_value=0.0,
                    step=10.0,
                    format="%.1f",
                    required=True
                ),
                "단위": st.column_config.SelectboxColumn(
                    "단위",
                    options=["g", "ml"],
                    required=True
                )
            }
        )

        meal_data[meal] = edited_df

# ==================================================
# 기록 저장 및 삭제
# ==================================================

st.divider()
st.subheader("💾 기록 관리")

col1, col2 = st.columns(2)

with col1:
    save_button = st.button(
        "💾 식사 기록 저장",
        use_container_width=True,
        type="primary"
    )

with col2:
    delete_button = st.button(
        "🗑️ 선택한 날짜 기록 삭제",
        use_container_width=True
    )


if save_button:
    new_day_record = {}

    for meal in MEALS:
        df = meal_data[meal].copy()
        saved_list = []

        for _, row in df.iterrows():
            name = str(row.get("음식 이름", "")).strip()

            if not name or name not in food_lookup:
                continue

            amount = to_number(row.get("섭취량", 0))
            unit = str(row.get("단위", "g"))

            if amount <= 0:
                continue

            if unit not in ["g", "ml"]:
                unit = "g"

            basis_unit = str(food_lookup[name]["_단위"])

            if unit != basis_unit:
                st.warning(
                    f"{name}: 데이터베이스 기준 단위는 "
                    f"{basis_unit}입니다. 입력 단위를 확인해 주세요."
                )
                continue

            saved_list.append({
                "음식 이름": name,
                "섭취량": amount,
                "단위": unit
            })

        new_day_record[meal] = saved_list

    if any(new_day_record.values()):
        records[date_key] = new_day_record
    else:
        records.pop(date_key, None)

    save_records(records)
    st.session_state["meal_records"] = records

    st.success("식사 기록이 저장되었습니다!")
    st.rerun()


if delete_button:
    if date_key in records:
        del records[date_key]

        save_records(records)
        st.session_state["meal_records"] = records

        for meal in MEALS:
            st.session_state.pop(
                f"editor_{date_key}_{meal}",
                None
            )

        st.success("선택한 날짜의 기록을 삭제했습니다.")
        st.rerun()
    else:
        st.warning("삭제할 기록이 없습니다.")

# ==================================================
# 선택한 날짜 기록 확인
# ==================================================

st.divider()
st.subheader("📋 선택한 날짜의 식사 기록")

day_record = records.get(date_key, {})
has_records = False

for meal in MEALS:
    foods = normalize_foods(day_record.get(meal, []))

    if not foods:
        continue

    has_records = True

    with st.expander(
        f"🍴 {meal} ({len(foods)}개 음식)",
        expanded=True
    ):
        display_df = pd.DataFrame(foods)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        total_amount = sum(
            food["섭취량"]
            for food in foods
        )

        st.caption(f"총 섭취량: {total_amount:,.1f}")

if not has_records:
    st.info("선택한 날짜에 저장된 식사 기록이 없습니다.")

# ==================================================
# 하루 영양 분석
# ==================================================

st.divider()
st.subheader("📊 하루 영양 분석")

all_foods = get_day_foods(day_record)
daily_nutrients, unmatched = calculate_meal_total(all_foods)

if all_foods:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "기록한 음식 수",
        f"{len(all_foods)}개"
    )

    col2.metric(
        "총 열량",
        f"{daily_nutrients['열량(kcal)']:,.1f} kcal"
    )

    col3.metric(
        "탄수화물",
        f"{daily_nutrients['탄수화물(g)']:,.1f} g"
    )

    col4.metric(
        "단백질",
        f"{daily_nutrients['단백질(g)']:,.1f} g"
    )

    if unmatched:
        st.warning(
            "단위가 데이터베이스 기준과 일치하지 않아 "
            "계산하지 못한 음식: " + ", ".join(unmatched)
        )

    st.markdown("### 🍴 식사별 영양 섭취량")

    meal_nutrition_rows = []

    for meal in MEALS:
        foods = normalize_foods(
            day_record.get(meal, [])
        )

        totals, _ = calculate_meal_total(foods)

        meal_nutrition_rows.append({
            "식사": meal,
            "음식 수": len(foods),
            "열량(kcal)": totals["열량(kcal)"],
            "탄수화물(g)": totals["탄수화물(g)"],
            "단백질(g)": totals["단백질(g)"],
            "지방(g)": totals["지방(g)"]
        })

    meal_nutrition_df = pd.DataFrame(meal_nutrition_rows)

    st.dataframe(
        meal_nutrition_df.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 🥧 3대 영양소 에너지 비율")

    macro_values = {
        "탄수화물": daily_nutrients["탄수화물(g)"] * 4,
        "단백질": daily_nutrients["단백질(g)"] * 4,
        "지방": daily_nutrients["지방(g)"] * 9
    }

    macro_df = pd.DataFrame({
        "영양소": list(macro_values.keys()),
        "에너지(kcal)": list(macro_values.values())
    })

    if macro_df["에너지(kcal)"].sum() > 0:
        fig_macro = px.pie(
            macro_df,
            names="영양소",
            values="에너지(kcal)",
            hole=0.45,
            title="탄수화물·단백질·지방의 에너지 구성 비율"
        )

        fig_macro.update_layout(
            paper_bgcolor="#FBF9F1",
            font_family="Gowun Dodum"
        )

        st.plotly_chart(
            fig_macro,
            use_container_width=True
        )

    # --------------------------------------------------
    # 세부 영양소
    # --------------------------------------------------

    st.markdown("### 🧬 세부 영양소 섭취량")

    nutrient_rows = []

    for name, value in daily_nutrients.items():
        nutrient_rows.append({
            "영양소": name,
            "섭취량": round(value, 2)
        })

    nutrient_df = pd.DataFrame(nutrient_rows)

    st.dataframe(
        nutrient_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 무기질 그래프
    # --------------------------------------------------

    mineral_names = [
        "칼슘(mg)",
        "철(mg)",
        "인(mg)",
        "칼륨(mg)",
        "나트륨(mg)"
    ]

    mineral_df = pd.DataFrame({
        "무기질": mineral_names,
        "섭취량(mg)": [
            daily_nutrients[name]
            for name in mineral_names
        ]
    })

    st.markdown("### 🧂 무기질 섭취 현황")

    fig_mineral = px.bar(
        mineral_df,
        x="무기질",
        y="섭취량(mg)",
        text_auto=".1f",
        title="하루 무기질 섭취량"
    )

    fig_mineral.update_layout(
        plot_bgcolor="#FBF9F1",
        paper_bgcolor="#FBF9F1",
        font_family="Gowun Dodum"
    )

    st.plotly_chart(
        fig_mineral,
        use_container_width=True
    )

else:
    st.info(
        "음식과 섭취량을 입력하고 저장하면 "
        "하루 영양 분석 결과가 표시됩니다."
    )

# ==================================================
# 최근 7일 영양 섭취 그래프
# ==================================================

st.divider()
st.subheader("📈 영양 섭취 현황 그래프")

graph_mode = st.radio(
    "조회 기간을 선택하세요.",
    ["하루", "최근 7일"],
    horizontal=True,
    key="graph_mode"
)

if graph_mode == "하루":
    graph_dates = [date_key]
else:
    graph_dates = [
        (selected_date - timedelta(days=i)).isoformat()
        for i in range(6, -1, -1)
    ]

graph_rows = []

for graph_date in graph_dates:
    graph_day = records.get(graph_date, {})
    graph_foods = get_day_foods(graph_day)

    totals, _ = calculate_meal_total(graph_foods)

    graph_rows.append({
        "날짜": graph_date,
        "열량(kcal)": totals["열량(kcal)"],
        "탄수화물(g)": totals["탄수화물(g)"],
        "단백질(g)": totals["단백질(g)"],
        "지방(g)": totals["지방(g)"]
    })

graph_df = pd.DataFrame(graph_rows)

if graph_mode == "하루":
    st.markdown("#### 🍚 하루 영양소 섭취량")

    chart_nutrient = st.selectbox(
        "그래프로 확인할 영양소",
        ["열량(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)"],
        key="daily_graph_nutrient"
    )

    fig = px.bar(
        graph_df,
        x="날짜",
        y=chart_nutrient,
        text_auto=".1f",
        title=f"하루 {chart_nutrient} 섭취량"
    )

else:
    st.markdown("#### 📅 최근 7일 영양소 섭취량")

    chart_nutrient = st.selectbox(
        "그래프로 확인할 영양소",
        ["열량(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)"],
        key="weekly_graph_nutrient"
    )

    fig = px.line(
        graph_df,
        x="날짜",
        y=chart_nutrient,
        markers=True,
        title=f"최근 7일 {chart_nutrient} 섭취 추이"
    )

fig.update_layout(
    plot_bgcolor="#FBF9F1",
    paper_bgcolor="#FBF9F1",
    font_family="Gowun Dodum",
    xaxis_title="날짜",
    yaxis_title=chart_nutrient
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# 마무리
# ==================================================

st.divider()

st.caption(
    "NutriDay | 나의 식사 기록을 통해 건강한 식습관을 만들어 보세요."
)
