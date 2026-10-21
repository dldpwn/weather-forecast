import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="식단 구성 확인 | NutriDay",
    page_icon="🥗",
    layout="wide"
)

# ==========================================
# 기본 디자인
# ==========================================

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

    .info-card {
        background-color: #F1F8F3;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 사이드바
# ==========================================

with st.sidebar:
    st.markdown("## 🥗 NutriDay")
    st.caption("나에게 맞는 하루 영양 관리")

    st.page_link("main.py", label="🏠 메인 페이지")
    st.page_link(
        "pages/calculate.py",
        label="🥗 식단 구성 확인"
    )


# ==========================================
# 제목
# ==========================================

st.markdown(
    '<div class="main-title">🥗 하루 식단 구성 확인</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-text">'
    '하루 에너지 참고값을 바탕으로 식단을 살펴보고, '
    '식단에 포함된 주요 영양소를 확인해 보세요.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# 하루 에너지 참고값
# ==========================================

# 첫 번째 페이지에서 저장한 값 불러오기
# calculated_tdee: 하루 총 에너지 소비량을 저장한 키
# meal_plan_calories: 기존 페이지에서 사용하던 키도 지원

saved_energy = st.session_state.get(
    "calculated_tdee",
    st.session_state.get(
        "meal_plan_calories",
        2000
    )
)

try:
    saved_energy = float(saved_energy)
except (TypeError, ValueError):
    saved_energy = 2000.0

if saved_energy <= 0:
    saved_energy = 2000.0

st.markdown("### 🔥 나의 하루 에너지 참고값")

st.metric(
    label="하루 에너지 참고값",
    value=f"{saved_energy:,.0f} kcal"
)

st.caption(
    "첫 번째 페이지에서 계산한 값이 있으면 해당 값을 사용해요. "
    "값이 없으면 2,000 kcal를 예시로 사용해요."
)


# ==========================================
# 식단 목표 선택
# ==========================================

st.markdown("### 🎯 식단 목표")

goal = st.radio(
    "목표를 선택하세요.",
    ["에너지 균형", "체중 감량 참고", "근육 증가 참고"],
    horizontal=True
)

if goal == "에너지 균형":
    target_energy = saved_energy

elif goal == "체중 감량 참고":
    target_energy = max(500, saved_energy - 500)

else:
    target_energy = saved_energy + 300

st.session_state["meal_plan_calories"] = target_energy

st.info(
    f"선택한 목표의 하루 에너지 참고값은 "
    f"**{target_energy:,.0f} kcal**예요."
)

st.caption(
    "목표별 증감량은 기능 설명을 위한 단순 예시이며, "
    "개인에게 적합한 에너지 섭취량을 확정하는 기준은 아니에요."
)


# ==========================================
# 식단 예시 및 영양 데이터
# ==========================================
#
# 영양 성분 값은 예시용 추정치이며 실제 제품이나 조리법에 따라 달라짐.
#
# 각 음식의 데이터:
# kcal, 탄수화물(g), 단백질(g), 지방(g), 식이섬유(g),
# 칼슘(mg), 철(mg), 칼륨(mg), 나트륨(mg),
# 비타민 A(µg RAE), 비타민 C(mg), 비타민 D(µg)
#
# 아래 값은 실제 식품 데이터베이스를 조회한 측정값이 아님.

foods = {
    "통밀빵": {
        "kcal": 160,
        "carbs": 28,
        "protein": 7,
        "fat": 2.5,
        "fiber": 4,
        "calcium": 60,
        "iron": 1.5,
        "potassium": 120,
        "sodium": 280,
        "vitamin_a": 0,
        "vitamin_c": 0,
        "vitamin_d": 0
    },
    "달걀": {
        "kcal": 78,
        "carbs": 0.6,
        "protein": 6.3,
        "fat": 5.3,
        "fiber": 0,
        "calcium": 28,
        "iron": 0.9,
        "potassium": 69,
        "sodium": 62,
        "vitamin_a": 75,
        "vitamin_c": 0,
        "vitamin_d": 1.1
    },
    "바나나": {
        "kcal": 89,
        "carbs": 22.8,
        "protein": 1.1,
        "fat": 0.3,
        "fiber": 2.6,
        "calcium": 5,
        "iron": 0.3,
        "potassium": 358,
        "sodium": 1,
        "vitamin_a": 3,
        "vitamin_c": 8.7,
        "vitamin_d": 0
    },
    "우유": {
        "kcal": 122,
        "carbs": 12,
        "protein": 8,
        "fat": 4.8,
        "fiber": 0,
        "calcium": 300,
        "iron": 0.1,
        "potassium": 380,
        "sodium": 100,
        "vitamin_a": 60,
        "vitamin_c": 0,
        "vitamin_d": 2.5
    },
    "밥": {
        "kcal": 310,
        "carbs": 68,
        "protein": 5.5,
        "fat": 0.7,
        "fiber": 1,
        "calcium": 10,
        "iron": 0.6,
        "potassium": 70,
        "sodium": 5,
        "vitamin_a": 0,
        "vitamin_c": 0,
        "vitamin_d": 0
    },
    "닭가슴살": {
        "kcal": 165,
        "carbs": 0,
        "protein": 31,
        "fat": 3.6,
        "fiber": 0,
        "calcium": 15,
        "iron": 1,
        "potassium": 256,
        "sodium": 74,
        "vitamin_a": 6,
        "vitamin_c": 0,
        "vitamin_d": 0.1
    },
    "시금치": {
        "kcal": 23,
        "carbs": 3.6,
        "protein": 2.9,
        "fat": 0.4,
        "fiber": 2.2,
        "calcium": 99,
        "iron": 2.7,
        "potassium": 558,
        "sodium": 79,
        "vitamin_a": 469,
        "vitamin_c": 28,
        "vitamin_d": 0
    },
    "브로콜리": {
        "kcal": 34,
        "carbs": 6.6,
        "protein": 2.8,
        "fat": 0.4,
        "fiber": 2.6,
        "calcium": 47,
        "iron": 0.7,
        "potassium": 316,
        "sodium": 33,
        "vitamin_a": 31,
        "vitamin_c": 89,
        "vitamin_d": 0
    },
    "고구마": {
        "kcal": 130,
        "carbs": 30,
        "protein": 2,
        "fat": 0.1,
        "fiber": 3.9,
        "calcium": 30,
        "iron": 0.6,
        "potassium": 475,
        "sodium": 55,
        "vitamin_a": 709,
        "vitamin_c": 2.4,
        "vitamin_d": 0
    },
    "두부": {
        "kcal": 76,
        "carbs": 1.9,
        "protein": 8,
        "fat": 4.8,
        "fiber": 0.3,
        "calcium": 350,
        "iron": 1.6,
        "potassium": 121,
        "sodium": 7,
        "vitamin_a": 0,
        "vitamin_c": 0,
        "vitamin_d": 0
    },
    "사과": {
        "kcal": 95,
        "carbs": 25,
        "protein": 0.5,
        "fat": 0.3,
        "fiber": 4.4,
        "calcium": 11,
        "iron": 0.2,
        "potassium": 195,
        "sodium": 2,
        "vitamin_a": 5,
        "vitamin_c": 8.4,
        "vitamin_d": 0
    }
}


# ==========================================
# 기본 식단
# ==========================================

# 각 음식의 수량은 위 데이터에 정의된 1회 분량을 기준으로 함.
# 이 식단은 기능 시연용 예시 식단임.

meal_plan = {
    "아침": {
        "통밀빵": 1,
        "달걀": 1,
        "바나나": 1,
        "우유": 1
    },
    "점심": {
        "밥": 1,
        "닭가슴살": 1,
        "시금치": 1,
        "브로콜리": 1
    },
    "저녁": {
        "고구마": 1,
        "두부": 1,
        "브로콜리": 1,
        "사과": 1
    }
}


# ==========================================
# 식사별 음식 표시
# ==========================================

st.divider()
st.markdown("### 🍽️ 하루 식단 예시")

st.caption(
    "아래 식단은 영양 분석 기능을 보여 주기 위한 예시예요."
)

breakfast_tab, lunch_tab, dinner_tab = st.tabs(
    ["🌅 아침", "☀️ 점심", "🌙 저녁"]
)

with breakfast_tab:
    st.markdown("#### 아침 식사")
    st.write("통밀빵 · 달걀 · 바나나 · 우유")

    for food_name, quantity in meal_plan["아침"].items():
        st.write(f"- {food_name}: {quantity}회 분량")

with lunch_tab:
    st.markdown("#### 점심 식사")
    st.write("밥 · 닭가슴살 · 시금치 · 브로콜리")

    for food_name, quantity in meal_plan["점심"].items():
        st.write(f"- {food_name}: {quantity}회 분량")

with dinner_tab:
    st.markdown("#### 저녁 식사")
    st.write("고구마 · 두부 · 브로콜리 · 사과")

    for food_name, quantity in meal_plan["저녁"].items():
        st.write(f"- {food_name}: {quantity}회 분량")


# ==========================================
# 하루 식단 영양소 합산
# ==========================================

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

total_nutrients = {
    key: 0.0 for key in nutrient_keys
}

meal_nutrients = {}

for meal_name, meal_foods in meal_plan.items():

    meal_total = {
        key: 0.0 for key in nutrient_keys
    }

    for food_name, quantity in meal_foods.items():

        food_info = foods[food_name]

        for key in nutrient_keys:
            meal_total[key] += (
                food_info[key] * quantity
            )

    meal_nutrients[meal_name] = meal_total

    for key in nutrient_keys:
        total_nutrients[key] += meal_total[key]


# ==========================================
# 실제 예시 식단의 에너지 구성 비율
# ==========================================

st.divider()
st.markdown("### 📊 하루 에너지 구성 비율")

st.caption(
    "아래 그래프는 하루 에너지 참고값을 기준으로 "
    "임의의 비율을 표시하는 것이 아니라, "
    "예시 식단에 포함된 탄수화물·단백질·지방의 양을 "
    "바탕으로 계산해요."
)

# 탄수화물과 단백질은 약 4 kcal/g,
# 지방은 약 9 kcal/g으로 계산
carb_energy = total_nutrients["carbs"] * 4
protein_energy = total_nutrients["protein"] * 4
fat_energy = total_nutrients["fat"] * 9

macro_energy_total = (
    carb_energy + protein_energy + fat_energy
)

if macro_energy_total > 0:

    chart_data = pd.DataFrame({
        "영양소": [
            "탄수화물",
            "단백질",
            "지방"
        ],
        "에너지량(kcal)": [
            carb_energy,
            protein_energy,
            fat_energy
        ]
    })

    chart_data["에너지 비율(%)"] = (
        chart_data["에너지량(kcal)"]
        / macro_energy_total * 100
    )

    fig = px.pie(
        chart_data,
        names="영양소",
        values="에너지량(kcal)",
        hole=0.55
    )

    fig.update_traces(
        texttemplate="%{label}<br>%{percent}",
        textposition="inside",
        hovertemplate=(
            "%{label}<br>"
            "에너지량: %{value:.1f} kcal<br>"
            "비율: %{percent}<extra></extra>"
        )
    )

    fig.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=10, r=10),
        legend_title_text="영양소"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="nutrition_donut_chart"
    )

    st.write(
        f"**하루 에너지 참고값:** "
        f"{target_energy:,.0f} kcal"
    )

    st.write(
        f"**예시 식단의 총에너지:** "
        f"{total_nutrients['kcal']:,.0f} kcal"
    )

    st.write(
        f"**3대 영양소로 계산한 에너지:** "
        f"{macro_energy_total:,.1f} kcal"
    )

    st.caption(
        "식품별 표시 열량과 4·4·9 환산값은 "
        "식이섬유, 식품 성분, 반올림 등의 영향으로 "
        "완전히 일치하지 않을 수 있어요."
    )


# ==========================================
# 영양소별 섭취량
# ==========================================

st.divider()
st.markdown("### 🧬 주요 영양소 분석")

st.caption(
    "아래 수치는 위에 제시된 예시 식단의 음식별 "
    "영양 성분 추정치를 합산한 값이에요."
)

macro_table = pd.DataFrame({
    "영양소": [
        "탄수화물",
        "단백질",
        "지방",
        "식이섬유"
    ],
    "하루 섭취량": [
        f"{total_nutrients['carbs']:.1f} g",
        f"{total_nutrients['protein']:.1f} g",
        f"{total_nutrients['fat']:.1f} g",
        f"{total_nutrients['fiber']:.1f} g"
    ]
})

st.dataframe(
    macro_table,
    hide_index=True,
    use_container_width=True
)


# ==========================================
# 비타민 및 무기질
# ==========================================

st.markdown("### 💊 비타민 및 무기질")

st.caption(
    "비타민과 무기질은 에너지를 직접 제공하지 않으므로 "
    "에너지 비율이 아닌 함량으로 표시해요."
)

# 아래 기준값은 예시 식단의 교육용 비교를 위한 참고값.
# 실제 권장량은 성별, 나이, 생애주기 등에 따라 달라질 수 있음.

reference_values = {
    "칼슘": {
        "key": "calcium",
        "unit": "mg",
        "reference": 1000
    },
    "철": {
        "key": "iron",
        "unit": "mg",
        "reference": 14
    },
    "칼륨": {
        "key": "potassium",
        "unit": "mg",
        "reference": 3500
    },
    "나트륨": {
        "key": "sodium",
        "unit": "mg",
        "reference": 2000
    },
    "비타민 A": {
        "key": "vitamin_a",
        "unit": "µg RAE",
        "reference": 800
    },
    "비타민 C": {
        "key": "vitamin_c",
        "unit": "mg",
        "reference": 100
    },
    "비타민 D": {
        "key": "vitamin_d",
        "unit": "µg",
        "reference": 10
    }
}

vitamin_rows = []

for nutrient_name, info in reference_values.items():

    amount = total_nutrients[info["key"]]
    reference = info["reference"]

    percentage = (
        amount / reference * 100
        if reference > 0 else 0
    )

    vitamin_rows.append({
        "영양소": nutrient_name,
        "예시 식단 함량": (
            f"{amount:.1f} {info['unit']}"
        ),
        "비교용 참고량": (
            f"{reference} {info['unit']}"
        ),
        "참고량 대비": f"{percentage:.1f}%"
    })

vitamin_table = pd.DataFrame(vitamin_rows)

st.dataframe(
    vitamin_table,
    hide_index=True,
    use_container_width=True
)

st.caption(
    "비교용 참고량은 모든 사람에게 적용되는 개인별 권장량이 아니에요. "
    "실제 권장량은 나이와 성별 등에 따라 달라질 수 있어요."
)


# ==========================================
# 식사별 에너지 비교
# ==========================================

st.divider()
st.markdown("### 🍴 식사별 에너지")

meal_energy_rows = []

for meal_name, nutrients in meal_nutrients.items():

    meal_energy_rows.append({
        "식사": meal_name,
        "에너지(kcal)": round(
            nutrients["kcal"], 1
        ),
        "탄수화물(g)": round(
            nutrients["carbs"], 1
        ),
        "단백질(g)": round(
            nutrients["protein"], 1
        ),
        "지방(g)": round(
            nutrients["fat"], 1
        )
    })

meal_energy_df = pd.DataFrame(
    meal_energy_rows
)

st.dataframe(
    meal_energy_df,
    hide_index=True,
    use_container_width=True
)


# ==========================================
# 안내
# ==========================================

st.divider()

st.markdown("### 💡 알아두기")

st.markdown("""
- **탄수화물·단백질·지방**은 예시 식단에 포함된 양을 기준으로 에너지 비율을 계산해요.
- **비타민·무기질**은 에너지 비율이 아닌 영양소별 함량으로 표시해요.
- **식이섬유**는 하루 식단에 포함된 추정 섭취량을 표시해요.
- 음식별 영양 성분은 예시용 추정치이므로 실제 제품, 중량, 조리 방법에 따라 달라질 수 있어요.
- 이 페이지는 식단 분석 기능의 예시이며, 실제 섭취량을 측정하거나 개인별 영양 상태를 진단하지는 않아요.
""")
