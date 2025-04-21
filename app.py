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

# تنسيق بصري جذاب
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

# تحميل نموذج YOLO
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

model = YOLO(model_path)

# بوابات ملعب الجوهرة
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
    "G": {"path": "crowd_system/G/g.png", "lat": 21.6242, "lon": 39.1122, "zone": "غرب"},
}

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

# تحليل صور البوابات
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
            "zone": info["zone"]
        }

# اختيار نوع المستخدم
user_type = st.sidebar.selectbox("أنا:", ["مشجع", "منظم"])

# واجهة المشجع
if user_type == "مشجع":
    st.title("🏟️ F.A.N.S - الملعب الذكي للمشجعين")

    st.header("🎫 توصية حسب تذكرتك")
    ticket_id = st.text_input("أدخل رقم تذكرتك (مثال: A123)")

    if ticket_id:
        zone = get_zone_from_ticket(ticket_id)
        if zone:
            st.info(f"📍 جهة مقعدك حسب التذكرة: {zone}")
            zone_gates = {g: d for g, d in gate_info.items() if d["zone"] == zone}

            if zone_gates:
                filtered = {g: d for g, d in zone_gates.items() if d["level"] != "عالي"}

                if filtered:
                    recommended_gate = min(filtered.items(), key=lambda x: x[1]["count"])[0]
                    level_name = f"ازدحام {filtered[recommended_gate]['level']}"
                    st.success(f"✅ نوصي بالتوجه إلى بوابة: {recommended_gate} ({level_name})")
                else:
                    st.warning("⚠️ جميع البوابات في هذه الجهة مزدحمة حالياً. يُنصح بالانتظار أو التواصل مع منظم.")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حالياً في هذه الجهة.")
        else:
            st.error("❌ رقم تذكرة غير معروف")

    st.subheader("🗺️ خريطة الملاعب")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - ازدحام {data['level']}",
            icon=folium.Icon(color="green" if data["level"] == "خفيف"
                             else "orange" if data["level"] == "متوسط"
                             else "red")
        ).add_to(m)
    st_folium(m, width=700, height=450)

# واجهة المنظم
else:
    st.title("📊 لوحة تحكم المنظم")

    st.subheader(" بيانات البوابات")
    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.info(f"""### بوابة {gate}
👥 عدد الأشخاص: {data['count']}
🚦 مستوى الازدحام: ازدحام {data['level']}
""")

    st.subheader("🚨 تنبيهات")
    for gate, data in gate_info.items():
        if data['level'] == "عالي":
            st.error(f"🔴 ازدحام عالي عند بوابة {gate}!")

    st.subheader("🛣️ تحليل الشوارع / المواقف")
    street_img = st.file_uploader("ارفع صورة", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level, _ = get_congestion_level(total)
        st.success(f"👥 أشخاص: {person_count} | 🚗 مركبات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الإجمالي: ازدحام {level}")
