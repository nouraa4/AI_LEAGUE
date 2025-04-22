import streamlit as st
import os
import gdown
import numpy as np
import folium
from ultralytics import YOLO
from streamlit_folium import st_folium
from PIL import Image
from base64 import b64encode

st.set_page_config(layout="wide", page_title="F.A.N.S", page_icon="⚽")

# خلفية صفحة الترحيب

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .welcome-wrapper {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        height: 100vh;
        padding-top: 10%;
    }}
    .welcome-title {{
        font-size: 3rem;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }}
    .stButton>button {{
        background-color: #ffffff22;
        color: white;
        border: 2px solid white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.8rem 2.2rem;
        margin: 0.8rem;
        font-size: 1.1rem;
    }}
    .stButton>button:hover {{
        background-color: white;
        color: black;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# حالة الصفحة الحالية
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "closed_gates" not in st.session_state:
    st.session_state.closed_gates = []

# تحميل نموذج YOLO
model_path = "best_Model.pt"
model_url = "https://drive.google.com/uc?id=1Lz6H7w92fli_I88Jy2Hd6gacUoPyNVPt"
if not os.path.exists(model_path):
    with st.spinner("📅 جاري تحميل نموذج YOLO..."):
        gdown.download(model_url, model_path, quiet=False)
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

# تحليل صور البوابات
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

# الصفحة الترحيبية
if st.session_state.page == "welcome":
    set_background("welcome.png")
    st.markdown(f'<div class="welcome-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-title">F.A.N.S - الملعب الذكي للمشجعين ⚽</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("أنا مشجع"):
            st.session_state.page = "fan"
            st.experimental_rerun()
    with col2:
        if st.button("أنا منظم"):
            st.session_state.page = "admin"
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- صفحة المشجع -------------------
elif st.session_state.page == "fan":
    if st.button("↩️ العودة للصفحة الرئيسية"):
        st.session_state.page = "welcome"
        st.experimental_rerun()

    st.title("🎫 توصية البوابة للمشجع")
    st.subheader("أدخل بيانات تذكرتك")
    ticket = st.text_input("🎟️ رقم التذكرة (مثال: A123)")

    if ticket:
        zone = gate_dirs.get(ticket[0].upper(), {}).get("zone")
        if zone:
            st.info(f"📍 جهة مقعدك: {zone}")
            available = {
                g: d for g, d in gate_info.items()
                if d["zone"] == zone and g not in st.session_state.closed_gates
            }
            filtered = {g: d for g, d in available.items() if d["level"] != "عالي"}

            if filtered:
                best_gate = min(filtered.items(), key=lambda x: x[1]["count"])[0]
                level = filtered[best_gate]["level"]
                st.success(f"✅ نوصي بالتوجه إلى بوابة: {best_gate} (ازدحام {level})")
            else:
                st.warning("⚠️ لا توجد بوابات متاحة حاليًا في هذه الجهة أو جميعها مغلقة/مزدحمة.")
        else:
            st.error("❌ رقم التذكرة غير معروف")

    st.subheader("🗺️ خريطة البوابات")
    m = folium.Map(location=[21.6235, 39.1115], zoom_start=17)
    for gate, data in gate_info.items():
        folium.Marker(
            location=[data["lat"], data["lon"]],
            popup=f"بوابة {gate} - ازدحام {data['level']}" + (" (مغلقة)" if gate in st.session_state.closed_gates else ""),
            icon=folium.Icon(
                color="gray" if gate in st.session_state.closed_gates else
                "green" if data["level"] == "خفيف" else
                "orange" if data["level"] == "متوسط" else "red"
            )
        ).add_to(m)
    st_folium(m, width=700, height=450)

# ------------------- صفحة المنظم -------------------
elif st.session_state.page == "admin":
    if st.button("↩️ العودة للصفحة الرئيسية"):
        st.session_state.page = "welcome"
        st.experimental_rerun()

    st.title("🛠️ لوحة تحكم المنظم")
    st.subheader("🚪 حالة وتحكم البوابات")

    cols = st.columns(3)
    for idx, (gate, data) in enumerate(gate_info.items()):
        with cols[idx % 3]:
            st.markdown(f"""### بوابة {gate}
- 👥 عدد الأشخاص: `{data['count']}`
- 🚦 مستوى الزحام: `ازدحام {data['level']}`
- 📌 الحالة: `{"مغلقة" if gate in st.session_state.closed_gates else "مفتوحة"}`""")

            if gate in st.session_state.closed_gates:
                if st.button(f"🔓 فتح بوابة {gate}", key=f"open_{gate}"):
                    st.session_state.closed_gates.remove(gate)
            else:
                if st.button(f"🔒 إغلاق بوابة {gate}", key=f"close_{gate}"):
                    st.session_state.closed_gates.append(gate)

    st.subheader("🚨 تنبيهات الازدحام")
    for gate, data in gate_info.items():
        if data["level"] == "عالي" and gate not in st.session_state.closed_gates:
            st.error(f"⚠️ ازدحام عالي عند بوابة {gate}!")

    st.subheader("🛣️ تحليل زحام الشوارع والمواقف")
    street_img = st.file_uploader("📷 حمّل صورة للشارع أو المواقف", type=["jpg", "png"])
    if street_img:
        img_array = np.array(Image.open(street_img))
        results = model(img_array)[0]
        person_count = sum(1 for c in results.boxes.cls if int(c) == 0)
        vehicle_count = sum(1 for c in results.boxes.cls if int(c) in [2, 3, 5, 7])
        total = person_count + vehicle_count
        level = "خفيف" if total <= 10 else "متوسط" if total <= 30 else "عالي"
        st.success(f"👥 أشخاص: {person_count} | 🚗 مركبات: {vehicle_count}")
        st.info(f"🚦 مستوى الزحام الإجمالي: ازدحام {level}")
