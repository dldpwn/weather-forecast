import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영양소 & 화학 반응 계산기",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# 2. 따뜻하고 둥근 폰트(Sunflower) 및 전체 스타일 적용
st.markdown("""
    
""", unsafe_allow_html=True)

# --- 사이드바 영역 ---
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.info("💡 왼쪽 위의 **`>` (화살표)**를 누르면 사이드바를 다시 숨길 수 있어요!")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    st.page_link("pages/calculate.py", label="🥗 맞춤형 식단 플래너", icon="🥗")

# --- 메인 화면 ---
st.title("🧪 내 몸에 맞는 영양소 & 화학 반응 계산기")
st.write("나의 신체 정보를 입력하고, 비만도(BMI), 하루 대사량, 그리고 몸속 화학 반응을 확인해보세요!")
st.divider()

# 크기가 흔들리지 않도록 커스텀 클래스 적용
st.markdown('
