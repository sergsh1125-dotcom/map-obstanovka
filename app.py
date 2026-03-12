import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium.features import DivIcon

# --- ВСТАВТЕ ВАШЕ ПОСИЛАННЯ ТУТ ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbUg4s6sTP1yo48ZhAuFjh5UzKetYeQvnGWAnxHdyuvs_DiCIcqY2555aclFUNXzt7zvQ8ggtNekkg/pub?output=csv"

st.set_page_config(layout="wide", page_title="Оперативна карта")

st.title("🗺️ Оперативна обстановка (Live-карта)")

# Функція завантаження даних
@st.cache_data(ttl=10)
def load_data(url):
    try:
        # Додаємо мітку часу, щоб обійти кешування браузера
        return pd.read_csv(f"{url}&t={pd.Timestamp.now().timestamp()}")
    except Exception as e:
        st.error(f"Не вдалося завантажити дані: {e}")
        return pd.DataFrame(columns=["Назва", "Широта", "Довгота", "Колір"])

df = load_data(CSV_URL)

# Відображення карти
if not df.empty:
    # Центруємо карту по середній точці ваших даних
    m = folium.Map(location=[df['Широта'].mean(), df['Довгота'].mean()], zoom_start=7)

    for _, row in df.iterrows():
        # Додаємо точку (маркер)
        folium.CircleMarker(
            location=[row["Широта"], row["Довгота"]],
            radius=8,
            color=row["Колір"],
            fill=True,
            fill_opacity=0.7,
            popup=row["Назва"]
        ).add_to(m)
        
        # Додаємо підпис поруч із точкою
        folium.Marker(
            location=[row["Широта"], row["Довгота"]],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 11pt; color: {row["Колір"]}; font-weight: bold; text-shadow: 1px 1px 2px white;">{row["Назва"]}</div>'
            )
        ).add_to(m)

    st_folium(m, width="100%", height=600)
else:
    st.warning("Таблиця порожня або посилання невірне. Перевірте заголовки: Назва, Широта, Довгота, Колір")

if st.button("🔄 Оновити карту"):
    st.rerun()
