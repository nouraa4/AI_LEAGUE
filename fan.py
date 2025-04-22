import streamlit as st
import os
import cv2
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تنسيق بصري
st.markdown("""
    <style>
    body { background-color: #1c1c1c; color: white; }
    h1, h2, h3, h4 { color: #ECECEC; font-weight: bold; }
    .stButton>button { background-color: #A8E6CF; color: black; border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input {
        background-color: #2c2c2c;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# تحميل النموذج
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

model = YOLO(model_path)

# بيانات البوابات
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
    "G": {"path": "crowd_system/G/g.png", "lat": 21.6242, "lon": 39.1122, "zone": "غرب"},
}

# تحليل صور البوابات
gate_info = {}
for gate, info in gate_dirs.items():
    if os.path.exists(info["path"]):
        results = model(info["path"])[0]
        count = sum(1 for c in results.boxes.cls if int(c) == 0)
        level, color = (
            ("خفيف", "#A8E6CF") if count <= 10 else
            ("متوسط", "#FFD3B6") if count <= 30 else
            ("عالي", "#FF8B94")
        )
        gate_info[gate] = {
            "count": count,
            "level": level,
            "color": color,
            "lat": info["lat"],
            "lon": info["lon"],
            "zone": info["zone"]
        }

# إدارة الحالة
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "closed_gates" not in st.session_state:
    st.session_state.closed_gates = []

# الصفحة الترحيبية
if st.session_state.page == "welcome":
    st.title("مرحبًا بك في نظام F.A.N.S")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("أنا مشجع"):
            st.session_state.page = "fan"
    with col2:
        if st.button("أنا منظم"):
            st.session_state.page = "admin"

# واجهة المشجع
elif st.session_state.page == "fan":
    st.title("🏟️ F.A.N.S - المشجع")

    # محاكاة بيانات التذكرة
    user_ticket = "C123"  # يتم جلبه تلقائيًا من قاعدة البيانات
    ticket_zone = gate_dirs[user_ticket[0]]["zone"]
    st.info(f"🎫 تذكرتك مرتبطة بجهة: {ticket_zone}")

    available_gates = {g: d for g, d in gate_info.items()
                       if d["zone"] == ticket_zone and g not in st.session_state.closed_gates}

    low_congestion_gates = {g: d for g, d in available_gates.items()
                            if d["level"] != "عالي"}

    if not available_gates:
        st.error("❌ جميع البوابات مغلقة في جهتك، تواصل مع منظم.")
    elif not low_congestion_gates:
        st.warning("⚠️ كل البوابات مزدحمة حالياً، يُنصح بالانتظار أو التواصل مع منظم.")
    else:
        recommended_gate = min(low_congestion_gates.items(), key=lambda x: x[1]["count"])[0]
        level = gate_info[recommended_gate]["level"]
        st.success(f"✅ أقرب بوابة مفضلة هي: {recommended_gate} (ازدحام {level})")

    # الخريطة
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

# واجهة المنظم
elif st.session_state.page == "admin":
    st.title("📊 لوحة تحكم المنظم")

    # إغلاق البوابات
    st.subheader("🚪 إدارة البوابات")
    for gate in gate_info.keys():
        if st.checkbox(f"إغلاق بوابة {gate}", value=gate in st.session_state.closed_gates):
            if gate not in st.session_state.closed_gates:
                st.session_state.closed_gates.append(gate)
        else:
            if gate in st.session_state.closed_gates:
                st.session_state.closed_gates.remove(gate)

    # عرض حالة البوابات
    st.subheader("👁️‍🗨️ حالة البوابات")
    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.info(f"""### بوابة {gate}
👥 عدد الأشخاص: {data['count']}
🚦 مستوى الازدحام: {data['level']}
🔒 الحالة: {"مغلقة" if gate in st.session_state.closed_gates else "مفتوحة"}
""")

    # تنبيهات الزحمة
    st.subheader("🚨 تنبيهات ازدحام")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in st.session_state.closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")

    # تحليل الصور
    st.subheader("📸 تحليل الزحام في الشوارع")
    street_img = st.file_uploader("ارفع صورة", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level, _ = (
            ("خفيف", "#A8E6CF") if total <= 10 else
            ("متوسط", "#FFD3B6") if total <= 30 else
            ("عالي", "#FF8B94")
        )
        st.success(f"👥 أشخاص: {person_count} | 🚗 مركبات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الإجمالي: ازدحام {level}")