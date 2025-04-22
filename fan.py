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

# --- تنسيق بصري ---
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

# --- تحميل نموذج YOLO ---
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

model = YOLO(model_path)

# --- بيانات البوابات ---
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
    "G": {"path": "crowd_system/G/g.png", "lat": 21.6242, "lon": 39.1122, "zone": "غرب"},
}

# --- الحالة الديناميكية للبوابات (إغلاقها من المنظم) ---
closed_gates = st.session_state.get("closed_gates", set())

def get_zone_from_ticket(ticket_id):
    if ticket_id.upper().startswith(("A", "B")):
        return "شمال"
    elif ticket_id.upper().startswith("C"):
        return "شرق"
    elif ticket_id.upper().startswith(("D", "G")):
        return "غرب"
    elif ticket_id.upper().startswith(("E", "F")):
        return "جنوب"
    return None

def get_congestion_level(count):
    if count <= 10:
        return "خفيف", "#A8E6CF"
    elif count <= 30:
        return "متوسط", "#FFD3B6"
    return "عالي", "#FF8B94"

# --- تحليل الصور ---
gate_info = {}
for gate, info in gate_dirs.items():
    if os.path.exists(info["path"]):
        results = model(info["path"])[0]
        count = sum(1 for c in results.boxes.cls if int(c) == 0)
        level, color = get_congestion_level(count)
        gate_info[gate] = {
            "count": count,
            "level": level,
            "color": color,
            "lat": info["lat"],
            "lon": info["lon"],
            "zone": info["zone"],
            "is_closed": gate in closed_gates
        }

# --- تحديد المستخدم ---
user_type = st.sidebar.selectbox("أنا:", ["مشجع", "منظم"])

# ================================
# 🧍‍♂️ واجهة المشجع
# ================================
if user_type == "مشجع":
    st.title("🎉 F.A.N.S - أهلاً بالمشجع")
    st.header("🎫 بياناتك الشخصية")

    col1, col2 = st.columns(2)
    with col1:
        ticket_id = st.text_input("رقم التذكرة", placeholder="مثال: B321")
    with col2:
        confirm = st.checkbox("✅ أؤكد دخولي للملعب")

    if ticket_id:
        zone = get_zone_from_ticket(ticket_id)
        if zone:
            st.success(f"📍 جهة مقعدك حسب التذكرة: {zone}")
            zone_gates = {g: d for g, d in gate_info.items()
                          if d["zone"] == zone and not d["is_closed"]}

            if not zone_gates:
                st.error("🚫 كل البوابات في جهتك مغلقة!")
            else:
                low_congestion = {g: d for g, d in zone_gates.items() if d["level"] != "عالي"}
                if low_congestion:
                    recommended = min(low_congestion.items(), key=lambda x: x[1]["count"])[0]
                    st.info(f"✅ نوصي ببوابة: {recommended} (ازدحام {gate_info[recommended]['level']})")
                else:
                    st.warning("⚠️ كل البوابات مزدحمة حالياً. يرجى انتظار التوجيه.")

                if confirm and gate_info[recommended]['level'] == "عالي":
                    st.warning(f"🚨 بوابتك ({recommended}) مزدحمة حالياً! يُنصح بالتوجه للبوابة الأقل ازدحامًا.")

            # خريطة
            st.subheader("🗺️ خريطة البوابات")
            m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
            for gate, data in gate_info.items():
                color = "gray" if data["is_closed"] else (
                        "green" if data["level"] == "خفيف" else
                        "orange" if data["level"] == "متوسط" else "red")
                folium.Marker(
                    location=[data["lat"], data["lon"]],
                    popup=f"بوابة {gate} - ازدحام {data['level']}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
            st_folium(m, width=700, height=450)
        else:
            st.error("❌ لم نتعرف على جهة التذكرة.")

# ================================
# 🎛️ واجهة المنظم
# ================================
else:
    st.title("📊 لوحة تحكم المنظم")
    st.subheader("🛡️ إدارة البوابات")

    for gate in gate_dirs:
        current = gate in closed_gates
        new_value = st.checkbox(f"🚪 إغلاق بوابة {gate}", value=current, key=f"close_{gate}")
        if new_value:
            closed_gates.add(gate)
        else:
            closed_gates.discard(gate)
    st.session_state["closed_gates"] = closed_gates

    # عرض الحالة
    st.subheader("📦 حالة البوابات")
    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            if data["is_closed"]:
                st.error(f"❌ {gate} - مغلقة")
            else:
                st.info(f"""### بوابة {gate}
👥 {data['count']} شخص
🚦 ازدحام {data['level']}
""")

    # تحليل صورة الشارع/مواقف
    st.subheader("🛣️ تحليل صورة خارجية")
    street_img = st.file_uploader("اختر صورة", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        level, _ = get_congestion_level(person_count + vehicle_count)
        st.success(f"👥 أشخاص: {person_count} | 🚗 سيارات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الخارجي: ازدحام {level}")
