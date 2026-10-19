# 영양소 에너지 비율 도넛형 그래프
st.subheader("🥗 영양소 에너지 비율")

chart_data = pd.DataFrame({
    "영양소": ["탄수화물", "단백질", "지방"],
    "에너지 비율": [50, 30, 20]
})

st.plotly_chart(
    {
        "data": [{
            "type": "pie",
            "labels": chart_data["영양소"],
            "values": chart_data["에너지 비율"],
            "hole": 0.55,
            "textinfo": "label+percent",
            "textposition": "outside",
            "marker": {
                "colors": ["#75A88C", "#B7DCC8", "#E9CFA6"]
            }
        }],
        "layout": {
            "showlegend": False,
            "margin": {"t": 25, "b": 35, "l": 35, "r": 35},
            "height": 350
        }
    },
    use_container_width=True
)
