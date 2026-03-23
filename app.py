import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ===============================
# 1. Налаштування сторінки
# ===============================
st.set_page_config(page_title="РАДІАЦІЙНА ТА ХІМІЧНА ОБСТАНОВКА", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

/* Стиль для всіх кнопок */
.stButton button {
    font-weight: bold; 
    width: 100%; 
    height: 3em; 
    border-radius: 8px; 
    background-color: #FFD600 !important; /* Яскравий жовтий колір (колір попередження) */
    color: black !important;
    border: 1px solid #cca300 !important;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}

/* Ефект при наведенні та натисканні */
.stButton button:hover {
    background-color: #ffea00 !important;
    border: 2px solid #4CAF50 !important;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
}

/* Окремий стиль для кнопки "Нанести на карту" (робимо її ще помітнішою) */
div.stButton > button:first-child[data-testid="stBaseButton-primary"] {
    background-color: #4CAF50 !important;
    color: white !important;
    border: 1px solid #388E3C !important;
}
</style>
""", unsafe_allow_html=True)

# Стан програми
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["lat", "lon", "value", "unit", "time", "type", "substance"])
if "clicked_coords" not in st.session_state:
    st.session_state.clicked_coords = None

# ===============================
# 2. Функція підпису з лінією
# ===============================
def get_custom_marker_html(top_text, bottom_text):
    return f"""
<div style="display:inline-block; font-family: 'Arial'; font-size:10pt; color:blue; font-weight:bold; text-align:center;
text-shadow:-1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;">
    <div style="white-space: nowrap; border-bottom: 2px solid blue; padding-bottom: 2px; margin-bottom: 2px;">
        {top_text}
    </div>
    <div style="white-space: nowrap; font-weight: normal; font-size: 9pt;">
        {bottom_text}
    </div>
</div>
"""

# ===============================
# 3. Створення карти
# ===============================
def create_map(df_data, start_lat, start_lon, zoom_val):
    m = folium.Map(location=[start_lat, start_lon], zoom_start=zoom_val, tiles=None, control_scale=True)
    folium.TileLayer('OpenStreetMap', name='Карта', show=True).add_to(m)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google', name='Супутник', show=False
    ).add_to(m)

    if st.session_state.clicked_coords:
        folium.Marker(
            [st.session_state.clicked_coords['lat'], st.session_state.clicked_coords['lng']],
            icon=folium.Icon(color="red", icon="plus")
        ).add_to(m)

    for _, r in df_data.iterrows():
        if r["type"] == "Хімічне":
            main_color, fill_color = "orange", "yellow"
            label = f"{r['substance']} {r['value']} {r['unit']}"
        else:
            main_color, fill_color = "blue", "blue"
            label = f"{r['value']} {r['unit']}"

        folium.CircleMarker(
            [r.lat, r.lon], radius=7, color=main_color, fill=True, fill_color=fill_color, fill_opacity=1
        ).add_to(m)

        folium.Marker(
            [r.lat, r.lon],
            icon=folium.DivIcon(icon_anchor=(70, 45), html=get_custom_marker_html(label, r['time']))
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m

# ===============================
# 4. ІНТЕРФЕЙС
# ===============================
st.header("📍 СИСТЕМА МОНІТОРИНГУ РХБ ОБСТАНОВКИ")
col_map, col_gui = st.columns([3, 1])

with col_gui:
    st.subheader("ПУЛЬТ УПРАВЛІННЯ")
    
    mode = st.radio("Оберіть режим:", ["Радіоактивне забруднення", "Хімічне забруднення"], key="mode_switch")
    st.divider()

    if st.session_state.clicked_coords:
        c_lat, c_lon = st.session_state.clicked_coords['lat'], st.session_state.clicked_coords['lng']
        st.info(f"Вибрано на карті: \n{c_lat:.6f}, {c_lon:.6f}")
        if st.button("Вставити координати"):
            st.session_state.manual_lat = c_lat
            st.session_state.manual_lon = c_lon
            st.rerun()

    lat = st.number_input("Широта", format="%.6f", value=st.session_state.get('manual_lat', 50.4500))
    lon = st.number_input("Довгота", format="%.6f", value=st.session_state.get('manual_lon', 30.5200))

    if mode == "Радіоактивне забруднення":
        st.markdown("#### Дані радіаційної розвідки")
        val = st.number_input("ПЕД (значення)", format="%.2f", step=0.01, key="rad_val")
        unit = st.selectbox("Одиниця", ["мкЗв/год", "мЗв/год"], key="rad_unit")
        substance = "" 
    else:
        st.markdown("#### Дані хімічної розвідки")
        substance = st.text_input("Назва речовини (напр. Хлор)", key="chem_sub")
        val = st.number_input("Концентрація", format="%.2f", step=0.01, key="chem_val")
        unit = st.selectbox("Одиниця", ["мг/м³", "ppm"], key="chem_unit")

    date_val = st.date_input("Дата", value=datetime.now()).strftime("%d.%m.%Y")

    if st.button("✅ НАНЕСТИ НА КАРТУ", type="primary"):
        p_type = "Хімічне" if mode == "Хімічне забруднення" else "Радіоактивне забруднення"
        new_row = pd.DataFrame([{
            "lat": lat, "lon": lon, "value": val, "unit": unit, 
            "time": date_val, "type": p_type, "substance": substance
        }])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.session_state.clicked_coords = None
        st.rerun()

# ===============================
# 5. КАРТА ТА ТАБЛИЦЯ
# ===============================
with col_map:
    c_lat = st.session_state.data.lat.mean() if not st.session_state.data.empty else 49.0
    c_lon = st.session_state.data.lon.mean() if not st.session_state.data.empty else 31.0
    
    m_obj = create_map(st.session_state.data, c_lat, c_lon, 6 if st.session_state.data.empty else 9)
    map_res = st_folium(m_obj, width="100%", height=700, key="main_map", returned_objects=["last_clicked"])

    if map_res.get("last_clicked"):
        clicked = map_res["last_clicked"]
        if st.session_state.clicked_coords != clicked:
            st.session_state.clicked_coords = clicked
            st.rerun()

    c1, c2, c3 = st.columns(3)
    if c1.button("🗑️ Очистити карту"):
        st.session_state.data = pd.DataFrame(columns=["lat","lon","value","unit","time","type","substance"])
        st.session_state.clicked_coords = None
        st.rerun()
    
    if not st.session_state.data.empty:
        c2.download_button("💾 Зберегти карту HTML", m_obj._repr_html_(), "map.html", "text/html")
        c3.download_button("📊 Скачати CSV", st.session_state.data.to_csv(index=False), "data.csv", "text/csv")
        st.dataframe(st.session_state.data, use_container_width=True)
