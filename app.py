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

# تنسيق دارك مود
st.markdown("""
    <style>
    body { background-color: #1c1c1c; color: #ffffff; }
    h1, h2, h3, h4 { color: #ECECEC; }
    .stButton>button { background-color: #444; color: white; border-radius: 8px; }
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

# بيانات البوابات
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 24.7840, "lon": 46.7265, "zone": "شرق"},
    "B": {"path": "crowd_system/B/b.png", "lat": 24.7832, "lon": 46.7282, "zone": "غرب"},
    "C": {"path": "crowd_system/C/c.png", "lat": 24.7825, "lon": 46.7270, "zone": "شمال"},
    "D": {"path": "crowd_system/D/d.png", "lat": 24.7835, "lon": 46.7255, "zone": "جنوب"},
}

# استخراج الجهة من رقم التذكرة
def get_zone_from_ticket(ticket_id):
    if ticket_id.upper().startswith("A"): return "شرق"
    elif ticket_id.upper().startswith("B"): return "غرب"
    elif ticket_id.upper().startswith("C"): return "شمال"
    elif ticket_id.upper().startswith("D"): return "جنوب"
    else: return None

# تصنيف الزحام
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

# تحليل صور البوابات
gate_info = {}
recommendation_log = []

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

# مشجع
if user_type == "مشجع":
    st.header("🎫 توصية حسب تذكرتك")
    ticket_id = st.text_input("أدخل رقم تذكرتك (مثال: A123)")
    if ticket_id:
        zone = get_zone_from_ticket(ticket_id)
        if zone:
            st.info(f"📍 جهة مقعدك حسب التذكرة: {zone}")
            zone_gates = {g: d for g, d in gate_info.items() if gate_dirs[g]["zone"] == zone}
            if zone_gates:
                recommended_gate = min(zone_gates.items(), key=lambda x: x[1]["count"])[0]
                st.success(f"✅ نوصي بالتوجه إلى بوابة: {recommended_gate} ({gate_info[recommended_gate]['level']})")
                recommendation_log.append(f"تذكرة {ticket_id} → بوابة {recommended_gate}")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حاليًا في هذه الجهة. يُرجى التواصل مع منظم.")
        else:
            st.error("❌ رقم تذكرة غير معروف")
            

    
# عنوان
st.subheader("📍 خريطة البوابات")

# بيانات البوابات حسب ملعب الجوهرة
gate_info = {
    "A1": {"lat": 21.5721, "lon": 39.2395, "level": "متوسط"},
    "A2": {"lat": 21.5724, "lon": 39.2402, "level": "خفيف"},
    "B1": {"lat": 21.5730, "lon": 39.2410, "level": "عالي"},
    "B2": {"lat": 21.5733, "lon": 39.2418, "level": "خفيف"},
    "C1": {"lat": 21.5740, "lon": 39.2425, "level": "متوسط"},
    "C2": {"lat": 21.5743, "lon": 39.2431, "level": "عالي"},
    "D1": {"lat": 21.5736, "lon": 39.2389, "level": "خفيف"},
    "D2": {"lat": 21.5731, "lon": 39.2382, "level": "خفيف"},
}

# إنشاء الخريطة
m = folium.Map(location=[21.5730, 39.2410], zoom_start=17)

# إضافة العلامات حسب مستوى الازدحام
for gate, data in gate_info.items():
    folium.Marker(
        location=[data["lat"], data["lon"]],
        popup=f"بوابة {gate} - {data['level']}",
        icon=folium.Icon(color="green" if data["level"] == "خفيف"
                         else "orange" if data["level"] == "متوسط"
                         else "red")
    ).add_to(m)

# عرض الخريطة في Streamlit
st_folium(m, width=700, height=450)


# منظم
else:
    st.header("📊 لوحة تحكم المنظم")

    # خريطة
    st.subheader("📍 خريطة البوابات")
    m = folium.Map(location=[24.7838, 46.7270], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - {data['level']}",
            icon=folium.Icon(color="green" if data["level"] == "خفيف" else
                             "orange" if data["level"] == "متوسط" else "red")
        ).add_to(m)
    st_folium(m, width=700, height=450)

    # بيانات البوابات
    for gate, data in gate_info.items():
        st.markdown(f"""
        ### بوابة {gate}
        - 👥 عدد الأشخاص: {data['count']}
        - 🚦 مستوى الزحام: `{data['level']}`
        """)

    # تنبيهات
    st.subheader("🚨 تنبيهات")
    for gate, data in gate_info.items():
        if data['level'] == "عالي":
            st.error(f"🔴 ازدحام عالي عند بوابة {gate}!")

    # التوصيات السابقة
    st.subheader("🗂️ التوصيات الصادرة للمشجعين")
    if recommendation_log:
        for log in recommendation_log:
            st.markdown(f"• {log}")
    else:
        st.info("لا توجد توصيات حالياً.")

    # تحليل خارجي (شوارع / مواقف)
    st.subheader("🛣️ تحليل صورة خارجية (زحام الشوارع أو المواقف)")
    street_img = st.file_uploader("حمّل صورة", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level, color = get_congestion_level(total)
        st.success(f"👥 أشخاص: {person_count} | 🚗 سيارات: {vehicle_count} → 🚦 الزحام: {level}")