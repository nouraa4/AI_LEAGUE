import streamlit as st
import os
import cv2
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

# إعداد الواجهة
st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تنسيق جذاب مع دارك مود
st.markdown("""
    <style>
    body { background-color: #1c1c1c; color: white; }
    h1, h2, h3, h4 { color: #ECECEC; font-weight: bold; }
    .stButton>button { background-color: #A8E6CF; color: black; border-radius: 8px; font-weight: bold; }
    .block-container { padding-top: 2rem; }
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

# بيانات بوابات ملعب الجوهرة بالحروف
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 21.6225, "lon": 39.1105, "zone": "شمال"},
    "B": {"path": "crowd_system/B/b.png", "lat": 21.6230, "lon": 39.1110, "zone": "شمال"},
    "C": {"path": "crowd_system/C/c.png", "lat": 21.6235, "lon": 39.1115, "zone": "شرق"},
    "D": {"path": "crowd_system/D/d.png", "lat": 21.6240, "lon": 39.1120, "zone": "غرب"},
    "E": {"path": "crowd_system/E/e.png", "lat": 21.6245, "lon": 39.1125, "zone": "جنوب"},
    "F": {"path": "crowd_system/F/f.png", "lat": 21.6250, "lon": 39.1130, "zone": "جنوب"},
}

def get_zone_from_ticket(ticket_id):
    if ticket_id.upper().startswith("A") or ticket_id.upper().startswith("B"):
        return "شمال"
    elif ticket_id.upper().startswith("C"):
        return "شرق"
    elif ticket_id.upper().startswith("D"):
        return "غرب"
    elif ticket_id.upper().startswith("E") or ticket_id.upper().startswith("F"):
        return "جنوب"
    else:
        return None

def get_congestion_level(count):
    if count <= 10:
        return "خفيف", "#A8E6CF"
    elif count <= 30:
        return "متوسط", "#FFD3B6"
    else:
        return "عالي", "#FF8B94"

# تحليل صور البوابات
gate_info = {}
for gate, info in gate_dirs.items():
    image_path = info["path"]
    if os.path.exists(image_path):
        results = model(image_path)[0]
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

# ----------------------------
# واجهة المشجع
# ----------------------------
if user_type == "مشجع":
    st.title("F.A.N.S - ملعب ذكي يشتغل معك")
    st.markdown("**حلّ ذكي يسهّل دخولك ويوجهك لأفضل بوابة بحسب الزحام وموقعك!**")

    st.header("🎫 توصية حسب تذكرتك")
    ticket_id = st.text_input("أدخل رقم تذكرتك (مثال: A123)")

    if ticket_id:
        zone = get_zone_from_ticket(ticket_id)
        if zone:
            st.info(f"📍 جهة مقعدك حسب التذكرة: {zone}")
            zone_gates = {g: d for g, d in gate_info.items() if d["zone"] == zone}
            if zone_gates:
                recommended_gate = min(zone_gates.items(), key=lambda x: x[1]["count"])[0]
                st.success(f"✅ نوصي بالتوجه إلى بوابة: {recommended_gate} ({gate_info[recommended_gate]['level']})")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حالياً في هذه الجهة.")
        else:
            st.error("❌ رقم تذكرة غير معروف")

    st.subheader("🗺️ خريطة الملاعب (بواباتك على الخريطة)")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - {data['level']}",
            icon=folium.Icon(color="green" if data["level"] == "خفيف"
                             else "orange" if data["level"] == "متوسط"
                             else "red")
        ).add_to(m)
    st_folium(m, width=700, height=450)

# ----------------------------
# واجهة المنظم
# ----------------------------
else:
    st.title("لوحة المنظم")
    st.markdown("**مراقبة مباشرة لحالة البوابات وتنبيهات فورية.**")

    for gate, data in gate_info.items():
        st.markdown(f"""
        ### بوابة {gate}
        - 👥 عدد الأشخاص: {data['count']}
        - 🚦 مستوى الزحام: `{data['level']}`
        """)

    st.subheader("🚨 تنبيهات الزحام العالي")
    for gate, data in gate_info.items():
        if data['level'] == "عالي":
            st.error(f"🔴 ازدحام عالي عند بوابة {gate}!")

    st.subheader("📸 تحليل الشوارع أو المواقف")
    street_img = st.file_uploader("ارفع صورة للمحيط الخارجي", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level, _ = get_congestion_level(total)
        st.success(f"👥 أشخاص: {person_count} | 🚗 مركبات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الإجمالي: {level}")