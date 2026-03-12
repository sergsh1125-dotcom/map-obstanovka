import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium.features import DivIcon

# Посилання на вашу таблицю
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbUg4s6sTP1yo48ZhAuFjh5UzKetYeQvnGWAnxHdyuvs_DiCIcqY2555aclFUNXzt7zvQ8ggtNekkg/pub?output=csv"

st.set_page_config(layout="wide", page_title="Розширена карта")

def load_data(url):
    try:
        df = pd.read_csv(f"{url}&t={pd.Timestamp.now().timestamp()}")
        df.columns = df.columns.str.strip().str.capitalize()
        # Заповнюємо пусті типи значенням "Точка"
        if 'Тип' not in df.columns: df['Тип'] = 'Точка'
        df['Тип'] = df['Тип'].fillna('Точка')
        return df
    except:
        return pd.DataFrame()

df = load_data(CSV_URL)

st.title("🗺️ Оперативна обстановка: Розширений режим")

if not df.empty:
    # 1. СТВОРЕННЯ КАРТИ ТА ВИБІР ШАРІВ
    m = folium.Map(location=[df['Широта'].mean(), df['Довгота'].mean()], zoom_start=6)
    
    # Додаємо різні типи мап
    folium.TileLayer('openstreetmap', name='Схема (OpenStreetMap)').add_to(m)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Супутник (Esri)',
        attr='Esri World Imagery'
    ).add_to(m)
    folium.TileLayer('Stamen Terrain', name='Рельєф (Terrain)').add_to(m)

    # 2. НАНЕСЕННЯ ОБ'ЄКТІВ
    for _, row in df.iterrows():
        try:
            lat, lon = float(row["Широта"]), float(row["Довгота"])
            color = row["Колір"] if pd.notna(row["Колір"]) else "blue"
            obj_type = str(row["Тип"]).strip().lower()

            if obj_type == 'точка':
                folium.CircleMarker(
                    location=[lat, lon], radius=8, color=color, fill=True, popup=row["Назва"]
                ).add_to(m)
                folium.Marker(
                    location=[lat, lon],
                    icon=DivIcon(html=f'<div style="font-size:10pt; color:{color}; font-weight:bold; white-space:nowrap;">{row["Назва"]}</div>')
                ).add_to(m)

            elif obj_type == 'лінія' and pd.notna(row['Координати_2']):
                # Розбиваємо другу координату
                lat2, lon2 = map(float, str(row['Координати_2']).split(','))
                folium.PolyLine([[lat, lon], [lat2, lon2]], color=color, weight=5, opacity=0.8, popup=row["Назва"]).add_to(m)

            elif obj_type == 'текст':
                folium.Marker(
                    location=[lat, lon],
                    icon=DivIcon(html=f'<div style="font-size:12pt; color:{color}; font-weight:bold; background:rgba(255,255,255,0.5); padding:2px; border-radius:3px;">{row["Назва"]}</div>')
                ).add_to(m)
        except: continue

    # Додаємо контроль шарів (кнопка вгорі справа)
    folium.LayerControl().add_to(m)

    # 3. ВІДОБРАЖЕННЯ
    col1, col2 = st.columns([4, 1])
    with col1:
        st_folium(m, width="100%", height=650)
    
    with col2:
        # 4. ЛЕГЕНДА
        st.subheader("📌 Легенда")
        # Створюємо унікальний список назв та кольорів з таблиці
        legend_items = df[['Назва', 'Колір']].drop_duplicates().head(10)
        for _, item in legend_items.iterrows():
            st.markdown(f'<p><span style="color:{item["Колір"]}; font-size:20px;">●</span> {item["Назва"]}</p>', unsafe_allow_value=True)
        
        if st.button("🔄 Оновити дані"):
            st.rerun()

else:
    st.error("Будь ласка, перевірте таблицю.")
