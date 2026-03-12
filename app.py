import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from folium.features import DivIcon

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(layout="wide", page_title="Система Обстановки (Cloud)")

# --- ПІДКЛЮЧЕННЯ ДО ТАБЛИЦІ ---
# Потрібно додати секрети в Streamlit Cloud (Settings -> Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="10s") # Оновлювати дані кожні 10 секунд

# --- ОСНОВНИЙ ІНТЕРФЕЙС ---
st.title("🗺️ Оперативна обстановка (Sync з Google Sheets)")

# Завантажуємо актуальні дані з хмари
df_objects = get_data()

col_map, col_ctrl = st.columns([3, 1])

with col_ctrl:
    st.subheader("📍 Нова відмітка")
    c_lat = st.session_state.get('last_clicked_lat', 50.4500)
    c_lon = st.session_state.get('last_clicked_lon', 30.5233)
    
    with st.form("add_point"):
        new_label = st.text_input("Назва:")
        new_lat = st.number_input("Широта:", value=c_lat, format="%.4f")
        new_lon = st.number_input("Довгота:", value=c_lon, format="%.4f")
        new_color = st.color_picker("Колір:", "#FF0000")
        
        if st.form_submit_button("Зберегти в хмару"):
            # Створюємо новий рядок
            new_data = pd.DataFrame([{
                "Назва": new_label,
                "Широта": new_lat,
                "Довгота": new_lon,
                "Колір": new_color
            }])
            # Оновлюємо таблицю
            updated_df = pd.concat([df_objects, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Дані збережено!")
            st.rerun()

with col_map:
    m = folium.Map(location=[c_lat, c_lon], zoom_start=7)
    
    # Малюємо точки з бази даних
    for _, row in df_objects.iterrows():
        folium.CircleMarker(
            location=[row["Широта"], row["Довгота"]],
            radius=8, color=row["Колір"], fill=True, fill_opacity=0.7
        ).add_to(m)
        
        folium.Marker(
            location=[row["Широта"], row["Довгота"]],
            icon=DivIcon(html=f'<div style="font-size:11pt; color:{row["Колір"]}; font-weight:bold; text-shadow:1px 1px 2px white;">{row["Назва"]}</div>')
        ).add_to(m)

    map_data = st_folium(m, width="100%", height=600)

    # Обробка кліку для координат
    if map_data and map_data.get("last_clicked"):
        st.session_state['last_clicked_lat'] = map_data["last_clicked"]["lat"]
        st.session_state['last_clicked_lon'] = map_data["last_clicked"]["lng"]
        st.rerun()

# --- ТАБЛИЦЯ ТА ВИДАЛЕННЯ ---
st.subheader("📝 Редагування бази даних")
edited_df = st.data_editor(df_objects, num_rows="dynamic", use_container_width=True)

if st.button("Оновити зміни в таблиці"):
    conn.update(data=edited_df)
    st.success("Базу даних синхронізовано!")
    st.rerun()
