import streamlit as st
import datetime

st.set_page_config(
    page_title="Weather Forecast Lab",
    page_icon="⛅",
    layout="wide"
)

st.title("⛅ Smart Weather Forecast Lab")
st.markdown("---")

# 계층형 지역 데이터 구조
region_data = {
    "서울특별시": {
        "동작구": ["신대방동", "노량진동", "흑석동", "상도동"],
        "중구": ["명동", "을지로동", "남대문로동", "장충동"]
    },
    "부산광역시": {
        "해운대구": ["우동", "중동", "좌동", "반송동"],
        "수영구": ["남천동", "수영동", "망미동", "민락동"]
    }
}

# 메인 화면에 3개의 열로 나누어 지역 선택 바 배치
st.subheader("📍 지역 선택")
col_sido, col_sigungu, col_dong = st.columns(3)

with col_sido:
    selected_sido = st.selectbox("시/도 선택", list(region_data.keys()))

with col_sigungu:
    sigungu_list = list(region_data[selected_sido].keys())
    selected_sigungu = st.selectbox("시/군/구 선택", sigungu_list)

with col_dong:
    dong_list = region_data[selected_sido][selected_sigungu]
    selected_dong = st.selectbox("읍/면/동 선택", dong_list)

full_location = f"{selected_sido} {selected_sigungu} {selected_dong}"
st.markdown("---")

# 현재 조회 위치 및 시간 표시
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
st.text(f"📍 현재 조회 위치: {full_location} (기준 시각: {now})")

# 상단 메트릭 지표 출력
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 기온", value="25.8 °C", delta="-3 °C")

with col2:
    st.metric(label="습도", value="39 %")

with col3:
    st.metric(label="자외선(UV) 지수", value="보통 (3.5)")

st.markdown("---")

# 과학적 환경 분석 섹션
st.subheader("🔬 대기 환경 및 화학 지표 분석")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(label="초미세먼지 (PM2.5)", value="11 µg/m³", delta="좋음", delta_color="normal")

with col_b:
    st.metric(label="미세먼지 (PM10)", value="21 µg/m³", delta="좋음", delta_color="normal")

with col_c:
    st.metric(label="오존 (O₃)", value="0.037 ppm", delta="보통", delta_color="off")
