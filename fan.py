import streamlit as st

# ====== إعدادات الصفحة ======
st.set_page_config(page_title="F.A.N.S - Recommend Gate", layout="centered")

# ====== CSS ستايل فخم بنفس طابع الصورة ======
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #121212;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
        padding: 10px 0;
    }

    .subtitle {
        font-size: 20px;
        text-align: center;
        color: #bbbbbb;
        margin-bottom: 40px;
    }

    .gate-box {
        background: linear-gradient(to right, #ff416c, #ff4b2b);
        padding: 25px;
        border-radius: 20px;
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
    }

    .stTextInput > div > div > input {
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #444;
        border-radius: 8px;
    }

    .stButton > button {
        background: linear-gradient(to right, #ff416c, #ff4b2b);
        color: white;
        border: none;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        margin-top: 10px;
    }

    .stButton > button:hover {
        background: linear-gradient(to right, #ff4b2b, #ff416c);
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# ====== المحتوى ======
st.markdown('<div class="title">F.A.N.S</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">مرحبًا بك! احصل على توصية بأفضل بوابة لدخول الملعب</div>', unsafe_allow_html=True)

ticket_number = st.text_input("أدخل رقم تذكرتك")

if st.button("اقتراح البوابة"):
    # لاحقًا: هنا تربطين مع الذكاء الاصطناعي أو قاعدة البيانات
    recommended_gate = "B2"
    st.markdown(
        f'<div class="gate-box">✅ بوابتك الأنسب: <span style="font-size:28px;">{recommended_gate}</span></div>',
        unsafe_allow_html=True
    )