import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
import folium
from streamlit_folium import st_folium

# تحميل نموذج الـ CNN
model = tf.keras.models.load_model("cnn_congestion_model.h5")
class_names = ['خفيف', 'متوسط', 'عالي']

st.title("📸 تحليل مستوى الازدحام في الصورة")

# تحميل صورة
uploaded_file = st.file_uploader("اختر صورة من التجمع", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).resize((128, 128))
    st.image(image, caption="📷 الصورة المدخلة", use_column_width=True)

    # تجهيز الصورة للنموذج
    img_array = np.array(image) / 255.0
    img_array = img_array.reshape(1, 128, 128, 3)

    # التنبؤ
    prediction = model.predict(img_array)
    congestion = class_names[np.argmax(prediction)]

    st.subheader(f"🚦 مستوى الازدحام: **{congestion}**")

    # خريطة تفاعلية
    st.subheader("📍 البوابات المتاحة:")

    # مثال لبوابات في استاد الملك فهد (أرقام وهمية كمثال)
    gates = {
        "البوابة A": {"lat": 24.7840, "lon": 46.7265, "level": "خفيف"},
        "البوابة B": {"lat": 24.7832, "lon": 46.7282, "level": "عالي"},
        "البوابة C": {"lat": 24.7825, "lon": 46.7270, "level": "متوسط"},
    }

    # إنشاء الخريطة
    m = folium.Map(location=[24.7838, 46.7270], zoom_start=17)
    color_map = {"خفيف": "green", "متوسط": "orange", "عالي": "red"}

    for name, info in gates.items():
        folium.Marker(
            location=[info["lat"], info["lon"]],
            popup=f"{name} - {info['level']}",
            icon=folium.Icon(color=color_map[info["level"]])
        ).add_to(m)

    # عرض الخريطة في ستريملت
    st_data = st_folium(m, width=700, height=450)

    # توصية تلقائية
    recommended_gate = next((g for g, v in gates.items() if v['level'] == 'خفيف'), None)
    if recommended_gate:
        st.success(f"✅ نوصي بالتوجه إلى: {recommended_gate}")
    else:
        st.warning("⚠️ جميع البوابات مزدحمة حالياً.")
