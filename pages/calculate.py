# 하루 에너지 참고값
daily_energy = st.session_state["meal_plan_calories"]

# 영양소별 에너지 비율(%)
carb_ratio = 50
protein_ratio = 20
fat_ratio = 30

# 에너지량(kcal)
carb_kcal = daily_energy * carb_ratio / 100
protein_kcal = daily_energy * protein_ratio / 100
fat_kcal = daily_energy * fat_ratio / 100

# g 단위 환산
carb_g = carb_kcal / 4
protein_g = protein_kcal / 4
fat_g = fat_kcal / 9

st.subheader("🥗 하루 에너지 구성 비율")

st.caption(
    f"하루 에너지 참고값 {daily_energy:,.0f} kcal 기준"
)

chart_data = pd.DataFrame({
    "영양소": ["탄수화물", "단백질", "지방"],
    "에너지량(kcal)": [carb_kcal, protein_kcal, fat_kcal],
    "에너지 비율(%)": [carb_ratio, protein_ratio, fat_ratio],
})

fig = px.pie(
    chart_data,
    names="영양소",
    values="에너지량(kcal)",
    hole=0.55,
)

fig.update_traces(
    texttemplate="%{label}<br>%{percent}",
    textposition="inside",
)

fig.update_layout(
    showlegend=True,
    margin=dict(t=20, b=20, l=10, r=10),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="nutrition_donut_chart",
)

st.dataframe(
    chart_data,
    hide_index=True,
    use_container_width=True,
)
