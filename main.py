import streamlit as st
import datetime

st.set_page_config(
    page_title="Weather Forecast Lab",
    page_icon="⛅",
    layout="wide"
)

st.title("⛅ Smart Weather Forecast Lab")
st.markdown("---")

# 1단계: 계층형 지역 데이터 구조 정의 (시/도 -> 시/군/구 -> 읍/면/동)
region_data = {
    "서울특별시": {
        "동작구": ["신대방동", "노량진동", "흑석동", "상도동"],
        "중구": ["명동", "을지로동", "남대문로동", "장충동"],
        "종로구": ["청운동", "신교동", "부암동", "사직동"]
    },
    "부산광역시": {
        "해운대구": ["우동", "중동", "좌동", "반송동"],
        "수영구": ["남천동", "수영동", "망미동", "민락동"]
    },
    "제주특별자치도": {
        "제주시": ["일도동", "이도동", "삼도동", "외도동"],
        "서귀포시": ["중문동", "대정읍", "남원읍", "성산읍"]
    }
}

# 사이드바 - 계층형 지역 선택 UI
st.sidebar.header("📍 상세 지역 설정")

# 1. 시/도 선택
selected_sido = st.sidebar.selectbox("시/도 선택", list(region_data.keys()))

# 2. 시/군/구 선택 (선택된 시/도에 하위 목록 연동)
sigungu_list = list(region_data[selected_sido].keys())
selected_sigungu = st.sidebar.selectbox("시/군/구 선택", sigungu_list)

# 3. 읍/면/동 선택 (선택된 시/군/구에 하위 목록 연동)
dong_list = region_data[selected_sido][selected_sigungu]
selected_dong = st.sidebar.selectbox("읍/면/동 선택", dong_list)

# 최종 선택된 지역 조합
full_location = f"{selected_sido} {selected_sigungu} {selected_dong}"
st.sidebar.success(f"선택된 지역: **{full_location}**")

# 현재 시간 표시
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
st.text(f"📍 현재 조회 위치: {full_location} (기준 시각: {now})")
st.markdown("---")

# 상단 메트릭 지표 출력 (가상 데이터 연동)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 기온", value="25.8 °C", delta="-3 °C (전일 대비)")

with col2:
    st.metric(label="습도", value="39 %")

with col3:
    st.metric(label="자외선(UV) 지수", value="보통 (3.5)")

st.markdown("---")

# 대기 환경 정보 섹션
st.subheader("🔬 대기 환경 및 화학 지표 분석")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(label="초미세먼지 (PM2.5)", value="11 µg/m³", delta="좋음", delta_color="normal")

with col_b:
    st.metric(label="미세먼지 (PM10)", value="21 µg/m³", delta="좋음", delta_color="normal")

with col_c:
    st.metric(label="오존 (O₃)", value="0.037 ppm", delta="보통", delta_color="off")

st.markdown("---")

# 과학적 행동 요령 가이드
st.subheader("💡 과학적 외출 가이드")
st.info("✅ **자외선 양호:** 야외 활동에 큰 무리가 없으나 장시간 노출 시 가벼운 차단제를 권장합니다.")
