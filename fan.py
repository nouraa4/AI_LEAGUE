import streamlit as st
import os
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image

st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# تنسيق ستايل
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
        background-color: #DDA0DD; /* mauve */
        color: black;
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

# تحليل الصور
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

# إغلاق البوابات يدويًا من المنظم
closed_gates = st.session_state.get("closed_gates", [])

# نوع المستخدم
user_type = st.sidebar.radio("أنا:", ["مشجع", "منظم"])

# ------------------- واجهة المشجع -------------------
if user_type == "مشجع":
    st.title("🎫 بيانات المشجع")
    with st.form("fan_form"):
        name = st.text_input("👤 الاسم الكامل")
        ticket = st.text_input("🎟️ رقم التذكرة (مثال: B123)")
        submitted = st.form_submit_button("تأكيد الدخول")

    if submitted and ticket:
        zone = gate_dirs.get(ticket[0].upper(), {}).get("zone")
        if zone:
            st.success(f"✅ تم تسجيل دخولك بنجاح يا {name}!")
            st.info(f"📍 جهة مقعدك: {zone}")
            zone_gates = {
                g: d for g, d in gate_info.items()
                if d["zone"] == zone and g not in closed_gates
            }
            # البحث عن بوابة خفيفة أو متوسطة
            recommended = {g: d for g, d in zone_gates.items() if d["level"] != "عالي"}
            if recommended:
                best_gate = min(recommended.items(), key=lambda x: x[1]["count"])[0]
                st.success(f"🎯 تم تخصيص بوابة: {best_gate} ({recommended[best_gate]['level']})")
                if gate_info[best_gate]["level"] == "عالي":
                    st.warning(f"⚠️ تنبيه: ازدحام مرتفع في بوابتك {best_gate}. سيتم إشعارك عند توفر بوابة بديلة.")
            else:
                st.warning("⚠️ لا توجد بوابات خفيفة متاحة حالياً في هذه الجهة.")
        else:
            st.error("❌ رقم التذكرة غير معروف أو غير مدعوم.")

    st.subheader("🗺️ خريطة البوابات")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],popup=f"بوابة {gate} - ازدحام {data['level']}" + (" (مغلقة)" if gate in closed_gates else ""),
            icon=folium.Icon(
                color="gray" if gate in closed_gates else
                "green" if data["level"] == "خفيف" else
                "orange" if data["level"] == "متوسط" else "red"
            )
        ).add_to(m)
    st_folium(m, width=700, height=450)

# ------------------- واجهة المنظم -------------------
elif user_type == "منظم":
    st.title("📊 لوحة تحكم المنظم")

    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.markdown(f"""### بوابة {gate}
- 👥 الأشخاص: {data['count']}
- 🚦 الزحام: ازدحام {data['level']}
- 🔐 الحالة: `{'مغلقة' if gate in closed_gates else 'مفتوحة'}`""")
            if gate in closed_gates:
                if st.button(f"🔓 فتح بوابة {gate}", key=f"open_{gate}"):
                    closed_gates.remove(gate)
            else:
                if st.button(f"🔒 إغلاق بوابة {gate}", key=f"close_{gate}"):
                    closed_gates.append(gate)
    st.session_state.closed_gates = closed_gates

    st.subheader("🚨 تنبيهات")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in closed_gates:
            st.error(f"⚠️ ازدحام مرتفع عند بوابة {gate}")

    st.subheader("🛣️ تحليل صورة للشوارع/المواقف")
    street_img = st.file_uploader("📷 حمّل صورة", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level = "خفيف" if total <= 10 else "متوسط" if total <= 30 else "عالي"
        st.success(f"👥 أشخاص: {person_count} | 🚗 مركبات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الإجمالي: ازدحام {level}")