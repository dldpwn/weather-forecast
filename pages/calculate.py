import streamlit as st

# 1. 페이지 설정 (사이드바 기본 숨김)
st.set_page_config(
    page_title="새로운 페이지",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 디자인 및 사이드바 스타일 적용
st.markdown("""
    
""", unsafe_allow_html=True)

# --- 사이드바 영역 ---
with st.sidebar:
    st.markdown("### 🧭 메뉴 이동")
    st.info("💡 왼쪽 위의 **`>` (화살표)**를 누르면 사이드바를 다시 숨길 수 있어요!")
    st.page_link("main.py", label="🧪 영양소 & 화학 계산기", icon="🧮")
    st.page_link("pages/2_📝_탐구_기록장.py", label="📝 새로운 서브 페이지", icon="📄")

# --- 메인 화면 (빈 페이지) ---
st.title("📄 새로운 서브 페이지")
st.write("이곳에 원하시는 다른 과학 관련 내용이나 기능을 자유롭게 채워 넣으세요!")
st.divider()

# 여기에 나중에 필요한 컴포넌트나 코드를 작성하시면 됩니다.
st.info("💡 빈 공간입니다. 필요한 내용을 추가해 보세요.")
