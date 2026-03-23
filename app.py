import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ===============================
# 1. НАЛАШТУВАННЯ СТОРІНКИ ТА СТИЛІВ
# ===============================
st.set_page_config(page_title="РХБ ОБСТАНОВКА", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
/* Стиль жовтих кнопок */
.stButton button {
    font-weight: bold; width: 100%; height: 3em; border-radius: 8px; 
    background-color: #FFD600 !important; color: black !important;
    border: 1px solid #cca300 !important;
}
.stButton button:hover { background-color: #ffea00 !important; border: 2px solid #4CAF50 !important; }

/* Зелена кнопка нанесення */
div.stButton > button:first-child[data-testid="stBaseButton-primary"] {
    background-color: #4CAF50 !important; color: white !important; border: 1px solid #388E3C !important;
}
</style>
""", unsafe_allow_html=True)

# Стан програми
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["lat", "lon", "value", "unit", "time", "type", "substance"])
if "clicked_coords" not in st.session_state:
    st.session_state.clicked_coords = None

# ===============================
# 2. ФУНКЦІЯ ПІДПИСУ (З ЛІНІЄЮ)
# ===============================
def marker_html(main_text, date_text):
    return f"""
    <div style="display: inline-block; font-family: Arial; font-size: 10pt; color: blue; font-weight: bold; 
                text-align: center; white-space: nowrap; text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;">
        <div style="border-bottom: 2px solid blue; display: inline-block; padding-bottom: 2px; margin-bottom: 2px;">
            {main_text}
        </div>
        <div style="font-weight: normal; font-size: 9pt;">
            {date_text}
        </div>
    </div>
    """

# ===============================
# 3. СТВОРЕННЯ КАРТИ З ЛЕГЕНДОЮ ПО ДНЯМ
# ===============================
def create_map(df, start_lat, start_lon, zoom_val):
    m = folium.Map(location=[start_lat, start_lon], zoom_start=zoom_val, tiles=None, control_scale=True)
    
    # Шари карти
    folium.TileLayer('OpenStreetMap', name='Карта', show=True).add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                     attr='Google', name='Супутник', show=False).add_to(m)

    # Червоний маркер вибору місця
    if st.session_state.clicked_coords:
        folium.Marker([st.session_state.clicked_coords['lat'], st.session_state.clicked_coords['lng']],
                      icon=folium.Icon(color="red", icon="plus")).add_to(m)

    # Групування точок по дням для легенди
    if not df.empty:
        # Отримуємо унікальні дати
        unique_days = sorted(df['time'].unique(), reverse=True)
        
        for day in unique_days:
            # Створюємо групу для кожного дня
            group = folium.FeatureGroup(name=f"📅 {day}")
            
            # Фільтруємо дані за цей день
            day_data = df[df['time'] == day]
            
            for _, r in day_data.iterrows():
                # Визначаємо стиль залежно від типу (Радіація чи Хімія)
                if "Хімічне" in str(r["type"]):
                    main_color, fill_color = "orange", "yellow"
                    label = f"{r['substance']} {r['value']} {r['unit']}"
                else:
                    main_color, fill_color = "blue", "blue"
                    label = f"{r['value']} {r['unit']}"

                # Сама точка
                folium.CircleMarker(
                    [r.lat, r.lon], radius=4, color=main_color, 
                    fill=True, fill_color=fill_color, fill_opacity=1
                ).add_to(group)

                # Підпис до точки
                folium.Marker(
                    [r.lat, r.lon],
                    icon=folium.DivIcon(icon_anchor=(80, 45), html=marker_html(label, str(r['time'])))
                ).add_to(group)
            
            # Додаємо групу дня на карту
            group.add_to(m)

    # Додаємо контроль шарів (Легенда)
    folium.LayerControl(collapsed=False).add_to(m)
    return m

# ===============================
# 4. ІНТЕРФЕЙС
# ===============================
st.header("📍 МОНІТОРИНГ РХБ ОБСТАНОВКИ")
col_map, col_gui = st.columns([3, 1])

with col_gui:
    st.subheader("ПУЛЬТ УПРАВЛІННЯ")
    mode = st.radio("Режим:", ["Радіоактивне забруднення", "Хімічне забруднення"], key="mode_switch")
    st.divider()

    # Координати з кліку
    if st.session_state.clicked_coords:
        c_lat, c_lon = st.session_state.clicked_coords['lat'], st.session_state.clicked_coords['lng']
        st.info(f"📍 {c_lat:.6f}, {c_lon:.6f}")
        if st.button("Вставити координати"):
            st.session_state.manual_lat, st.session_state.manual_lon = c_lat, c_lon
            st.rerun()

    lat_input = st.number_input("Широта", format="%.6f", value=st.session_state.get('manual_lat', 50.4500))
    lon_input = st.number_input("Довгота", format="%.6f", value=st.session_state.get('manual_lon', 30.5200))

    # Блоки вводу
    if mode == "Радіоактивне забруднення":
        st.markdown("#### Радіація")
        val = st.number_input("Значення", format="%.2f", step=0.01, key="r_v")
        uni = st.selectbox("Одиниця", ["мкЗв/год", "мЗв/год"], key="r_u")
        sub = ""
    else:
        st.markdown("#### Хімія")
        sub = st.text_input("Речовина", key="c_s")
        val = st.number_input("Значення", format="%.2f", step=0.01, key="c_v")
        uni = st.selectbox("Одиниця", ["мг/м³", "ppm"], key="c_u")

    date_input = st.date_input("Дата", value=datetime.now()).strftime("%d.%m.%Y")

    if st.button("✅ НАНЕСТИ НА КАРТУ", type="primary"):
        new_row = pd.DataFrame([{
            "lat": lat_input, "lon": lon_input, "value": val, "unit": uni, 
            "time": date_input, "type": mode, "substance": sub
        }])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.session_state.clicked_coords = None
        st.rerun()

    st.divider()
    file = st.file_uploader("Імпорт CSV", type=["csv"])
    if file and st.button("Завантажити дані"):
        df_csv = pd.read_csv(file)
        st.session_state.data = pd.concat([st.session_state.data, df_csv], ignore_index=True)
        st.rerun()

# ===============================
# 5. ВІДОБРАЖЕННЯ КАРТИ
# ===============================
with col_map:
    c_lat = st.session_state.data.lat.mean() if not st.session_state.data.empty else 49.0
    c_lon = st.session_state.data.lon.mean() if not st.session_state.data.empty else 31.0
    
    map_obj = create_map(st.session_state.data, c_lat, c_lon, 6 if st.session_state.data.empty else 9)
    res = st_folium(map_obj, width="100%", height=700, key="rkhb_map", returned_objects=["last_clicked"])

    if res.get("last_clicked"):
        if st.session_state.clicked_coords != res["last_clicked"]:
            st.session_state.clicked_coords = res["last_clicked"]
            st.rerun()

    # Функції під картою
    c1, c2, c3 = st.columns(3)
    if c1.button("🗑️ Очистити"):
        st.session_state.data = pd.DataFrame(columns=["lat","lon","value","unit","time","type","substance"])
        st.rerun()
    
    if not st.session_state.data.empty:
        c2.download_button("💾 Карта HTML", map_obj._repr_html_(), "map.html", "text/html")
        c3.download_button("📊 Дані CSV", st.session_state.data.to_csv(index=False), "data.csv", "text/csv")
        st.dataframe(st.session_state.data, use_container_width=True)
