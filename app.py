import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium.features import DivIcon

# Ваше посилання (вже перевірене)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbUg4s6sTP1yo48ZhAuFjh5UzKetYeQvnGWAnxHdyuvs_DiCIcqY2555aclFUNXzt7zvQ8ggtNekkg/pub?output=csv"

st.set_page_config(layout="wide", page_title="Карта")

def load_data(url):
    try:
        # Читаємо дані
        df = pd.read_csv(f"{url}&t={pd.Timestamp.now().timestamp()}")
        # Очищаємо назви стовпців від пробілів та робимо їх з великої літери
        df.columns = df.columns.str.strip().str.capitalize()
        return df
    except Exception as e:
        st.error(f"Помилка: {e}")
        return pd.DataFrame()

df = load_data(CSV_URL)

if not df.empty and 'Широта' in df.columns:
    st.title("🗺️ Оперативна обстановка")
    
    # Створення карти
    m = folium.Map(location=[df['Широта'].mean(), df['Довгота'].mean()], zoom_start=6)

    for _, row in df.iterrows():
        try:
            folium.CircleMarker(
                location=[float(row["Широта"]), float(row["Довгота"])],
                radius=8, color=row["Колір"], fill=True, fill_opacity=0.7
            ).add_to(m)
            
            folium.Marker(
                location=[float(row["Широта"]), float(row["Довгота"])],
                icon=DivIcon(html=f'<div style="font-size:11pt; color:{row["Колір"]}; font-weight:bold; text-shadow:1px 1px 2px white;">{row["Назва"]}</div>')
            ).add_to(m)
        except:
            continue

    st_folium(m, width="100%", height=600)
else:
    st.error("⚠️ Проблема з даними!")
    st.write("Програма бачить такі стовпці:", df.columns.tolist() if not df.empty else "Таблиця порожня")
    st.info("Переконайтеся, що в першому рядку таблиці написано: Назва, Широта, Довгота, Колір")
