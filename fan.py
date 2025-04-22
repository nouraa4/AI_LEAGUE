
import streamlit as st
import os
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "closed_gates" not in st.session_state:
    st.session_state.closed_gates = []

model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
model = YOLO(model_path)

gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
    "G": {"path": "crowd_system/G/g.png", "lat": 21.6242, "lon": 39.1122, "zone": "غرب"},
}

gate_info = {}
for gate, info in gate_dirs.items():
    if os.path.exists(info["path"]):
        results = model(info["path"])[0]
        count = sum(1 for c in results.boxes.cls if int(c) == 0)
        level = "خفيف" if count <= 10 else "متوسط" if count <= 30 else "عالي"
        gate_info[gate] = {
            "count": count,
            "level": level,
            "lat": info["lat"],
            "lon": info["lon"],
            "zone": info["zone"]
        }

# Welcome Page
if st.session_state.page == "welcome":
    st.markdown("""
        <style>
        .welcome-wrapper {
            position: relative;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }
        .welcome-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            position: absolute;
            top: 0;
            left: 0;
            z-index: -2;
        }
        .overlay {
            background-color: rgba(0, 0, 0, 0.5);
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
        }
        .welcome-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        .welcome-title {
            font-size: 3rem;
            font-weight: bold;
            color: white;
            margin-bottom: 40px;
        }
        .stButton>button {
            background-color: #ffffff22;
            color: white;
            border: 2px solid white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.8rem 2.2rem;
            margin: 0.8rem;
            font-size: 1.1rem;
        }
        .stButton>button:hover {
            background-color: white;
            color: black;
        }
        </style>
        <div class="welcome-wrapper">
            <img src="welcome.png" class="welcome-img">
            <div class="overlay"></div>
            <div class="welcome-content">
                <div class="welcome-title">🏟️ F.A.N.S - الملعب الذكي للمشجعين</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("أنا مشجع"):
            st.session_state.page = "fan"
    with col2:
        if st.button("أنا منظم"):
            st.session_state.page = "admin"

# Fan Page
elif st.session_state.page == "fan":
    if st.button("↩️ العودة للصفحة الرئيسية"):
        st.session_state.page = "welcome"
        st.experimental_rerun()

    st.title("🎫 توصية البوابة للمشجع")
    ticket = st.text_input("أدخل رقم تذكرتك (مثال: C123)")
    if ticket:
        zone = gate_dirs.get(ticket[0].upper(), {}).get("zone")
        if zone:
            st.info(f"📍 جهة مقعدك: {zone}")
            available = {
                g: d for g, d in gate_info.items()
                if d["zone"] == zone and g not in st.session_state.closed_gates
            }
            options = {g: d for g, d in available.items() if d["level"] != "عالي"}
            if options:
                gate = min(options.items(), key=lambda x: x[1]["count"])[0]
                level = options[gate]["level"]
                st.success(f"✅ نوصي ببوابة: {gate} (ازدحام {level})")
            else:
                st.warning("⚠️ كل البوابات في منطقتك مزدحمة أو مغلقة.")
        else:
            st.error("❌ رقم التذكرة غير معروف")

    st.subheader("🗺️ خريطة الملاعب")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - ازدحام {data['level']}",
            icon=folium.Icon(
                color="gray" if gate in st.session_state.closed_gates else
                "green" if data["level"] == "خفيف" else
                "orange" if data["level"] == "متوسط" else
                "red")
        ).add_to(m)
    st_folium(m, width=700, height=450)

# Admin Page
elif st.session_state.page == "admin":
    if st.button("↩️ العودة للصفحة الرئيسية"):
        st.session_state.page = "welcome"
        st.experimental_rerun()

    st.title("📊 لوحة تحكم المنظم")
    st.subheader("🚪 حالة البوابات + التحكم")

    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.info(f"بوابة {gate}\nعدد الأشخاص: {data['count']}\nمستوى الازدحام: {data['level']}\nالحالة: {'مغلقة' if gate in st.session_state.closed_gates else 'مفتوحة'}")

            if gate in st.session_state.closed_gates:
                if st.button(f"🔓 فتح بوابة {gate}", key=f"open_{gate}"):
                    st.session_state.closed_gates.remove(gate)
            else:
                if st.button(f"🔒 إغلاق بوابة {gate}", key=f"close_{gate}"):
                    st.session_state.closed_gates.append(gate)

    st.subheader("🚨 تنبيهات الازدحام")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in st.session_state.closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")