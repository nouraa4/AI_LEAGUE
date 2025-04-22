import streamlit as st
import os
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تحميل YOLO model إذا ما كان موجود
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 تحميل نموذج الذكاء الاصطناعي..."):
        gdown.download(model_url, model_path, quiet=False)
model = YOLO(model_path)

# تنسيق CSS
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #ffffff;
    }
    .main {
        padding: 2rem;
    }
    .stButton > button {
        background-color: #00C896;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
    }
    .stTextInput > div > div > input {
        background-color: #2c2c2c;
        color: white;
        border-radius: 8px;
    }
    .hero {
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# البوابات ومواقعها
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
    "G": {"path": "crowd_system/G/g.png", "lat": 21.6242, "lon": 39.1122, "zone": "غرب"},
}

# تحليل الصور
gate_info = {}
for gate, info in gate_dirs.items():
    if os.path.exists(info["path"]):
        results = model(info["path"])[0]
        count = sum(1 for c in results.boxes.cls if int(c) == 0)
        level, color = (
            ("خفيف", "#00C896") if count <= 10 else
            ("متوسط", "#FFC300") if count <= 30 else
            ("عالي", "#FF5733")
        )
        gate_info[gate] = {
            "count": count,
            "level": level,
            "color": color,
            "lat": info["lat"],
            "lon": info["lon"],
            "zone": info["zone"]
        }

# session state
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "closed_gates" not in st.session_state:
    st.session_state.closed_gates = []
if "logged_users" not in st.session_state:
    st.session_state.logged_users = []

if st.session_state.page == "welcome":
    st.markdown("""
        <style>
        .bg-container {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('welcome.png');
            background-size: cover;
            background-position: center;
            z-index: -2;
        }

        .overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(0, 0, 0, 0.75);
            z-index: -1;
        }

        .content {
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
        }

        .welcome-title {
            font-size: 3rem;
            font-weight: bold;
            color: white;
            margin-bottom: 3rem;
        }

        .button-row {
            display: flex;
            gap: 2rem;
        }

        .stButton > button {
            background-color: transparent;
            color: white;
            border: 2px solid white;
            padding: 0.8rem 2rem;
            font-size: 1.2rem;
            border-radius: 10px;
            font-weight: bold;
            transition: 0.3s;
        }

        .stButton > button:hover {
            background-color: white;
            color: black;
            border: 2px solid white;
        }
        </style>

        <div class="bg-container"></div>
        <div class="overlay"></div>
        <div class="content">
            <div class="welcome-title">🏟️ F.A.N.S - الملعب الذكي للمشجعين</div>
            <div class="button-row">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("أنا مشجع"):
            st.session_state.page = "fan"
    with col2:
        if st.button("أنا منظم"):
            st.session_state.page = "admin"

    st.markdown("</div></div>", unsafe_allow_html=True)
    
    
# صفحة المشجع
elif st.session_state.page == "fan":
    st.title("🏟️ دخول المشجع")
    with st.form("fan_form"):
        name = st.text_input("الاسم")
        ticket = st.text_input("رقم التذكرة (مثال: C123)")
        submitted = st.form_submit_button("تسجيل الدخول")
        if submitted:
            if not name or not ticket:
                st.warning("يرجى تعبئة جميع الحقول")
            else:
                st.session_state.logged_users.append({"name": name, "ticket": ticket})
                st.success(f"مرحباً {name}!")
                zone = gate_dirs.get(ticket[0].upper(), {}).get("zone")
                if zone:
                    available = {
                        g: d for g, d in gate_info.items()
                        if d["zone"] == zone and g not in st.session_state.closed_gates
                    }
                    options = {g: d for g, d in available.items() if d["level"] != "عالي"}
                    if options:
                        gate = min(options.items(), key=lambda x: x[1]["count"])[0]
                        level = options[gate]["level"]
                        st.success(f"البوابة الموصى بها: {gate} (ازدحام {level})")
                    else:
                        st.warning("كل البوابات في منطقتك مزدحمة أو مغلقة")
                else:
                    st.error("رقم التذكرة غير معروف")

# صفحة المنظم
elif st.session_state.page == "admin":
    st.title("📊 لوحة تحكم المنظم")

    st.subheader("🚪 إدارة البوابات")
    for gate in gate_info.keys():
        if st.checkbox(f"إغلاق بوابة {gate}", value=gate in st.session_state.closed_gates):
            if gate not in st.session_state.closed_gates:
                st.session_state.closed_gates.append(gate)
        else:
            if gate in st.session_state.closed_gates:
                st.session_state.closed_gates.remove(gate)

    st.subheader("👁️‍🗨️ حالة البوابات")
    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.info(f"""### بوابة {gate}
👥 عدد الأشخاص: {data['count']}
🚦 الازدحام: {data['level']}
🔒 الحالة: {"مغلقة" if gate in st.session_state.closed_gates else "مفتوحة"}
""")

    st.subheader("🚨 تنبيهات")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in st.session_state.closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")

    st.subheader("📝 قائمة المشجعين الذين سجلوا الدخول")
    for user in st.session_state.logged_users:
        st.write(f"- {user['name']} | تذكرة: {user['ticket']}")
