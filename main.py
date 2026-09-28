import streamlit as st

# 페이지 기본 설정 (와이드 모드)
st.set_page_config(
    page_title="Weather Forecast Lab",
    page_icon="⛅",
    layout="wide"
)

# 메인 타이틀
st.title("⛅ Smart Weather Forecast Lab")
st.markdown("과학적 분석(자외선, 대기오염, 체감온도)이 더해진 실생활 날씨 예측 대시보드입니다.")
st.markdown("---")

# 사이드바 - 지역 선택 및 설정
st.sidebar.header("📍 지역 및 환경 설정")
region = st.sidebar.selectbox(
    "조회할 지역을 선택하세요",
    ["서울특별시 동작구", "서울특별시 중구", "부산광역시 해운대구", "대구광역시 수성구", "제주시"]
)

st.sidebar.info(f"현재 선택된 지역: **{region}**")

# 메인 화면 레이아웃 미리보기 (추후 API 데이터로 채워질 공간)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 기온", value="-- °C", delta="-- °C (전일 대비)")

with col2:
    st.metric(label="습도", value="-- %")

with col3:
    st.metric(label="자외선(UV) 지수", value="--", delta="안전")

st.markdown("---")
st.info("💡 **1일차 개발 목표:** 앱 기본 레이아웃 구성 및 UI 컴포넌트 배치 완료!")
