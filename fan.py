import streamlit as st
import os
import gdown
import numpy as np
import folium
from PIL import Image
from ultralytics import YOLO
from streamlit_folium import st_folium

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تنسيق CSS
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
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #2c2c2c;
        color: white;
        border-radius: 8px;
    }
    </style>
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

# تحليل الصور وتحديد مستوى الزحام
gate_info = {}
for gate, info in gate_dirs.items():
    if os.path.exists(info["path"]):
        results = model(info["path"])[0]
        count = sum(1 for c in results.boxes.cls if int(c) == 0)
        if count <= 10:
            level = "خفيف"
        elif count <= 30:
            level = "متوسط"
        else:
            level = "عالي"
        gate_info[gate] = {
            "count": count,
            "level": level,
            "lat": info["lat"],
            "lon": info["lon"],
            "zone": info["zone"]
        }

# بوابات مغلقة (يدويًا من المنظم)
if "closed_gates" not in st.session_state:
    st.session_state.closed_gates = []

# اختيار نوع المستخدم
user_type = st.sidebar.radio("أنا:", ["مشجع", "منظم"])

# ---------------- صفحة المشجع ----------------
if user_type == "مشجع":
    st.title("🎫 مشجع - توصية البوابة")
    
    name = st.text_input("👤 اسمك")
    ticket = st.text_input("🎟️ رقم التذكرة (مثال: A123)")
    
    if ticket:
        gate_letter = ticket[0].upper()
        zone = gate_dirs.get(gate_letter, {}).get("zone")
        
        if zone:
            st.info(f"📍 جهة المقعد (حسب التذكرة): {zone}")
            available = {
                g: d for g, d in gate_info.items()
                if d["zone"] == zone and g not in st.session_state.closed_gates
            }
            not_heavy = {g: d for g, d in available.items() if d["level"] != "عالي"}

            if not_heavy:
                best_gate = min(not_heavy.items(), key=lambda x: x[1]["count"])[0]
                level = not_heavy[best_gate]["level"]
                st.success(f"✅ نوصي بالتوجه إلى بوابة: {best_gate} ( {level} )")
            elif available:
                congested_gate = min(available.items(), key=lambda x: x[1]["count"])[0]
                st.warning(f"⚠️ بوابتك الحالية مزدحمة، أقرب خيار هو {congested_gate}")
            else:
                st.error("❌ لا توجد بوابات متاحة حاليًا في هذه الجهة.")
        else:
            st.error("❌ رقم تذكرة غير معروف.")

    st.subheader("🗺️ خريطة البوابات")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - {data['level']}" + (" (مغلقة)" if gate in st.session_state.closed_gates else ""),
            icon=folium.Icon(
                color="gray" if gate in st.session_state.closed_gates else
                "green" if data["level"] == "خفيف" else
                "orange" if data["level"] == "متوسط" else "red"
            )
        ).add_to(m)
    st_folium(m, use_container_width=True)

# ---------------- صفحة المنظم ----------------
else:
    st.title("📊 لوحة تحكم المنظم")
    st.subheader("🕹️ التحكم في البوابات")

    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.markdown(f"""### بوابة {gate}
- 👥 عدد الأشخاص: `{data['count']}`
- 🚦 الزحام: `{data['level']}`
- 📌 الحالة: `{"مغلقة" if gate in st.session_state.closed_gates else "مفتوحة"}`""")
            
            if gate in st.session_state.closed_gates:
                if st.button(f"🔓 فتح بوابة {gate}", key=f"open_{gate}"):
                    st.session_state.closed_gates.remove(gate)
            else:
                if st.button(f"🔒 إغلاق بوابة {gate}", key=f"close_{gate}"):
                    st.session_state.closed_gates.append(gate)

    st.subheader("🚨 تنبيهات")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in st.session_state.closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")

