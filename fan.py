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

# تنسيقات CSS مع صورة بانر
st.markdown("""
    <style>
    body { background-color: #1c1c1c; color: white; }
    h1, h2, h3, h4 { color: #ECECEC; font-weight: bold; }
    .stButton>button {
        background-color: #A8E6CF;
        color: black;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #9370DB;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #2c2c2c;
        color: white;
        border-radius: 8px;
    }
    .banner-container {
        position: relative;
        width: 100%;
        height: 250px;
        overflow: hidden;
        border-radius: 12px;
        margin-bottom: 30px;
    }
    .banner-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.5);
    }
    .banner-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 6px #000;
    }
    </style>

    <div class="banner-container">
        <img src="welcome.png">
        <div class="banner-text">F.A.N.S - ملعب ذكي لمشجع ذكي</div>
    </div>
""", unsafe_allow_html=True)

# تحميل نموذج YOLO
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
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

# تحليل الزحام
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

# حالة البوابات المغلقة
closed_gates = st.session_state.get("closed_gates", [])

# تحديد نوع المستخدم
user_type = st.sidebar.radio("أنا:", ["مشجع", "منظم"])

# ------------------- صفحة المشجع -------------------
if user_type == "مشجع":
    st.title("🏟️ F.A.N.S - منصة المشجع الذكي")

    st.subheader("معلومات المستخدم")
    with st.form("user_info_form"):
        name = st.text_input("الاسم الكامل")
        ticket = st.text_input("🎟️ رقم التذكرة (مثال: A123)")
        confirm = st.form_submit_button("✅ تأكيد الدخول")
        if confirm and ticket:
            st.success(f"تم تأكيد دخولك{'، ' + name if name else ''} بتذكرتك رقم {ticket}")

    if ticket:
        zone = gate_dirs.get(ticket[0].upper(), {}).get("zone")
        if zone:
            st.info(f"📍 جهة مقعدك: {zone}")
            available = {
                g: d for g, d in gate_info.items()
                if d["zone"] == zone and g not in closed_gates
            }
            filtered = {g: d for g, d in available.items() if d["level"] != "عالي"}

            if filtered:
                best_gate = min(filtered.items(), key=lambda x: x[1]["count"])[0]
                level = filtered[best_gate]["level"]
                st.success(f"✅ نوصي بالتوجه إلى بوابة: {best_gate} ({level})")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حاليًا في هذه الجهة أو جميعها مغلقة/مزدحمة.")
        else:
            st.error("❌ رقم التذكرة غير معروف")

    st.subheader("🗺️ خريطة البوابات")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - {data['level']}" + (" (مغلقة)" if gate in closed_gates else ""),
            icon=folium.Icon(
                color="gray" if gate in closed_gates else
                "green" if data["level"] == "خفيف" else
                "orange" if data["level"] == "متوسط" else "red"
            )
        ).add_to(m)
    st_folium(m, width=700, height=450)

# ------------------- صفحة المنظم -------------------
elif user_type == "منظم":
    st.title("📊 لوحة تحكم المنظم")
    st.subheader("🕹️ إدارة وتحكم البوابات")

    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.markdown(f"""### بوابة {gate}
- 👥 عدد الأشخاص: `{data['count']}`
- 🚦 مستوى الزحام: `{data['level']}`
- 📌 الحالة: `{'مغلقة' if gate in closed_gates else 'مفتوحة'}`""")

            if gate in closed_gates:
                if st.button(f"🔓 فتح بوابة {gate}", key=f"open_{gate}"):
                    closed_gates.remove(gate)
            else:
                if st.button(f"🔒 إغلاق بوابة {gate}", key=f"close_{gate}"):
                    closed_gates.append(gate)

    st.session_state.closed_gates = closed_gates

    st.subheader("🚨 تنبيهات الازدحام")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")

