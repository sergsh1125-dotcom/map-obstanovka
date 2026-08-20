import base64
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Платформа ХБРЯ", layout="wide")


# ============================================================
# СТИЛИ STREAMLIT
# ============================================================

st.markdown(
    """
<style>
#MainMenu, footer, header {
    visibility: hidden;
}

.main .block-container {
    max-width: 100% !important;
    padding-top: 0.5rem !important;
    padding-bottom: 0rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.custom-header {
    margin-top: -15px !important;
    margin-bottom: 10px !important;
    font-size: 26px;
    font-weight: bold;
    color: white;
}

.coord-box {
    background-color: #1e1e1e;
    color: #00ff00;
    padding: 8px 12px;
    border-radius: 5px;
    font-family: monospace;
    font-weight: bold;
    margin-bottom: 10px;
    border: 1px solid #333;
}

.info-text {
    font-size: 13px;
    color: #aaa;
    margin-bottom: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# ЗАГОЛОВОК
# ============================================================

st.markdown(
    "<div class='custom-header'>КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ</div>",
    unsafe_allow_html=True,
)


# ============================================================
# КОЛОНКИ
# ============================================================

col_map, col_gui = st.columns([3, 1])


# ============================================================
# GITHUB SVG
# ============================================================

GITHUB_USER = "sergsh1125-dotcom"
GITHUB_REPO = "map-obstanovka"
GITHUB_BRANCH = "main"

GITHUB_BASE_URL = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/svg"
)


def get_gh_svg_url(filename):
    return f"{GITHUB_BASE_URL}/{filename}"


SRC_BIOLOGICAL_HAZARD_SITE = get_gh_svg_url("biological_hazard_site.svg")
SRC_CBRN_CONTAMINATION_AREA = get_gh_svg_url("cbrn_contamination_area.svg")
SRC_CBRN_POST = get_gh_svg_url("cbrn_post.svg")
SRC_CBRN_RECON_AREA = get_gh_svg_url("cbrn_recon_area.svg")
SRC_CHEMICAL_HAZARD_SITE = get_gh_svg_url("chemical_hazard_site.svg")
SRC_DECON_AREA_SPECIAL = get_gh_svg_url("decon_area_special.svg")
SRC_DECON_POINT_SPECIAL = get_gh_svg_url("decon_point_special.svg")
SRC_DETECT_BIOLOGICAL = get_gh_svg_url("detect_biological.svg")
SRC_DETECT_CHEMICAL = get_gh_svg_url("detect_chemical.svg")
SRC_DETECT_RADIATION = get_gh_svg_url("detect_radiation.svg")
SRC_NUCLEAR_BLAST = get_gh_svg_url("nuclear_blast.svg")
SRC_RADIOACTIVE_SITE = get_gh_svg_url("radioactive_site.svg")


# ============================================================
# SESSION STATE
# ============================================================

if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = []


if "map_objects" not in st.session_state:
    st.session_state.map_objects = []


# ============================================================
# ВОССТАНОВЛЕНИЕ СОСТОЯНИЯ КАРТЫ
# ============================================================

if "map_state" in st.query_params:
    try:
        raw_map_state = st.query_params["map_state"]

        parsed_map_state = (
            json.loads(raw_map_state) if raw_map_state else []
        )

        if isinstance(parsed_map_state, list):
            st.session_state.map_objects = parsed_map_state

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):
        pass


# ============================================================
# КООРДИНАТЫ
# ============================================================

if "captured_lat" not in st.session_state:
    st.session_state.captured_lat = 50.4500


if "captured_lng" not in st.session_state:
    st.session_state.captured_lng = 30.5200


# ============================================================
# ПОЛНОЕ ОЧИЩЕНИЕ
# ============================================================

if "clear_all" in st.query_params:

    st.session_state.rkhb_points = []
    st.session_state.map_objects = []

    st.session_state.captured_lat = 50.4500
    st.session_state.captured_lng = 30.5200

    st.query_params.clear()

    st.rerun()


# ============================================================
# УДАЛЕНИЕ ТОЧКИ РАЗВЕДКИ
# ============================================================

if "delete_point_idx" in st.query_params:

    try:

        idx_to_del = int(st.query_params["delete_point_idx"])

        if 0 <= idx_to_del < len(st.session_state.rkhb_points):
            st.session_state.rkhb_points.pop(idx_to_del)

        st.query_params.clear()
        st.rerun()

    except (
        ValueError,
        TypeError,
    ):
        pass


# ============================================================
# КООРДИНАТЫ КЛИКА ПО КАРТЕ
# ============================================================

if "click_lat" in st.query_params and "click_lng" in st.query_params:

    try:

        st.session_state.captured_lat = float(st.query_params["click_lat"])

        st.session_state.captured_lng = float(st.query_params["click_lng"])

    except (
        ValueError,
        TypeError,
    ):
        pass


# ============================================================
# ПРАВАЯ ПАНЕЛЬ
# ============================================================

with col_gui:

    st.subheader("ПАНЕЛЬ УПРАВЛІННЯ")

    st.markdown(
        """
        <div class='info-text'>
        ℹ️ Для нанесення точки РХБ забруднення вручну
        клікніть у визначеній точці на карті та введіть показники.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div id='pythonCoordBox' class='coord-box'>
        📍 {st.session_state.captured_lat:.5f} ,
        {st.session_state.captured_lng:.5f}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # ТОЧКА ВИМІРЮВАННЯ
    # ========================================================

    with st.expander(
        "➕ Параметри точки вимірювання",
        expanded=True,
    ):

        m_type = st.radio(
            "Тип загрязнення:",
            [
                "Радіоактивне",
                "Хімічне",
            ],
        )

        m_lat = st.number_input(
            "Широта (Lat)",
            value=st.session_state.captured_lat,
            format="%.5f",
            key=f"lat_{st.session_state.captured_lat}",
        )

        m_lon = st.number_input(
            "Довгота (Lon)",
            value=st.session_state.captured_lng,
            format="%.5f",
            key=f"lng_{st.session_state.captured_lng}",
        )

        if m_type == "Радіоактивне":

            r_val = st.number_input(
                "Потужність дози",
                value=0.15,
                step=0.01,
            )

            r_uni = st.selectbox(
                "Одиниця виміру",
                [
                    "мкЗв/год",
                    "мЗв/год",
                ],
            )

            lbl = f"{r_val} {r_uni}"
            ico = SRC_DETECT_RADIATION

        else:

            c_sub = st.text_input(
                "Речовина",
                value="Іприт",
            )

            c_val = st.number_input(
                "Концентрація",
                value=0.10,
                step=0.01,
            )

            c_uni = st.selectbox(
                "Одиниця виміру",
                [
                    "мг/м³",
                    "ppm",
                ],
            )

            lbl = f"{c_sub} - {c_val} {c_uni}"
            ico = SRC_DETECT_CHEMICAL

        m_date = datetime.now().strftime("%d.%m.%Y")

        st.caption(f"📅 Дата фіксації (авто): {m_date}")

        if st.button(
            "Нанести точку на карту",
            type="primary",
        ):

            st.session_state.rkhb_points.append(
                {
                    "lat": m_lat,
                    "lng": m_lon,
                    "label": lbl,
                    "date": m_date,
                    "icon": ico,
                }
            )

            st.rerun()

    st.divider()

    # ========================================================
    # CSV
    # ========================================================

    st.write("📊 **Імпорт бази даних розвідки**")

    file = st.file_uploader(
        "Виберіть CSV файл:",
        type=["csv"],
        label_visibility="collapsed",
    )

    if file:

        try:

            df_csv = pd.read_csv(file)

            st.dataframe(
                df_csv.head(3),
                use_container_width=True,
            )

            if st.button("📥 Додати точки на карту з таблиці"):

                df_csv.columns = [
                    col.strip().lower() for col in df_csv.columns
                ]

                lat_col = "lat" if "lat" in df_csv.columns else None

                lng_col = (
                    "lon"
                    if "lon" in df_csv.columns
                    else ("lng" if "lng" in df_csv.columns else None)
                )

                val_col = "value" if "value" in df_csv.columns else None

                uni_col = "unit" if "unit" in df_csv.columns else None

                tim_col = "time" if "time" in df_csv.columns else None

                typ_col = "type" if "type" in df_csv.columns else None

                sub_col = (
                    "substance" if "substance" in df_csv.columns else None
                )

                if lat_col and lng_col:

                    for idx, row in df_csv.iterrows():

                        val_raw = (
                            str(row[val_col]).strip()
                            if (val_col and pd.notna(row[val_col]))
                            else ""
                        )

                        uni_raw = (
                            str(row[uni_col]).strip()
                            if (uni_col and pd.notna(row[uni_col]))
                            else ""
                        )

                        sub_raw = (
                            str(row[sub_col]).strip()
                            if (sub_col and pd.notna(row[sub_col]))
                            else ""
                        )

                        type_str = (
                            str(row[typ_col]).strip().lower()
                            if (typ_col and pd.notna(row[typ_col]))
                            else ""
                        )

                        if sub_raw:

                            label_text = (
                                f"{sub_raw.capitalize()} "
                                f"- {val_raw} {uni_raw}"
                            )

                        else:

                            label_text = f"{val_raw} {uni_raw}".strip()

                        if not label_text:
                            label_text = "Точка розвідки"

                        date_text = (
                            str(row[tim_col]).strip()
                            if (tim_col and pd.notna(row[tim_col]))
                            else datetime.now().strftime("%d.%m.%Y")
                        )

                        if (
                            "хім" in type_str
                            or "chemical" in type_str
                            or "мг/" in uni_raw
                            or "ppm" in uni_raw
                        ):

                            icon_url = SRC_DETECT_CHEMICAL

                        elif (
                            "біо" in type_str or "biological" in type_str
                        ):

                            icon_url = SRC_DETECT_BIOLOGICAL

                        else:

                            icon_url = SRC_DETECT_RADIATION

                        st.session_state.rkhb_points.append(
                            {
                                "lat": float(row[lat_col]),
                                "lng": float(row[lng_col]),
                                "label": label_text,
                                "date": date_text,
                                "icon": icon_url,
                            }
                        )

                    st.rerun()

        except Exception as e:

            st.error(f"Помилка: {str(e)}")

    # ========================================================
    # ТАБЛИЦА ТОЧЕК
    # ========================================================

    if st.session_state.rkhb_points:

        pts_only = [
            p for p in st.session_state.rkhb_points if "lat" in p
        ]

        if pts_only:

            df_view = pd.DataFrame(pts_only)

            st.dataframe(
                df_view[
                    [
                        "date",
                        "label",
                        "lat",
                        "lng",
                    ]
                ],
                use_container_width=True,
                height=110,
            )


# ============================================================
# JSON ДАННЫЕ
# ============================================================

points_json = json.dumps(
    st.session_state.rkhb_points,
    ensure_ascii=False,
)


map_objects_json = json.dumps(
    st.session_state.map_objects,
    ensure_ascii=False,
)


# ============================================================
# HTML / JAVASCRIPT КАРТЫ
# ============================================================

html_map_template = """<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Map Module CBRN</title>

<link
rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<link
rel="stylesheet"
href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css"
/>

<script
src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
</script>

<script
src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js">
</script>


<style>

html,
body {

    margin: 0;
    padding: 0;
    height: 100%;

    font-family: Arial, sans-serif;

    background: #fff;

    overflow: hidden;
}


#mapContainer {

    width: 100%;
    height: 550px;

    position: relative;

    border: 1px solid #ccc;

    border-radius: 8px;

    overflow: hidden;
}


#map {

    width: 100%;
    height: 100%;
}


#bottomControlsPanel {

    margin-top: 6px;

    background: #f9f9f9;

    padding: 8px 10px;

    border-radius: 8px;

    border: 1px solid #ddd;

    box-shadow:
        0 2px 5px rgba(0,0,0,0.1);

    box-sizing: border-box;
}


.controls-row {

    display: flex;

    gap: 8px;

    align-items: center;

    margin-bottom: 6px;

    flex-wrap: wrap;
}


.controls-row:last-child {

    margin-bottom: 0;
}


.controls-row select,
.controls-row input {

    padding: 5px 8px;

    background: #fff;

    color: #000;

    border: 1px solid #ccc;

    border-radius: 4px;

    font-size: 13px;
}


.controls-row label {

    font-size: 13px;

    font-weight: bold;

    color: #333;
}


.panel-btn {

    padding: 5px 10px;

    background: #e0e0e0;

    color: #000;

    border: 1px solid #adadad;

    border-radius: 4px;

    font-weight: bold;

    cursor: pointer;

    font-size: 13px;

    display: inline-flex;

    align-items: center;

    gap: 5px;
}


.panel-btn:hover {

    background: #d4d4d4;
}


.btn-stop {

    background: #ffebee !important;

    color: #c62828 !important;

    border-color: #ef9a9a !important;
}


.btn-stop:hover {

    background: #ffcdd2 !important;
}


.btn-clear-all {

    background: #b71c1c !important;

    color: #ffffff !important;

    border-color: #880e4f !important;
}


.btn-clear-all:hover {

    background: #d32f2f !important;
}


.btn-autoroute {

    background: #FFD600 !important;

    color: #000 !important;

    border-color: #cca300 !important;
}


.btn-autoroute:hover {

    background: #ffea00 !important;
}


#windWidget {

    position: absolute;

    bottom: 15px;

    left: 10px;

    z-index: 1000;

    background:
        rgba(26, 26, 26, 0.9);

    color: #FFD600;

    padding: 6px;

    border-radius: 8px;

    border: 1px solid #FFD600;

    text-align: center;

    width: 70px;

    box-shadow:
        0 2px 10px rgba(0,0,0,0.5);
}


.wind-arrow {

    font-size: 22px;

    display: inline-block;

    transition:
        transform 0.3s ease;
}


.wind-info {

    font-size: 10px;

    color: #fff;

    margin-top: 1px;

    font-weight: bold;
}


.route-label {

    background:
        rgba(0, 0, 0, 0.85) !important;

    border:
        1px solid #d97706 !important;

    color: #fff !important;

    font-size: 11px !important;

    font-weight: bold !important;

    padding: 2px 6px !important;

    border-radius: 4px !important;

    white-space: nowrap !important;
}

.route-endpoint {
    position: relative;
    width: 18px;
    height: 30px;
    background: transparent !important;
}
.route-endpoint::before {
    content: ""; position: absolute; left: 8px; top: 9px;
    width: 2px; height: 19px; background: #222; border-radius: 1px;
}
.route-endpoint::after {
    content: ""; position: absolute; left: 3px; top: 0;
    width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;
    box-shadow: 0 0 0 1px #222, 0 2px 5px rgba(0,0,0,0.45);
}
.route-start::after { background: #00a000; }
.route-finish::after { background: #d00000; }


.leaflet-div-icon {

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}


.cbrn-military-lbl {

    font-family: Arial, sans-serif;

    font-size: 12px;

    font-weight: bold;

    color: #000 !important;

    text-align: center;

    display: inline-block;

    white-space: nowrap;

    line-height: 1.3;

    background: transparent !important;
}


.cbrn-line-divider {

    border-bottom:
        2px solid #000 !important;

    width: 100%;

    display: block;

    margin: 2px 0;
}


.cbrn-date-sub {

    font-size: 11px;

    font-weight: bold;

    color: #000 !important;

    display: block;
}


</style>

</head>


<body>


<div id="mapContainer">

    <div id="map"></div>

    <div id="windWidget">

        <div
            class="wind-arrow"
            id="arrow">
            ↑
        </div>

        <div
            class="wind-info"
            id="degInfo">
            0°
        </div>

        <div
            class="wind-info"
            id="speedInfo">
            0 м/с
        </div>

    </div>

</div>


<div id="bottomControlsPanel">


    <div class="controls-row">

        <label>
            🧭 УМОВНІ ЗНАКИ РХБЗ:
        </label>


        <select id="signSelect">

            <option value="">
                -- Оберіть умовний знак для встановлення кліком --
            </option>

            <option value="ICO_DETECT_RADIATION">
                Точка рад. забруднення (detect_radiation)
            </option>

            <option value="ICO_DETECT_CHEMICAL">
                Точка хім. забруднення (detect_chemical)
            </option>

            <option value="ICO_DETECT_BIOLOGICAL">
                Точка біо. зараження (detect_biological)
            </option>

            <option value="ICO_CBRN_POST">
                Пост РХ спостереження (cbrn_post)
            </option>

            <option value="ICO_NUCLEAR_BLAST">
                Епіцентр ядерного вибуху (nuclear_blast)
            </option>

            <option value="ICO_BIOLOGICAL_HAZARD_SITE">
                Біологічно небезпечний об'єкт
            </option>

            <option value="ICO_CHEMICAL_HAZARD_SITE">
                Хімічно небезпечний об'єкт
            </option>

            <option value="ICO_RADIOACTIVE_SITE">
                Радіаціно небезпечний об'єкт
            </option>

            <option value="ICO_CBRN_CONTAMINATION_AREA">
                Район РХБ забруднення
            </option>

            <option value="ICO_CBRN_RECON_AREA">
                Район РХБЗ розвідки
            </option>

            <option value="ICO_DECON_AREA_SPECIAL">
                Район спеціальної обробки
            </option>

            <option value="ICO_DECON_POINT_SPECIAL">
                Пункт спеціальної обробки
            </option>

        </select>
        <button
            class="panel-btn"
            style="
                background:#fff3e0;
                border-color:#d97706;
                color:#b45309;
            "
            id="reconRouteBtn">

            Маршрут (ручний)

        </button>


        <button
            class="panel-btn"
            style="
                background:#e1f5fe;
                border-color:#0288d1;
            "
            id="textBtn">

            Текст

        </button>


        <button
            class="panel-btn"
            style="
                background:#efebe9;
                border-color:#5d4037;
            "
            id="ellipseBtn">

            Еліпс AEGL

        </button>


        <button
            class="panel-btn"
            style="
                background:#ffffff;
                border-color:#616161;
            "
            id="stopBtn">

            ЗАВЕРШИТИ знак

        </button>


        <button
            class="panel-btn btn-stop"
            id="deleteModeBtn">

            🗑️ ВИДАЛИТИ (кліком)

        </button>


        <button
            class="panel-btn btn-clear-all"
            id="clearAllMapBtn">

            ОЧИСТИТИ ВСЮ КАРТУ

        </button>

    </div>


    <div class="controls-row">

        <label>
            МАРШРУТ (через ';'):
        </label>


        <input
            type="text"
            id="autoRouteInput"
            placeholder="Наприклад: Київ; Фастів; Житомир"
            style="
                flex:1;
                min-width:220px;
            "
        >


        <button
            class="panel-btn btn-autoroute"
            id="buildAutoRouteBtn">

            Маршрут (автоматичний режим)

        </button>

    </div>


    <div class="controls-row">

        <label>
            МЕТЕО — Напрямок вітру (звідки дме):
        </label>


        <input
            type="number"
            id="windInput"
            placeholder="Градуси (0-360)"
            min="0"
            max="360"
            value="0"
            style="width:120px;"
        >


        <label>
            Швидкість вітру:
        </label>


        <input
            type="number"
            id="windSpeedInput"
            placeholder="м/с"
            min="0"
            value="2.0"
            step="0.1"
            style="width:90px;"
        >


        <button
            class="panel-btn"
            style="
                background:#fff59d;
                border-color:#fbc02d;
            "
            id="applyMeteoBtn">

            🌀 Застосувати

        </button>


        <button
            class="panel-btn"
            style="
                background:#c8e6c9;
                border-color:#388e3c;
                margin-left:15px;
            "
            id="htmlBtn">

            🌐 Зберегти HTML

        </button>


        <button
            class="panel-btn"
            style="
                background:#ffcdd2;
                border-color:#d32f2f;
            "
            id="printBtn">

            🖨️ Друк / PDF

        </button>

    </div>

</div>


<script>

var DATA_FROM_PYTHON = __POINTS_JSON__;
var SAVED_MAP_OBJECTS = __MAP_OBJECTS_JSON__;

var map = L.map('map', { zoomControl: true }).setView([48.3, 31.1], 6);

var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});

var satLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
    attribution: '© Google'
});

osmLayer.addTo(map);

map.pm.addControls({
    position: 'topleft',
    drawMarker: false,
    drawCircleMarker: false,
    drawPolyline: true,
    drawRectangle: true,
    drawPolygon: true,
    drawCircle: true,
    editControls: false
});

map.pm.setGlobalOptions({
    measurements: { display: true },
    pathOptions: {
        color: '#d97706',
        fillColor: '#FFD600',
        fillOpacity: 0.35,
        weight: 4
    },
    pinToMarker: true
});

map.pm.setLang('uk');

var baseMaps = {
    "🗺️ Карта OSM": osmLayer,
    "🛰️ Супутник Google": satLayer
};

L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

// Завантаження точок розвідки
if (Array.isArray(DATA_FROM_PYTHON)) {
    DATA_FROM_PYTHON.forEach(function(p) {
        if (p.lat && p.lng) {
            var customIcon = L.icon({
                iconUrl: p.icon || "__SRC_DETECT_RADIATION__",
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            });
            var m = L.marker([p.lat, p.lng], { icon: customIcon }).addTo(map);
            m.bindTooltip(p.label + " (" + p.date + ")", { permanent: false });
        }
    });
}

map.on('click', function(e) {
    window.location.href = '?click_lat=' + e.latlng.lat + '&click_lng=' + e.latlng.lng;
});

</script>

</body>
</html>
"""


# ============================================================
# ВПРОАДЖЕННЯ ДАНИХ ТА РЕНДЕРИНГ
# ============================================================

html_rendered = (
    html_map_template.replace("__POINTS_JSON__", points_json)
    .replace("__MAP_OBJECTS_JSON__", map_objects_json)
    .replace("__SRC_DETECT_RADIATION__", SRC_DETECT_RADIATION)
)

with col_map:
    components.html(html_rendered, height=720)
