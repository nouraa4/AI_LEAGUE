import streamlit as st
import os
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium

# إعداد الصفحة
st.set_page_config(page_title="F.A.N.S | Crowd Management", page_icon="🎉", layout="centered")

# رأس الصفحة
st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>📣 نظام إدارة الزحام - <span style='color:#117864'>F.A.N.S</span></h1>
    <p style='text-align: center; font-size:18px;'>تحليل الزحام الحي في بوابات الملاعب باستخدام YOLOv8</p>
    <hr style="border:1px solid #bbb">
""", unsafe_allow_html=True)

# تحميل الموديل
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"

if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

model = YOLO(model_path)

# صور البوابات
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 24.7840, "lon": 46.7265},
    "B": {"path": "crowd_system/B/b.png", "lat": 24.7832, "lon": 46.7282},
    "C": {"path": "crowd_system/C/c.png", "lat": 24.7825, "lon": 46.7270},
}

gate_info = {}

st.subheader("🔍 تحليل البوابات")

# تحليل الصور
for gate, info in gate_dirs.items():
    image_path = info["path"]
    if not os.path.exists(image_path):
        st.warning(f"❌ لم يتم العثور على الصورة {image_path}")
        continue

    try:
        results = model(image_path)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)

        # تحديد مستوى الزحام
        if person_count <= 10:
            level = "خفيف"
            color = "green"
        elif person_count <= 30:
            level = "متوسط"
            color = "orange"
        else:
            level = "عالي"
            color = "red"

        gate_info[gate] = {
            "count": person_count,
            "level": level,
            "color": color,
            "lat": info["lat"],
            "lon": info["lon"]
        }

    except Exception as e:
        st.warning(f"❌ خطأ أثناء تحليل الصورة {image_path}: {e}")

# عرض النتائج في بطاقات
cols = st.columns(3)
for i, (gate, data) in enumerate(gate_info.items()):
    with cols[i]:
        st.markdown(f"""
            <div style="border:1px solid #ccc; border-radius:12px; padding:16px; background-color:#f9f9f9; text-align:center;">
                <h3 style="color:#2E86C1;">🅰️ بوابة {gate}</h3>
                <p style="font-size:18px;">👥 <strong>{data['count']}</strong> شخص</p>
                <p style="font-size:16px;">🚦 <span style="color:{data['color']};"><strong>{data['level']}</strong></span></p>
            </div>
        """, unsafe_allow_html=True)

# الخريطة
st.subheader("🗺️ الخريطة التفاعلية")

map_center = [24.7838, 46.7270]
m = folium.Map(location=map_center, zoom_start=17)

for gate, data in gate_info.items():
    folium.Marker(
        location=[data["lat"], data["lon"]],
        popup=f"بوابة {gate} - {data['level']}",
        icon=folium.Icon(color=data["color"])
    ).add_to(m)

st_folium(m, width=700, height=450)

# التوصية
if gate_info:
    recommended = min(gate_info.items(), key=lambda x: x[1]['count'])[0]
    st.markdown(f"""
        <div style="background-color:#dff0d8; padding:15px; border-radius:10px; text-align:center;">
            ✅ نوصي بالتوجه إلى <strong>بوابة {recommended}</strong> لكونها الأقل ازدحامًا.
        </div>
    """, unsafe_allow_html=True)
