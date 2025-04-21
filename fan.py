import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="F.A.N.S", layout="wide")

# ============================= CSS ستايل فخم =============================
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #121212;
        color: white;
        font-family: 'Segoe UI', sans-serif;
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

    .title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
        padding: 10px 0;
    }

    .section {
        padding: 20px;
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
    </style>
""", unsafe_allow_html=True)

# ============================= التنقل =============================
page = st.sidebar.selectbox("اختر القسم", ["الصفحة الرئيسية", "توصية البوابة", "الخريطة", "لوحة المنظم"])

# ============================= الصفحة الرئيسية =============================
if page == "الصفحة الرئيسية":
    st.markdown('<div class="title">F.A.N.S</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">نظام ذكي لإدارة الحشود داخل الملاعب باستخدام الذكاء الاصطناعي. استمتع بتجربة مخصصة وسريعة في دخولك وخروجك من الملعب.</div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1596040033229-92c48b4d4215", use_column_width=True, caption="مرحبًا بك في F.A.N.S")

# ============================= توصية البوابة =============================
elif page == "توصية البوابة":
    st.markdown('<div class="title">اقتراح البوابة</div>', unsafe_allow_html=True)
    ticket_number = st.text_input("أدخل رقم تذكرتك:")
    if st.button("احصل على التوصية"):
        # لاحقًا: ربط مع الذكاء الاصطناعي أو قاعدة بيانات
        st.markdown(
            '<div class="gate-box">✅ بوابتك الأنسب: <span style="font-size:28px;">B2</span></div>',
            unsafe_allow_html=True
        )

# ============================= الخريطة =============================
elif page == "الخريطة":
    st.markdown('<div class="title">خريطة الملعب</div>', unsafe_allow_html=True)
    st.image("https://i.imgur.com/F3n44pD.png", caption="مخطط البوابات وأماكن الازدحام", use_column_width=True)

# ============================= لوحة المنظم =============================
elif page == "لوحة المنظم":
    st.markdown('<div class="title">لوحة تحكم المنظم</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">هنا ستظهر بيانات البوابات - عدد الداخلين - التحذيرات - حالة الزحام.</div>', unsafe_allow_html=True)
    st.metric("عدد الحضور الكلي", "14,250")
    st.metric("نسبة الزحام الحالية", "67%")
    st.metric("أعلى بوابة ازدحامًا", "Gate A1")