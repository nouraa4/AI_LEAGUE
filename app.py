import streamlit as st
import os
import cv2
import folium
import gdown
import numpy as np
from ultralytics import YOLO
from streamlit_folium import st_folium

# رابط Google Drive لتحميل النموذج
model_url = "https://drive.google.com/file/d/1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
model_path = "best_Model.pt"  # المسار الذي سيتم تحميل النموذج فيه
# تحميل النموذج إذا ما كان موجود
if not os.path.exists(model_path):
    with st.spinner("📥 جاري تحميل نموذج YOLO..."):
        # تحميل الملف من Google Drive
        gdown.download(model_url, model_path, quiet=False)
        st.success("✅ تم تحميل النموذج!")

# تحقق من أن الملف صحيح (أن يكون .pt وليس مجلد)
if os.path.isdir(model_path):
    st.error(f"❌ خطأ: {model_path} هو مجلد، يجب أن يكون الملف نموذج .pt وليس مجلدًا.")
else:
    try:
        # تحميل النموذج من المسار
        model = YOLO(model_path)
        st.success("✅ تم تحميل النموذج بنجاح!")

        # اختبار النموذج على صورة (تأكد من وجود الصورة في المسار الصحيح)
        image_path = "crowd_system/A/a.png"  # تأكد من وجود الصورة في المسار الصحيح
        results = model(image_path)

        # عرض النتائج
        st.image(image_path, caption="الصورة المدخلة")
        st.write(results.pandas().xywh)  # عرض النتائج
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تحميل النموذج: {e}")



# تحميل النموذج
model = YOLO(model_path)

# إعداد مسارات البوابات
gate_dirs = {
    "A": {"path": "crowd_system/A/a.png", "lat": 24.7840, "lon": 46.7265},
    "B": {"path": "crowd_system/B/b.png", "lat": 24.7832, "lon": 46.7282},
    "C": {"path": "crowd_system/C/c.png", "lat": 24.7825, "lon": 46.7270},
}

st.title("تحليل الزحام عند بوابات الملاعب باستخدام YOLOv8")

gate_info = {}

# تحليل صورة من كل بوابة
for gate, info in gate_dirs.items():
    image_path = info["path"]
    
    # التحقق من وجود الصورة
    if not os.path.exists(image_path):
        st.warning(f"❌ لم يتم العثور على الصورة {image_path}")
        continue

    # اختبار إذا كانت الصورة موجودة، ثم تمريرها للنموذج
    try:
        # النتائج من النموذج
        results = model(image_path)[0]
        
        # حساب عدد الأشخاص (class = 0)
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)

        # تحديد مستوى الزحام بناءً على عدد الأشخاص
        if person_count <= 10:
            level = "خفيف"
            color = "green"
        elif person_count <= 30:
            level = "متوسط"
            color = "orange"
        else:
            level = "عالي"
            color = "red"

        # تخزين المعلومات المتعلقة بالبوابة
        gate_info[gate] = {
            "count": person_count,
            "level": level,
            "color": color,
            "lat": info["lat"],
            "lon": info["lon"]
        }

    except Exception as e:
        st.warning(f"❌ حدث خطأ أثناء تحليل الصورة {image_path}: {e}")
        continue

# عرض النتائج
for gate, data in gate_info.items():
    st.write(f"🅰️ بوابة {gate}")
    st.write(f"👥 عدد الأشخاص: {data['count']}")
    st.write(f"🚦 مستوى الزحام: {data['level']}")
    st.markdown("---")

# رسم الخريطة
st.subheader("📍 خريطة البوابات")
m = folium.Map(location=[24.7838, 46.7270], zoom_start=17)

for gate, data in gate_info.items():
    folium.Marker(
        location=[data["lat"], data["lon"]],
        popup=f"بوابة {gate} - {data['level']}",
        icon=folium.Icon(color=data["color"])
    ).add_to(m)

st_folium(m, width=700, height=450)

# التوصية
if gate_info:
    least_gate = min(gate_info.items(), key=lambda x: x[1]['count'])[0]
    st.success(f"✅ نوصي بالتوجه إلى البوابة: {least_gate}")
