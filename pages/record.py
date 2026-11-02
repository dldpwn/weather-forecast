
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import date, timedelta

# ==================================================
# 페이지 설정
# ==================================================

st.set_page_config(
    page_title="NutriDay | 식사 기록",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# 디자인
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

html, body, [class*="css"] {
    font-family: 'Gowun Dodum', sans-serif;
}

.stApp {
    background-color: #FBF9F1;
    color: #263B32;
}

h1, h2, h3 {
    color: #377D61;
}

.record-card {
    background-color: #F0F7F0;
    border: 1px solid #DCEBDD;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background-color: #F0F7F0;
    border: 1px solid #DCEBDD;
    border-radius: 12px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 제목
# ==================================================

st.title("🍽️ 식사 기록 & 영양 관리")
st.markdown(
    "매일 먹은 음식을 기록하고 나의 영양 섭취 현황을 확인해 보세요."
)

st.divider()

# ==================================================
# 데이터 저장 설정
# ==================================================

DATA_FILE = Path(__file__).resolve().parent.parent / "meal_records.json"

MEALS = ["아침", "점심", "저녁", "간식"]

NUTRIENTS = [
    "열량(kcal)",
    "탄수화물(g)",
    "단백질(g)",
    "지방(g)",
    "나트륨(mg)",
    "칼슘(mg)",
    "철분(mg)",
    "칼륨(mg)"
]

COLUMNS = ["음식 이름", "섭취량(g)"] + NUTRIENTS


def load_records():
    """저장된 식사 기록 불러오기"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            st.warning("저장된 기록을 읽지 못했습니다. 새 기록을 시작합니다.")

    return {}


def save_records(records):
    """식사 기록 JSON 파일에 저장"""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)


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

st.caption(f"선택한 날짜: {selected_date.strftime('%Y년 %m월 %d일')}")

# ==================================================
# 식사 기록 입력
# ==================================================

st.divider()
st.subheader("🥗 오늘 먹은 음식 입력")

st.info(
    "음식 이름과 섭취량, 영양성분을 입력해 주세요. "
    "한 끼에 여러 음식을 추가할 수 있습니다."
)

meal_data = {}

tabs = st.tabs(MEALS)

for index, meal in enumerate(MEALS):

    with tabs[index]:

        st.markdown(f"### 🍴 {meal}")

        saved_foods = records.get(date_key, {}).get(meal, [])

        if saved_foods:
            default_df = pd.DataFrame(saved_foods)
            default_df = default_df.reindex(columns=COLUMNS, fill_value=0)
        else:
            default_df = pd.DataFrame(
                [{
                    "음식 이름": "",
                    "섭취량(g)": 0,
                    **{nutrient: 0 for nutrient in NUTRIENTS}
                }],
                columns=COLUMNS
            )

        edited_df = st.data_editor(
            default_df,
            key=f"editor_{date_key}_{meal}",
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "음식 이름": st.column_config.TextColumn(
                    "음식 이름",
                    help="먹은 음식의 이름을 입력하세요.",
                    width="medium"
                ),
                "섭취량(g)": st.column_config.NumberColumn(
                    "섭취량(g)",
                    min_value=0,
                    step=10,
                    format="%.1f"
                ),
                "열량(kcal)": st.column_config.NumberColumn(
                    "열량(kcal)",
                    min_value=0,
                    step=1
                ),
                "탄수화물(g)": st.column_config.NumberColumn(
                    "탄수화물(g)",
                    min_value=0,
                    step=1
                ),
                "단백질(g)": st.column_config.NumberColumn(
                    "단백질(g)",
                    min_value=0,
                    step=1
                ),
                "지방(g)": st.column_config.NumberColumn(
                    "지방(g)",
                    min_value=0,
                    step=1
                ),
                "나트륨(mg)": st.column_config.NumberColumn(
                    "나트륨(mg)",
                    min_value=0,
                    step=10
                ),
                "칼슘(mg)": st.column_config.NumberColumn(
                    "칼슘(mg)",
                    min_value=0,
                    step=10
                ),
                "철분(mg)": st.column_config.NumberColumn(
                    "철분(mg)",
                    min_value=0,
                    step=1
                ),
                "칼륨(mg)": st.column_config.NumberColumn(
                    "칼륨(mg)",
                    min_value=0,
                    step=10
                )
            }
        )

        meal_data[meal] = edited_df

# ==================================================
# 기록 저장
# ==================================================

st.divider()

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
        df = df.fillna(0)

        # 음식 이름이 입력된 행만 저장
        df["음식 이름"] = df["음식 이름"].astype(str).str.strip()
        df = df[df["음식 이름"] != ""]

        saved_list = []

        for _, row in df.iterrows():

            food = {}

            for column in COLUMNS:
                if column == "음식 이름":
                    food[column] = str(row[column])
                else:
                    food[column] = float(row[column])

            saved_list.append(food)

        new_day_record[meal] = saved_list

    # 모든 식사 칸이 비어 있으면 날짜 기록 제거
    if not any(new_day_record.values()):
        records.pop(date_key, None)
    else:
        records[date_key] = new_day_record

    save_records(records)

    st.session_state["meal_records"] = records

    st.success("식사 기록이 저장되었습니다!")
    st.rerun()


if delete_button:

    if date_key in records:
        del records[date_key]
        save_records(records)
        st.session_state["meal_records"] = records
        st.success("선택한 날짜의 기록을 삭제했습니다.")
        st.rerun()
    else:
        st.warning("삭제할 기록이 없습니다.")

# ==================================================
# 하루 영양 분석
# ==================================================

st.divider()
st.subheader("📊 하루 영양 분석")

if date_key in records:

    daily_df = pd.DataFrame()

    all_foods = []

    for meal in MEALS:
        all_foods.extend(records[date_key].get(meal, []))

    if all_foods:
        daily_df = pd.DataFrame(all_foods)

        totals = daily_df[NUTRIENTS].sum()

        # 주요 영양소
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "총 섭취 열량",
            f"{totals['열량(kcal)']:,.0f} kcal"
        )

        col2.metric(
            "탄수화물",
            f"{totals['탄수화물(g)']:,.1f} g"
        )

        col3.metric(
            "단백질",
            f"{totals['단백질(g)']:,.1f} g"
        )

        col4.metric(
            "지방",
            f"{totals['지방(g)']:,.1f} g"
        )

        st.markdown("#### 🧂 무기질 섭취량")

        mineral_cols = st.columns(4)

        minerals = [
            "나트륨(mg)",
            "칼슘(mg)",
            "철분(mg)",
            "칼륨(mg)"
        ]

        for index, mineral in enumerate(minerals):
            mineral_cols[index].metric(
                mineral,
                f"{totals[mineral]:,.1f}"
            )

        st.markdown("#### 🍴 식사별 섭취 열량")

        meal_calories = []

        for meal in MEALS:
            meal_total = sum(
                float(food.get("열량(kcal)", 0))
                for food in records[date_key].get(meal, [])
            )

            meal_calories.append({
                "식사": meal,
                "열량(kcal)": meal_total
            })

        meal_chart_df = pd.DataFrame(meal_calories)

        fig = px.bar(
            meal_chart_df,
            x="식사",
            y="열량(kcal)",
            text_auto=".0f",
            title="식사별 열량 섭취 현황",
            color="식사"
        )

        fig.update_layout(
            plot_bgcolor="#FBF9F1",
            paper_bgcolor="#FBF9F1",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📋 오늘 먹은 음식")

        st.dataframe(
            daily_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("아직 입력된 음식이 없습니다.")

else:
    st.info("선택한 날짜에 저장된 식사 기록이 없습니다.")

# ==================================================
# 하루 / 일주일 영양 섭취 그래프
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

    day_record = records.get(graph_date, {})

    all_foods = []

    for meal in MEALS:
        all_foods.extend(day_record.get(meal, []))

    if all_foods:

        food_df = pd.DataFrame(all_foods)

        row = {
            "날짜": graph_date
        }

        for nutrient in NUTRIENTS:
            row[nutrient] = pd.to_numeric(
                food_df[nutrient],
                errors="coerce"
            ).fillna(0).sum()

        graph_rows.append(row)

    else:

        row = {"날짜": graph_date}

        for nutrient in NUTRIENTS:
            row[nutrient] = 0

        graph_rows.append(row)


graph_df = pd.DataFrame(graph_rows)

if graph_mode == "하루":

    selected_nutrient = st.selectbox(
        "확인할 영양소를 선택하세요.",
        NUTRIENTS,
        key="daily_graph_nutrient"
    )

    fig = px.bar(
        graph_df,
        x="날짜",
        y=selected_nutrient,
        text_auto=".1f",
        title=f"하루 {selected_nutrient} 섭취량"
    )

else:

    selected_nutrient = st.selectbox(
        "확인할 영양소를 선택하세요.",
        NUTRIENTS,
        key="weekly_graph_nutrient"
    )

    fig = px.line(
        graph_df,
        x="날짜",
        y=selected_nutrient,
        markers=True,
        title=f"최근 7일 {selected_nutrient} 섭취 변화"
    )

fig.update_layout(
    plot_bgcolor="#FBF9F1",
    paper_bgcolor="#FBF9F1",
    xaxis_title="날짜",
    yaxis_title=selected_nutrient
)

st.plotly_chart(fig, use_container_width=True)

# ==================================================
# 기록 다운로드
# ==================================================

st.divider()
st.subheader("📥 식사 기록 다운로드")

if records:

    export_df = []

    for saved_date, day_record in records.items():

        for meal in MEALS:

            for food in day_record.get(meal, []):

                row = {
                    "날짜": saved_date,
                    "식사": meal
                }

                row.update(food)
                export_df.append(row)

    if export_df:

        export_df = pd.DataFrame(export_df)

        st.download_button(
            "식사 기록 CSV 다운로드",
            data=export_df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="NutriDay_meal_records.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("다운로드할 식사 기록이 없습니다.")

st.divider()

st.caption(
    "NutriDay | 나의 식사 기록을 통해 건강한 식습관을 만들어 보세요."
)
