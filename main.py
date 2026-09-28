import streamlit as st

st.set_page_config(
    page_title="Weather Forecast Lab",
    page_icon="⛅",
    layout="wide"
)

st.title("⛅ Smart Weather Forecast Lab")
st.markdown("---")

st.sidebar.header("📍 지역 설정")
region = st.sidebar.selectbox(
    "조회할 지역",
    ["서울특별시 동작구", "서울특별시 중구", "부산광역시 해운대구", "대구광역시 수성구", "제주시"]
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 기온", value="-- °C")

with col2:
    st.metric(label="습도", value="-- %")

with col3:
    st.metric(label="자외선(UV) 지수", value="--")
