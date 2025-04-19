import streamlit as st
import os
import cv2
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تنسيق الواجهة (CSS)
st.markdown("""
    <style>
    body {
        background-color: #1c1c1c;
        color: #ffffff;
    }
    .main {
        background-image: url("https://i.imgur.com/Fdt2u6s.jpg");
        background-size: cover;
        background-position: center;
    }
    h1, h2, h3, h4 {
        color: #ECECEC;
    }
    </style>
""", unsafe_allow_html=True)

# تحميل النموذج
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"

if not os.path.exists(model_path):
    with st.spinner("📥 تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

model = YOLO(model_path)

# خريطة البوابات ومواقعها وجهاتها
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 24.7840, "lon": 46.7265, "zone": "شرق"},
    "B": {"path": "crowd_system/B/b.png", "lat": 24.7832, "lon": 46.7282, "zone": "غرب"},
    "C": {"path": "crowd_system/C/c.png", "lat": 24.7825, "lon": 46.7270, "zone": "شرق"},
}

# استخراج الزون من رقم التذكرة
def get_zone_from_ticket(ticket_id):
    if ticket_id.upper().startswith("A"):
        return "شرق"
    elif ticket_id.upper().startswith("B"):
        return "غرب"
    elif ticket_id.upper().startswith("C"):
        return "شمال"
    elif ticket_id.upper().startswith("D"):
        return "جنوب"
    else:
        return None

# توصيف مستوى الزحام حسب عدد الأشخاص
def get_congestion_level(count):
    if count <= 10:
        return "خفيف", "#A8E6CF"
    elif count <= 30:
        return "متوسط", "#FFD3B6"
    else:
        return "عالي", "#FF8B94"

st.title("⚽ F.A.N.S - نظام ذكي لتحليل الزحام في الملاعب")

# اختيار نوع المستخدم
user_type = st.sidebar.selectbox("أنا:", ["مشجع", "منظم"])

# تحليل الزحام عند البوابات
gate_info = {}
for gate, info in gate_dirs.items():
    image_path = info["path"]
    if not os.path.exists(image_path):
        continue
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

# واجهة المشجع
if user_type == "مشجع":
    st.header("🎫 توصية مخصصة حسب تذكرتك")
    ticket_id = st.text_input("أدخل رقم التذكرة (مثلاً: A123)")
    if ticket_id:
        zone = get_zone_from_ticket(ticket_id)
        if zone:
            st.info(f"📍 جهة مقعدك (حسب التذكرة): {zone}")
            zone_gates = {g: d for g, d in gate_info.items() if gate_dirs[g]["zone"] == zone}
            if zone_gates:
                recommended_gate = min(zone_gates.items(), key=lambda x: x[1]["count"])[0]
                st.success(f"✅ نوصي ببوابة: {recommended_gate} ({gate_info[recommended_gate]['level']})")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حالياً في هذه الجهة.")
        else:
            st.error("❌ رقم التذكرة غير معروف")
    
# واجهة المنظم
else:
    st.header("📊 لوحة تحكم المنظم")
    for gate, data in gate_info.items():
        st.markdown(f"""
        ### بوابة {gate}
        - 👥 عدد الأشخاص: {data['count']}
        - 🚦 مستوى الزحام: `{data['level']}`
        """)
        st.markdown("---")

    # خريطة البوابات
    st.subheader("📍 خريطة تفاعلية للبوابات")
    m = folium.Map(location=[24.7838, 46.7270], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - {data['level']}",
            icon=folium.Icon(color="green" if data["level"] == "خفيف" else
                             "orange" if data["level"] == "متوسط" else "red")
        ).add_to(m)
    st_folium(m, width=700, height=450)

    st.subheader("🛣️ تحليل الزحام خارج الملعب (المواقف / الشوارع)")
    street_img = st.file_uploader("حمّل صورة من الشارع أو المواقف", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        car_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        st.success(f"👥 أشخاص: {person_count} | 🚗 سيارات: {car_count}")