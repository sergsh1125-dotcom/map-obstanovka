import base64
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Платформа ХБРЯ",
    layout="wide"
)


# =========================================================
# СТИЛИ STREAMLIT
# =========================================================

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


# =========================================================
# ЗАГОЛОВОК
# =========================================================

st.markdown(
    "<div class='custom-header'>КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ</div>",
    unsafe_allow_html=True,
)


col_map, col_gui = st.columns([3, 1])


# =========================================================
# GITHUB SVG
# =========================================================

GITHUB_USER = "sergsh1125-dotcom"
GITHUB_REPO = "map-obstanovka"
GITHUB_BRANCH = "main"

GITHUB_BASE_URL = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/svg"
)


def get_gh_svg_url(filename):
    return f"{GITHUB_BASE_URL}/{filename}"


SRC_BIOLOGICAL_HAZARD_SITE = get_gh_svg_url(
    "biological_hazard_site.svg"
)

SRC_CBRN_CONTAMINATION_AREA = get_gh_svg_url(
    "cbrn_contamination_area.svg"
)

SRC_CBRN_POST = get_gh_svg_url(
    "cbrn_post.svg"
)

SRC_CBRN_RECON_AREA = get_gh_svg_url(
    "cbrn_recon_area.svg"
)

SRC_CHEMICAL_HAZARD_SITE = get_gh_svg_url(
    "chemical_hazard_site.svg"
)

SRC_DECON_AREA_SPECIAL = get_gh_svg_url(
    "decon_area_special.svg"
)

SRC_DECON_POINT_SPECIAL = get_gh_svg_url(
    "decon_point_special.svg"
)

SRC_DETECT_BIOLOGICAL = get_gh_svg_url(
    "detect_biological.svg"
)

SRC_DETECT_CHEMICAL = get_gh_svg_url(
    "detect_chemical.svg"
)

SRC_DETECT_RADIATION = get_gh_svg_url(
    "detect_radiation.svg"
)

SRC_NUCLEAR_BLAST = get_gh_svg_url(
    "nuclear_blast.svg"
)

SRC_RADIOACTIVE_SITE = get_gh_svg_url(
    "radioactive_site.svg"
)


# =========================================================
# SESSION STATE
# =========================================================

if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = []


if "map_objects" not in st.session_state:
    st.session_state.map_objects = []


if "captured_lat" not in st.session_state:
    st.session_state.captured_lat = 50.4500


if "captured_lng" not in st.session_state:
    st.session_state.captured_lng = 30.5200


# =========================================================
# ВОССТАНОВЛЕНИЕ MAP STATE
# =========================================================

if "map_state" in st.query_params:

    try:

        raw_map_state = st.query_params["map_state"]

        parsed_map_state = (
            json.loads(raw_map_state)
            if raw_map_state
            else []
        )

        if isinstance(parsed_map_state, list):

            st.session_state.map_objects = parsed_map_state

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError
    ):
        pass


# =========================================================
# ПОЛНОЕ ОЧИЩЕНИЕ
# =========================================================

if "clear_all" in st.query_params:

    st.session_state.rkhb_points = []
    st.session_state.map_objects = []

    st.session_state.captured_lat = 50.4500
    st.session_state.captured_lng = 30.5200

    st.query_params.clear()

    st.rerun()


# =========================================================
# УДАЛЕНИЕ ТОЧКИ РАЗВЕДКИ
# =========================================================

if "delete_point_idx" in st.query_params:

    try:

        idx_to_del = int(
            st.query_params["delete_point_idx"]
        )

        if (
            0 <= idx_to_del
            < len(st.session_state.rkhb_points)
        ):
            st.session_state.rkhb_points.pop(
                idx_to_del
            )

        st.query_params.clear()

        st.rerun()

    except (
        ValueError,
        TypeError
    ):
        pass


# =========================================================
# КООРДИНАТЫ
# =========================================================

if (
    "click_lat" in st.query_params
    and "click_lng" in st.query_params
):

    try:

        st.session_state.captured_lat = float(
            st.query_params["click_lat"]
        )

        st.session_state.captured_lng = float(
            st.query_params["click_lng"]
        )

    except (
        ValueError,
        TypeError
    ):
        pass


# =========================================================
# ПРАВАЯ ПАНЕЛЬ
# =========================================================

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
📍 {st.session_state.captured_lat:.5f},
{st.session_state.captured_lng:.5f}
</div>
""",
        unsafe_allow_html=True,
    )


    # =====================================================
    # ТОЧКА РАЗВЕДКИ
    # =====================================================

    with st.expander(
        "➕ Параметри точки вимірювання",
        expanded=True
    ):

        m_type = st.radio(
            "Тип забруднення:",
            [
                "Радіоактивне",
                "Хімічне"
            ]
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
                step=0.01
            )

            r_uni = st.selectbox(
                "Одиниця виміру",
                [
                    "мкЗв/год",
                    "мЗв/год"
                ]
            )

            lbl = f"{r_val} {r_uni}"

            ico = SRC_DETECT_RADIATION

        else:

            c_sub = st.text_input(
                "Речовина",
                value="Іприт"
            )

            c_val = st.number_input(
                "Концентрація",
                value=0.10,
                step=0.01
            )

            c_uni = st.selectbox(
                "Одиниця виміру",
                [
                    "мг/м³",
                    "ppm"
                ]
            )

            lbl = (
                f"{c_sub} - "
                f"{c_val} {c_uni}"
            )

            ico = SRC_DETECT_CHEMICAL


        m_date = datetime.now().strftime(
            "%d.%m.%Y"
        )

        st.caption(
            f"📅 Дата фіксації (авто): {m_date}"
        )


        if st.button(
            "Нанести точку на карту",
            type="primary"
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


    # =====================================================
    # CSV
    # =====================================================

    st.write(
        "📊 **Імпорт бази даних розвідки**"
    )

    file = st.file_uploader(
        "Виберіть CSV файл:",
        type=["csv"],
        label_visibility="collapsed"
    )


    if file:

        try:

            df_csv = pd.read_csv(file)

            st.dataframe(
                df_csv.head(3),
                use_container_width=True
            )


            if st.button(
                "📥 Додати точки на карту з таблиці"
            ):

                df_csv.columns = [
                    col.strip().lower()
                    for col in df_csv.columns
                ]

                lat_col = (
                    "lat"
                    if "lat" in df_csv.columns
                    else None
                )

                lng_col = None

                if "lon" in df_csv.columns:
                    lng_col = "lon"

                elif "lng" in df_csv.columns:
                    lng_col = "lng"


                val_col = (
                    "value"
                    if "value" in df_csv.columns
                    else None
                )

                uni_col = (
                    "unit"
                    if "unit" in df_csv.columns
                    else None
                )

                tim_col = (
                    "time"
                    if "time" in df_csv.columns
                    else None
                )

                typ_col = (
                    "type"
                    if "type" in df_csv.columns
                    else None
                )

                sub_col = (
                    "substance"
                    if "substance" in df_csv.columns
                    else None
                )


                if lat_col and lng_col:

                    for _, row in df_csv.iterrows():

                        val_raw = (
                            str(row[val_col]).strip()
                            if (
                                val_col
                                and pd.notna(row[val_col])
                            )
                            else ""
                        )

                        uni_raw = (
                            str(row[uni_col]).strip()
                            if (
                                uni_col
                                and pd.notna(row[uni_col])
                            )
                            else ""
                        )

                        sub_raw = (
                            str(row[sub_col]).strip()
                            if (
                                sub_col
                                and pd.notna(row[sub_col])
                            )
                            else ""
                        )

                        type_str = (
                            str(row[typ_col])
                            .strip()
                            .lower()
                            if (
                                typ_col
                                and pd.notna(row[typ_col])
                            )
                            else ""
                        )


                        if sub_raw:

                            label_text = (
                                f"{sub_raw.capitalize()} - "
                                f"{val_raw} {uni_raw}"
                            )

                        else:

                            label_text = (
                                f"{val_raw} {uni_raw}"
                                .strip()
                            )


                        if not label_text:
                            label_text = "Точка розвідки"


                        date_text = (
                            str(row[tim_col]).strip()
                            if (
                                tim_col
                                and pd.notna(row[tim_col])
                            )
                            else datetime.now().strftime(
                                "%d.%m.%Y"
                            )
                        )


                        if (
                            "хім" in type_str
                            or "chemical" in type_str
                            or "мг/" in uni_raw
                            or "ppm" in uni_raw
                        ):

                            icon_url = (
                                SRC_DETECT_CHEMICAL
                            )

                        elif (
                            "біо" in type_str
                            or "biological" in type_str
                        ):

                            icon_url = (
                                SRC_DETECT_BIOLOGICAL
                            )

                        else:

                            icon_url = (
                                SRC_DETECT_RADIATION
                            )


                        try:

                            st.session_state.rkhb_points.append(
                                {
                                    "lat": float(row[lat_col]),
                                    "lng": float(row[lng_col]),
                                    "label": label_text,
                                    "date": date_text,
                                    "icon": icon_url,
                                }
                            )

                        except Exception:
                            continue


                    st.rerun()


        except Exception as e:

            st.error(
                f"Помилка: {str(e)}"
            )


    if st.session_state.rkhb_points:

        pts_only = [
            p
            for p in st.session_state.rkhb_points
            if "lat" in p
        ]

        if pts_only:

            df_view = pd.DataFrame(
                pts_only
            )

            st.dataframe(
                df_view[
                    [
                        "date",
                        "label",
                        "lat",
                        "lng"
                    ]
                ],
                use_container_width=True,
                height=110,
            )


# =========================================================
# JSON ДЛЯ КАРТИ
# =========================================================

points_json = json.dumps(
    st.session_state.rkhb_points,
    ensure_ascii=False
)

map_objects_json = json.dumps(
    st.session_state.map_objects,
    ensure_ascii=False
)


# =========================================================
# HTML КАРТЫ
# =========================================================

html_map_template = r"""
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Карта фактичної РХБ обстановки</title>

<link
rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<link
rel="stylesheet"
href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css"
/>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js"></script>


<style>

html,
body {

    margin: 0;
    padding: 0;

    height: 100%;

    font-family: Arial, sans-serif;

    background: white;

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

    background: white;

    color: black;

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


.btn-clear-all {

    background: #b71c1c !important;

    color: white !important;

    border-color: #880e4f !important;
}


.btn-autoroute {

    background: #FFD600 !important;

    color: black !important;

    border-color: #cca300 !important;
}


.btn-html {

    background: #dbeafe !important;

    color: #075985 !important;

    border-color: #0284c7 !important;
}


#windWidget {

    position: absolute;

    bottom: 15px;

    left: 10px;

    z-index: 1000;

    background:
        rgba(26,26,26,0.9);

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

    color: white;

    margin-top: 1px;

    font-weight: bold;
}


.route-label {

    background:
        rgba(0,0,0,0.85) !important;

    border:
        1px solid #d97706 !important;

    color: white !important;

    font-size: 11px !important;

    font-weight: bold !important;

    padding: 2px 6px !important;

    border-radius: 4px !important;

    white-space: nowrap !important;
}


.leaflet-div-icon {

    background: transparent !important;

    border: none !important;

    box-shadow: none !important;
}


.cbrn-military-lbl {

    font-family: Arial, sans-serif;

    font-size: 12px;

    font-weight: bold;

    color: black !important;

    text-align: center;

    display: inline-block;

    white-space: nowrap;

    line-height: 1.3;

    background: transparent !important;
}


.cbrn-line-divider {

    border-bottom:
        2px solid black !important;

    width: 100%;

    display: block;

    margin: 2px 0;
}


.cbrn-date-sub {

    font-size: 11px;

    font-weight: bold;

    color: black !important;

    display: block;
}


/* ==========================================
   МАРКЕРЫ НАЧАЛА / КОНЦА МАРШРУТА
   ========================================== */

.route-endpoint {

    width: 18px;

    height: 18px;

    border-radius: 50%;

    border: 3px solid white;

    box-shadow:
        0 0 0 2px #222,
        0 2px 5px rgba(0,0,0,0.5);

    text-align: center;

    font-size: 10px;

    font-weight: bold;

    line-height: 18px;

    color: white;
}


.route-start {

    background: #008000;
}


.route-finish {

    background: #d00000;
}


.route-end-label {

    background:
        rgba(0,0,0,0.85);

    color: white;

    border: 1px solid #555;

    padding: 2px 5px;

    border-radius: 3px;

    font-size: 10px;

    font-weight: bold;
}


/* PRINT */

@media print {

    #bottomControlsPanel,
    .leaflet-control-container,
    #windWidget {

        display: none !important;
    }

    #mapContainer {

        height: 95vh;

        border: none;
    }

    #map {

        height: 95vh;
    }
}

</style>

</head>


<body>


<div id="mapContainer">

    <div id="map"></div>

    <div id="windWidget">

        <div
            class="wind-arrow"
            id="arrow"
        >↑</div>

        <div
            class="wind-info"
            id="degInfo"
        >0°</div>

        <div
            class="wind-info"
            id="speedInfo"
        >0 м/с</div>

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
Точка рад. забруднення
</option>

<option value="ICO_DETECT_CHEMICAL">
Точка хім. забруднення
</option>

<option value="ICO_DETECT_BIOLOGICAL">
Точка біо. зараження
</option>

<option value="ICO_CBRN_POST">
Пост РХ спостереження
</option>

<option value="ICO_NUCLEAR_BLAST">
Епіцентр ядерного вибуху
</option>

<option value="ICO_BIOLOGICAL_HAZARD_SITE">
Біологічно небезпечний об'єкт
</option>

<option value="ICO_CHEMICAL_HAZARD_SITE">
Хімічно небезпечний об'єкт
</option>

<option value="ICO_RADIOACTIVE_SITE">
Радіаційно небезпечний об'єкт
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
id="reconRouteBtn"
style="
background:#fff3e0;
border-color:#d97706;
color:#b45309;
"
>
Маршрут (ручний)
</button>


<button
class="panel-btn"
id="textBtn"
style="
background:#e1f5fe;
border-color:#0288d1;
"
>
Текст
</button>


<button
class="panel-btn"
id="ellipseBtn"
style="
background:#efebe9;
border-color:#5d4037;
"
>
Еліпс AEGL
</button>


<button
class="panel-btn"
id="stopBtn"
>
ЗАВЕРШИТИ знак
</button>


<button
class="panel-btn btn-stop"
id="deleteModeBtn"
>
🗑️ ВИДАЛИТИ
</button>


<button
class="panel-btn btn-clear-all"
id="clearAllMapBtn"
>
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
id="buildAutoRouteBtn"
>
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
placeholder="Градуси"
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
id="applyMeteoBtn"
>
🌀 Застосувати
</button>


<!-- HTML -->

<button
class="panel-btn btn-html"
id="htmlBtn"
>
🌐 Зберегти HTML
</button>


<!-- PDF -->

<button
class="panel-btn"
style="
background:#ffcdd2;
border-color:#d32f2f;
"
id="printBtn"
>
🖨️ Друк / PDF
</button>

</div>

</div>


<script>


// ========================================================
// ДАННЫЕ PYTHON
// ========================================================

var DATA_FROM_PYTHON =
    __POINTS_JSON__;

var SAVED_MAP_OBJECTS =
    __MAP_OBJECTS_JSON__;


// ========================================================
// SVG
// ========================================================

var ico_biological_hazard_site =
    "__SRC_BIOLOGICAL_HAZARD_SITE__";

var ico_cbrn_contamination_area =
    "__SRC_CBRN_CONTAMINATION_AREA__";

var ico_cbrn_post =
    "__SRC_CBRN_POST__";

var ico_cbrn_recon_area =
    "__SRC_CBRN_RECON_AREA__";

var ico_chemical_hazard_site =
    "__SRC_CHEMICAL_HAZARD_SITE__";

var ico_decon_area_special =
    "__SRC_DECON_AREA_SPECIAL__";

var ico_decon_point_special =
    "__SRC_DECON_POINT_SPECIAL__";

var ico_detect_biological =
    "__SRC_DETECT_BIOLOGICAL__";

var ico_detect_chemical =
    "__SRC_DETECT_CHEMICAL__";

var ico_detect_radiation =
    "__SRC_DETECT_RADIATION__";

var ico_nuclear_blast =
    "__SRC_NUCLEAR_BLAST__";

var ico_radioactive_site =
    "__SRC_RADIOACTIVE_SITE__";


// ========================================================
// MAP
// ========================================================

var map = L.map(
    'map',
    {
        zoomControl: true
    }
).setView(
    [48.3,31.1],
    6
);


var osmLayer =
    L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            maxZoom: 19,
            attribution:
                '© OpenStreetMap'
        }
    );


var satLayer =
    L.tileLayer(
        'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        {
            attribution:
                '© Google'
        }
    );


osmLayer.addTo(map);


// ========================================================
// GEOMAN
// ========================================================

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

    measurements: {
        display: true
    },

    pathOptions: {

        color: '#d97706',

        fillColor: '#FFD600',

        fillOpacity: 0.35,

        weight: 4

    },

    pinToMarker: true

});


map.pm.setLang('uk');


// ========================================================
// LAYER CONTROL
// ========================================================

var baseMaps = {

    "🗺️ Карта OSM": osmLayer,

    "🛰️ Супутник Google": satLayer

};


var dateLayers = {};


var layerControl =
    L.control.layers(
        baseMaps,
        null,
        {
            collapsed: false
        }
    ).addTo(map);


// ========================================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ========================================================

function flattenLatLngs(raw) {

    if (!Array.isArray(raw))
        return [];

    if (
        raw.length > 0
        && Array.isArray(raw[0])
    ) {
        raw = raw[0];
    }

    return raw.filter(
        function(p) {

            return p
                && typeof p.lat === 'number'
                && typeof p.lng === 'number';

        }
    );
}


function sampleLatLngs(
    raw,
    maxPoints
) {

    var arr =
        flattenLatLngs(raw);

    if (
        arr.length <= maxPoints
    )
        return arr;

    var step =
        Math.ceil(
            arr.length / maxPoints
        );

    var out = [];

    for (
        var i = 0;
        i < arr.length;
        i += step
    ) {

        out.push(arr[i]);

    }

    if (
        out[out.length - 1]
        !== arr[arr.length - 1]
    ) {

        out.push(
            arr[arr.length - 1]
        );

    }

    return out;
}


function getTooltipText(layer) {

    if (layer.__cbrnLabel)
        return layer.__cbrnLabel;

    var tooltip =
        layer.getTooltip
        && layer.getTooltip();

    if (
        tooltip
        && tooltip.getContent
    )
        return tooltip.getContent();

    return '';
}


// ========================================================
// МАРКЕР НАЧАЛА МАРШРУТА
// ========================================================

function createRouteEndpoint(
    latlng,
    type,
    label
) {

    var isStart =
        type === 'start';


    var icon =
        L.divIcon({

            className: '',

            html:
                '<div class="route-endpoint '
                +
                (
                    isStart
                    ? 'route-start'
                    : 'route-finish'
                )
                +
                '">'
                +
                (
                    isStart
                    ? 'Н'
                    : 'К'
                )
                +
                '</div>',

            iconSize: [
                24,
                24
            ],

            iconAnchor: [
                12,
                12
            ]

        });


    var marker =
        L.marker(
            latlng,
            {
                icon: icon,
                zIndexOffset: 1000
            }
        ).addTo(map);


    marker.__cbrnType =
        'route_endpoint';

    marker.__routeEndpointType =
        type;

    marker.__routeEndpointLabel =
        label;


    marker.bindTooltip(
        label,
        {
            permanent: false,
            direction: 'top',
            className: 'route-end-label'
        }
    );


    attachRemovalClick(
        marker,
        null
    );


    return marker;
}


// ========================================================
// МАРКЕРЫ НАЧАЛА/КОНЦА РУЧНОГО МАРШРУТА
// ========================================================

function addRouteEndpoints(
    latlngs,
    routeId
) {

    if (
        !latlngs
        || latlngs.length < 2
    )
        return [];


    var first =
        latlngs[0];

    var last =
        latlngs[
            latlngs.length - 1
        ];


    var start =
        createRouteEndpoint(
            first,
            'start',
            'Початок маршруту'
        );


    var finish =
        createRouteEndpoint(
            last,
            'finish',
            'Кінець маршруту'
        );


    start.__routeId =
        routeId;

    finish.__routeId =
        routeId;


    return [
        start,
        finish
    ];
}


// ========================================================
// SAVE MAP OBJECTS
// ========================================================

function captureMapObjects() {

    var objects = [];

    map.eachLayer(
        function(layer) {

            if (
                !layer.__cbrnType
                || layer.__rkhbPoint
            )
                return;


            var type =
                layer.__cbrnType;


            // CIRCLE

            if (
                type === 'circle'
                && layer.getLatLng
                && layer.getRadius
            ) {

                var c =
                    layer.getLatLng();

                objects.push({

                    type: 'circle',

                    lat: c.lat,

                    lng: c.lng,

                    radius:
                        layer.getRadius(),

                    color:
                        layer.options.color
                        || '#d97706',

                    fillColor:
                        layer.options.fillColor
                        || '#FFD600',

                    fillOpacity:
                        layer.options.fillOpacity
                        !== undefined
                        ? layer.options.fillOpacity
                        : 0.35,

                    weight:
                        layer.options.weight
                        || 4,

                    label:
                        getTooltipText(layer)

                });

            }


            // POLYGON / ROUTE

            else if (
                (
                    type === 'polygon'
                    || type === 'route'
                )
                && layer.getLatLngs
            ) {

                var pts =
                    sampleLatLngs(
                        layer.getLatLngs(),
                        300
                    ).map(
                        function(p) {

                            return [
                                p.lat,
                                p.lng
                            ];

                        }
                    );


                if (
                    pts.length < 2
                )
                    return;


                objects.push({

                    type: type,

                    points: pts,

                    color:
                        layer.options.color
                        || '#d97706',

                    fillColor:
                        layer.options.fillColor
                        || '#FFD600',

                    fillOpacity:
                        layer.options.fillOpacity
                        !== undefined
                        ? layer.options.fillOpacity
                        : 0.35,

                    weight:
                        layer.options.weight
                        || 4,

                    dashArray:
                        layer.options.dashArray
                        || null,

                    label:
                        getTooltipText(layer)

                });

            }


            // AUTO ROUTE

            else if (
                type === 'autoRoute'
                && layer.__cbrnPoints
            ) {

                objects.push({

                    type: 'autoRoute',

                    points:
                        layer.__cbrnPoints,

                    color:
                        layer.options.color
                        || '#d97706',

                    weight:
                        layer.options.weight
                        || 4,

                    dashArray:
                        layer.options.dashArray
                        || '8, 8',

                    label:
                        getTooltipText(layer)

                });

            }


            // SIGN

            else if (
                type === 'sign'
                && layer.getLatLng
            ) {

                var s =
                    layer.getLatLng();

                objects.push({

                    type: 'sign',

                    lat: s.lat,

                    lng: s.lng,

                    icon:
                        layer.__cbrnIcon
                        || '',

                    size: [
                        32,
                        32
                    ]

                });

            }


            // TEXT

            else if (
                type === 'text'
                && layer.getLatLng
            ) {

                var t =
                    layer.getLatLng();

                objects.push({

                    type: 'text',

                    lat: t.lat,

                    lng: t.lng,

                    text:
                        layer.__cbrnText
                        || ''

                });

            }


            // ROUTE ENDPOINT

            else if (
                type === 'route_endpoint'
                && layer.getLatLng
            ) {

                var ep =
                    layer.getLatLng();


                objects.push({

                    type:
                        'route_endpoint',

                    lat:
                        ep.lat,

                    lng:
                        ep.lng,

                    endpointType:
                        layer.__routeEndpointType
                        || 'start',

                    label:
                        layer.__routeEndpointLabel
                        || ''

                });

            }

        }
    );


    return objects;
}


// ========================================================
// SAVE STATE TO STREAMLIT
// ========================================================

function saveMapState() {

    try {

        var state =
            captureMapObjects();

        var encoded =
            JSON.stringify(state);


        var url =
            new URL(
                window.parent.location.href
            );


        url.searchParams.set(
            'map_state',
            encoded
        );


        window.parent.history.replaceState(
            {},
            '',
            url
        );


        window.parent.postMessage(
            {
                type:
                    "streamlit:set_query_params",

                params:
                    {
                        map_state:
                            encoded
                    }
            },
            "*"
        );

    }

    catch (err) {

        console.warn(
            'Не вдалося зберегти обстановку карти:',
            err
        );

    }

}


// ========================================================
// УДАЛЕНИЕ
// ========================================================

function attachRemovalClick(
    layer,
    pointIndex
) {

    layer.on(
        'click',
        function(e) {

            if (
                map.pm.globalRemovalModeEnabled()
            ) {

                L.DomEvent.stopPropagation(e);

                map.removeLayer(layer);

                saveMapState();


                if (
                    pointIndex !== undefined
                    && pointIndex !== null
                ) {

                    var url =
                        new URL(
                            window.parent.location.href
                        );


                    url.searchParams.set(
                        'delete_point_idx',
                        pointIndex
                    );


                    window.parent.history.replaceState(
                        {},
                        '',
                        url
                    );


                    window.parent.postMessage(
                        {
                            type:
                                "streamlit:set_query_params",

                            params:
                                {
                                    delete_point_idx:
                                        pointIndex.toString()
                                }
                        },
                        "*"
                    );

                }

            }

        }
    );
}


// ========================================================
// СОЗДАНИЕ ГЕОМЕТРИИ
// ========================================================

map.on(
    'pm:create',
    function(e) {

        var layer =
            e.layer;


        if (
            e.shape === 'Line'
        ) {

            layer.__cbrnType =
                'route';


            var latlngs =
                layer.getLatLngs();


            var totalDist = 0;


            for (
                var i = 0;
                i < latlngs.length - 1;
                i++
            ) {

                totalDist +=
                    latlngs[i].distanceTo(
                        latlngs[i + 1]
                    );

            }


            var distKm =
                (
                    totalDist / 1000
                ).toFixed(2);


            var labelTxt =
                "Маршрут розвідки: "
                +
                distKm
                +
                " км";


            layer.__cbrnLabel =
                labelTxt;


            layer.setStyle({

                color: '#d97706',

                weight: 4,

                dashArray: '8, 8'

            });


            layer.bindTooltip(
                labelTxt,
                {
                    permanent: true,

                    direction: 'center',

                    className:
                        'route-label'
                }
            );


            // ==========================================
            // ГЛАВНОЕ — МАРКЕРЫ НАЧАЛА И КОНЦА
            // ==========================================

            addRouteEndpoints(
                latlngs,
                "manual_" + Date.now()
            );

        }


        if (
            e.shape === 'Circle'
        ) {

            layer.__cbrnType =
                'circle';


            var radius =
                layer.getRadius();


            var rTxt =
                radius >= 1000
                ? (
                    radius / 1000
                ).toFixed(2) + ' км'
                : Math.round(radius) + ' м';


            layer.__cbrnLabel =
                "Радіус: " + rTxt;


            layer.bindTooltip(
                layer.__cbrnLabel,
                {
                    permanent: true,

                    direction: 'center',

                    className:
                        'route-label'
                }
            );


            layer.on(
                'pm:change',
                function(ev) {

                    var newR =
                        ev.layer.getRadius();


                    var newTxt =
                        newR >= 1000
                        ? (
                            newR / 1000
                        ).toFixed(2)
                        + ' км'
                        : Math.round(newR)
                        + ' м';


                    ev.layer.__cbrnLabel =
                        "Радіус: "
                        + newTxt;


                    ev.layer.setTooltipContent(
                        ev.layer.__cbrnLabel
                    );


                    saveMapState();

                }
            );

        }

        else if (
            e.shape === 'Polygon'
        ) {

            layer.__cbrnType =
                'polygon';

        }

        else if (
            e.shape === 'Rectangle'
        ) {

            layer.__cbrnType =
                'polygon';

        }


        attachRemovalClick(
            layer,
            null
        );


        saveMapState();

    }
);


// ========================================================
// ТОЧКИ РАЗВЕДКИ PYTHON
// ========================================================

var inputPoints =
    DATA_FROM_PYTHON;


if (
    Array.isArray(inputPoints)
) {

    inputPoints.forEach(
        function(pt, index) {

            var dateStr =
                pt.date
                || "Базові дані";


            if (
                !dateLayers[dateStr]
            ) {

                dateLayers[dateStr] =
                    L.layerGroup()
                    .addTo(map);


                layerControl.addOverlay(
                    dateLayers[dateStr],
                    "📅 " + dateStr
                );

            }


            if (
                typeof pt.lat === 'number'
                &&
                typeof pt.lng === 'number'
            ) {

                var customIcon =
                    L.icon({

                        iconUrl:
                            pt.icon,

                        iconSize: [
                            32,
                            32
                        ],

                        iconAnchor: [
                            16,
                            16
                        ]

                    });


                var marker =
                    L.marker(
                        [
                            pt.lat,
                            pt.lng
                        ],
                        {
                            icon:
                                customIcon
                        }
                    );


                marker.__rkhbPoint =
                    true;


                var labelHtml =
                    "<div class='cbrn-military-lbl'>"
                    +
                    "<span>"
                    +
                    pt.label
                    +
                    "</span>"
                    +
                    "<div class='cbrn-line-divider'></div>"
                    +
                    "<span class='cbrn-date-sub'>"
                    +
                    dateStr
                    +
                    "</span>"
                    +
                    "</div>";


                marker.bindTooltip(
                    labelHtml,
                    {
                        permanent: true,

                        direction: 'bottom',

                        offset: [
                            0,
                            16
                        ],

                        className:
                            'leaflet-div-icon'
                    }
                );


                attachRemovalClick(
                    marker,
                    index
                );


                marker.addTo(
                    dateLayers[dateStr]
                );

            }

        }
    );

}


// ========================================================
// РЕЖИМЫ
// ========================================================

var activeIcon = "";

var textMode = false;

var ellipseMode = false;

var isReconMode = false;


function clearModes() {

    activeIcon = "";

    textMode = false;

    ellipseMode = false;

    isReconMode = false;


    document.getElementById(
        'signSelect'
    ).value = "";


    if (
        map.pm.globalDrawModeEnabled()
    ) {

        map.pm.disableDraw();

    }

}


// ========================================================
// ОЧИСТИТЬ КАРТУ
// ========================================================

document.getElementById(
    'clearAllMapBtn'
).onclick = function() {

    if (
        confirm(
            "Ви дійсно бажаєте очистити всі знаки та маршрути з карти?"
        )
    ) {

        map.eachLayer(
            function(layer) {

                if (
                    layer !== osmLayer
                    && layer !== satLayer
                ) {

                    map.removeLayer(layer);

                }

            }
        );


        Object.keys(
            dateLayers
        ).forEach(
            function(k) {

                layerControl.removeLayer(
                    dateLayers[k]
                );

            }
        );


        dateLayers = {};


        saveMapState();


        var url =
            new URL(
                window.parent.location.href
            );


        url.searchParams.set(
            'clear_all',
            '1'
        );


        window.parent.history.replaceState(
            {},
            '',
            url
        );


        window.parent.postMessage(
            {
                type:
                    "streamlit:set_query_params",

                params:
                    {
                        clear_all:
                            '1'
                    }
            },
            "*"
        );

    }

};


// ========================================================
// ГЕОКОДИРОВКА
// ========================================================

async function geocodePlaceJS(query) {

    if (!query)
        return null;


    query =
        query.trim();


    var parts =
        query.split(',');


    if (
        parts.length === 2
        &&
        !isNaN(parts[0])
        &&
        !isNaN(parts[1])
    ) {

        return {

            lat:
                parseFloat(
                    parts[0].trim()
                ),

            lng:
                parseFloat(
                    parts[1].trim()
                )

        };

    }


    var searchStr =
        (
            query
                .toLowerCase()
                .includes("україна")
            ||
            query
                .toLowerCase()
                .includes("ukraine")
        )
        ?
        query
        :
        query + ", Україна";


    try {

        var pUrl =
            "https://photon.komoot.io/api/?q="
            +
            encodeURIComponent(
                searchStr
            )
            +
            "&limit=1";


        var resP =
            await fetch(pUrl);


        var dataP =
            await resP.json();


        if (
            dataP
            &&
            dataP.features
            &&
            dataP.features.length > 0
        ) {

            var coordsP =
                dataP.features[0]
                    .geometry
                    .coordinates;


            return {

                lat:
                    coordsP[1],

                lng:
                    coordsP[0]

            };

        }

    }

    catch(e) {}


    try {

        var nUrl =
            "https://nominatim.openstreetmap.org/search?format=json&q="
            +
            encodeURIComponent(
                searchStr
            )
            +
            "&limit=1";


        var resN =
            await fetch(
                nUrl,
                {
                    headers:
                        {
                            'Accept-Language':
                                'uk,en'
                        }
                }
            );


        var dataN =
            await resN.json();


        if (
            dataN
            &&
            dataN.length > 0
        ) {

            return {

                lat:
                    parseFloat(
                        dataN[0].lat
                    ),

                lng:
                    parseFloat(
                        dataN[0].lon
                    )

            };

        }

    }

    catch(e) {}


    return null;

}


// ========================================================
// АВТОМАТИЧЕСКИЙ МАРШРУТ
// ========================================================

document.getElementById(
    'buildAutoRouteBtn'
).onclick = async function() {


    var inputVal =
        document
            .getElementById(
                'autoRouteInput'
            )
            .value
            .trim();


    if (!inputVal) {

        alert(
            "Введіть населені пункти через ';'"
        );

        return;

    }


    var pointsList =
        inputVal
            .split(';')
            .map(
                p => p.trim()
            )
            .filter(
                p => p.length > 0
            );


    if (
        pointsList.length < 2
    ) {

        alert(
            "Введіть як мінімум 2 населені пункти"
        );

        return;

    }


    var btn =
        document.getElementById(
            'buildAutoRouteBtn'
        );


    btn.innerText =
        "⏳ Пошук...";

    btn.disabled = true;


    var coords = [];

    var failedPoint = null;


    for (
        var p of pointsList
    ) {

        var c =
            await geocodePlaceJS(p);


        if (c) {

            coords.push(c);

        }

        else {

            failedPoint = p;

            break;

        }

    }


    if (failedPoint) {

        alert(
            "Не вдалося знайти: '"
            +
            failedPoint
            +
            "'"
        );


        btn.innerText =
            "Маршрут (автоматичний режим)";

        btn.disabled = false;

        return;

    }


    var coordsStr =
        coords
            .map(
                c =>
                    c.lng
                    +
                    ","
                    +
                    c.lat
            )
            .join(";");


    var osrmUrl =
        "https://router.project-osrm.org/route/v1/driving/"
        +
        coordsStr
        +
        "?overview=full&geometries=geojson";


    try {

        var res =
            await fetch(
                osrmUrl
            );


        var resData =
            await res.json();


        if (
            resData.code === 'Ok'
        ) {

            var routeData =
                resData.routes[0];


            var distKm =
                (
                    routeData.distance
                    / 1000
                ).toFixed(2);


            var durMin =
                Math.round(
                    routeData.duration
                    / 60
                );


            var labelName =
                "Маршрут: "
                +
                pointsList.join(
                    " ➔ "
                )
                +
                " ("
                +
                distKm
                +
                " км, ~"
                +
                durMin
                +
                " хв)";


            var routePoints =
                routeData.geometry
                    .coordinates
                    .map(
                        function(c) {

                            return [
                                c[1],
                                c[0]
                            ];

                        }
                    );


            var rLayer =
                L.geoJSON(
                    routeData.geometry,
                    {
                        style:
                            {
                                color:
                                    "#d97706",

                                weight:
                                    4,

                                dashArray:
                                    "8, 8"
                            }
                    }
                ).addTo(map);


            rLayer.__cbrnType =
                'autoRoute';


            rLayer.__cbrnLabel =
                labelName;


            rLayer.__cbrnPoints =
                routePoints;


            rLayer.bindTooltip(
                labelName,
                {
                    permanent: true,

                    direction: 'center',

                    className:
                        'route-label'
                }
            );


            attachRemovalClick(
                rLayer,
                null
            );


            // ==========================================
            // МАРКЕР НАЧАЛА
            // ==========================================

            createRouteEndpoint(
                routePoints[0],
                'start',
                "Початок маршруту: "
                +
                pointsList[0]
            );


            // ==========================================
            // МАРКЕР КОНЦА
            // ==========================================

            createRouteEndpoint(
                routePoints[
                    routePoints.length - 1
                ],
                'finish',
                "Кінець маршруту: "
                +
                pointsList[
                    pointsList.length - 1
                ]
            );


            map.fitBounds(
                rLayer.getBounds(),
                {
                    padding:
                        [30,30]
                }
            );


            saveMapState();

        }

        else {

            alert(
                "Помилка побудови маршруту."
            );

        }

    }

    catch(err) {

        alert(
            "Помилка: "
            +
            err
        );

    }

    finally {

        btn.innerText =
            "Маршрут (автоматичний режим)";

        btn.disabled = false;

    }

};


// ========================================================
// УМОВНІ ЗНАКИ
// ========================================================

document.getElementById(
    'signSelect'
).onchange = function(e) {

    var val =
        e.target.value;


    if (
        val ===
        "ICO_DETECT_RADIATION"
    )
        activeIcon =
            ico_detect_radiation;


    else if (
        val ===
        "ICO_DETECT_CHEMICAL"
    )
        activeIcon =
            ico_detect_chemical;


    else if (
        val ===
        "ICO_DETECT_BIOLOGICAL"
    )
        activeIcon =
            ico_detect_biological;


    else if (
        val ===
        "ICO_CBRN_POST"
    )
        activeIcon =
            ico_cbrn_post;


    else if (
        val ===
        "ICO_NUCLEAR_BLAST"
    )
        activeIcon =
            ico_nuclear_blast;


    else if (
        val ===
        "ICO_BIOLOGICAL_HAZARD_SITE"
    )
        activeIcon =
            ico_biological_hazard_site;


    else if (
        val ===
        "ICO_CHEMICAL_HAZARD_SITE"
    )
        activeIcon =
            ico_chemical_hazard_site;


    else if (
        val ===
        "ICO_RADIOACTIVE_SITE"
    )
        activeIcon =
            ico_radioactive_site;


    else if (
        val ===
        "ICO_CBRN_CONTAMINATION_AREA"
    )
        activeIcon =
            ico_cbrn_contamination_area;


    else if (
        val ===
        "ICO_CBRN_RECON_AREA"
    )
        activeIcon =
            ico_cbrn_recon_area;


    else if (
        val ===
        "ICO_DECON_AREA_SPECIAL"
    )
        activeIcon =
            ico_decon_area_special;


    else if (
        val ===
        "ICO_DECON_POINT_SPECIAL"
    )
        activeIcon =
            ico_decon_point_special;


    else
        activeIcon = "";


    textMode = false;

    ellipseMode = false;

    isReconMode = false;

};


// ========================================================
// РУЧНОЙ МАРШРУТ
// ========================================================

document.getElementById(
    'reconRouteBtn'
).onclick = function() {

    clearModes();

    isReconMode = true;


    map.pm.enableDraw(
        'Line',
        {
            snappable: true,

            pathOptions:
                {
                    color:
                        '#d97706',

                    weight:
                        4,

                    dashArray:
                        '8, 8'
                }
        }
    );

};


// ========================================================
// ТЕКСТ
// ========================================================

document.getElementById(
    'textBtn'
).onclick = function() {

    clearModes();

    textMode = true;

};


// ========================================================
// AEGL
// ========================================================

document.getElementById(
    'ellipseBtn'
).onclick = function() {

    clearModes();

    ellipseMode = true;

};


// ========================================================
// СТОП
// ========================================================

document.getElementById(
    'stopBtn'
).onclick = function() {

    clearModes();


    if (
        map.pm.globalRemovalModeEnabled()
    ) {

        map.pm.toggleGlobalRemovalMode();

    }

};


// ========================================================
// УДАЛЕНИЕ
// ========================================================

document.getElementById(
    'deleteModeBtn'
).onclick = function() {

    clearModes();

    map.pm.toggleGlobalRemovalMode();

};


// ========================================================
// ВЕТЕР
// ========================================================

document.getElementById(
    'applyMeteoBtn'
).onclick = function() {

    var windFromDeg =
        parseFloat(
            document.getElementById(
                'windInput'
            ).value
        )
        || 0;


    var windSpeed =
        parseFloat(
            document.getElementById(
                'windSpeedInput'
            ).value
        )
        || 0;


    var blowToDeg =
        (
            windFromDeg + 180
        ) % 360;


    document.getElementById(
        'arrow'
    ).style.transform =
        'rotate('
        +
        blowToDeg
        +
        'deg)';


    document.getElementById(
        'degInfo'
    ).innerText =
        windFromDeg
        +
        '°';


    document.getElementById(
        'speedInfo'
    ).innerText =
        windSpeed
        +
        ' м/с';

};


// ========================================================
// HTML EXPORT
// ========================================================

document.getElementById(
    'htmlBtn'
).onclick = function() {

    try {

        var mapObjects =
            captureMapObjects();


        var exportData = {

            title:
                "КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ",

            created:
                new Date().toLocaleString(
                    'uk-UA'
                ),

            center:
                map.getCenter(),

            zoom:
                map.getZoom(),

            objects:
                mapObjects,

            points:
                DATA_FROM_PYTHON

        };


        var exportJson =
            JSON.stringify(
                exportData
            );


        var html = `<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Карта фактичної РХБ обстановки</title>

<style>

body {
    margin:0;
    font-family:Arial,sans-serif;
    background:#fff;
}

.header {
    padding:12px;
    font-size:22px;
    font-weight:bold;
    border-bottom:1px solid #ccc;
}

.info {
    padding:8px 12px;
    color:#555;
    font-size:13px;
}

pre {
    white-space:pre-wrap;
    word-break:break-word;
    margin:12px;
    padding:12px;
    background:#f3f3f3;
    border:1px solid #ddd;
    border-radius:6px;
}

</style>

</head>

<body>

<div class="header">
КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ
</div>

<div class="info">
Експорт оперативної обстановки.
Дата формування:
${new Date().toLocaleString('uk-UA')}
</div>

<pre>${escapeHtml(
            JSON.stringify(
                exportData,
                null,
                2
            )
        )}</pre>

</body>
</html>`;


        var blob =
            new Blob(
                [html],
                {
                    type:
                        'text/html;charset=utf-8'
                }
            );


        var url =
            URL.createObjectURL(
                blob
            );


        var a =
            document.createElement(
                'a'
            );


        a.href = url;


        a.download =
            'RHB_obstanovka_'
            +
            new Date()
                .toISOString()
                .slice(0,19)
                .replace(
                    /:/g,
                    '-'
                )
            +
            '.html';


        document.body.appendChild(a);

        a.click();

        document.body.removeChild(a);


        URL.revokeObjectURL(url);

    }

    catch(err) {

        alert(
            "Помилка збереження HTML: "
            +
            err
        );

    }

};


function escapeHtml(text) {

    return text
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


// ========================================================
// PDF
// ========================================================

document.getElementById(
    'printBtn'
).onclick = function() {

    window.print();

};


// ========================================================
// КЛИК ПО КАРТЕ
// ========================================================

map.on(
    'click',
    function(e) {

        var lat =
            e.latlng.lat;

        var lng =
            e.latlng.lng;


        if (
            window.parent
            &&
            window.parent.document
        ) {

            var targetBox =
                window.parent.document
                    .getElementById(
                        'pythonCoordBox'
                    );


            if (targetBox) {

                targetBox.innerHTML =
                    "📍 "
                    +
                    lat.toFixed(5)
                    +
                    " , "
                    +
                    lng.toFixed(5);

            }

        }


        if (
            !activeIcon
            &&
            !textMode
            &&
            !ellipseMode
            &&
            !isReconMode
        ) {

            if (
                map.pm.globalRemovalModeEnabled()
            )
                return;


            var url =
                new URL(
                    window.parent.location.href
                );


            url.searchParams.set(
                'click_lat',
                lat.toFixed(5)
            );


            url.searchParams.set(
                'click_lng',
                lng.toFixed(5)
            );


            window.parent.history.replaceState(
                {},
                '',
                url
            );


            window.parent.postMessage(
                {
                    type:
                        "streamlit:set_query_params",

                    params:
                        {
                            click_lat:
                                lat.toFixed(5),

                            click_lng:
                                lng.toFixed(5)
                        }
                },
                "*"
            );


            return;

        }


        // ===============================================
        // УСЛОВНЫЙ ЗНАК
        // ===============================================

        if (activeIcon) {

            var m =
                L.marker(
                    e.latlng,
                    {
                        icon:
                            L.icon(
                                {
                                    iconUrl:
                                        activeIcon,

                                    iconSize:
                                        [
                                            32,
                                            32
                                        ],

                                    iconAnchor:
                                        [
                                            16,
                                            16
                                        ]
                                }
                            )
                    }
                ).addTo(map);


            m.__cbrnType =
                'sign';


            m.__cbrnIcon =
                activeIcon;


            attachRemovalClick(
                m,
                null
            );


            saveMapState();

        }


        // ===============================================
        // ТЕКСТ
        // ===============================================

        if (textMode) {

            var txt =
                prompt(
                    "Введіть оперативно-тактичний підпис:"
                );


            if (txt) {

                var tm =
                    L.marker(
                        e.latlng,
                        {
                            icon:
                                L.divIcon(
                                    {
                                        className:
                                            'leaflet-div-icon',

                                        html:
                                            "<span class='cbrn-military-lbl' style='font-size:13px;'>"
                                            +
                                            txt
                                            +
                                            "</span>"
                                    }
                                )
                        }
                    ).addTo(map);


                tm.__cbrnType =
                    'text';


                tm.__cbrnText =
                    txt;


                attachRemovalClick(
                    tm,
                    null
                );


                saveMapState();

            }

        }


        // ===============================================
        // AEGL
        // ===============================================

        if (ellipseMode) {

            var inputL =
                prompt(
                    "Введіть загальну довжину зони розповсюдження L (у метрах):",
                    "4000"
                );


            if (!inputL)
                return;


            var totalLength =
                parseFloat(
                    inputL
                );


            if (
                isNaN(totalLength)
                ||
                totalLength <= 0
            )
                return;


            var rX =
                totalLength / 2.0;


            var windFromDeg =
                parseFloat(
                    document
                        .getElementById(
                            'windInput'
                        )
                        .value
                )
                || 0;


            var windSpeed =
                parseFloat(
                    document
                        .getElementById(
                            'windSpeedInput'
                        )
                        .value
                )
                || 0;


            var widthFactor =
                0.40;


            if (
                windSpeed <= 1.5
            ) {

                widthFactor = 0.40;

            }

            else if (
                windSpeed <= 4.0
            ) {

                widthFactor = 0.25;

            }

            else {

                widthFactor = 0.15;

            }


            var rY =
                rX * widthFactor;


            var groupId =
                "aegl_group_"
                +
                Date.now();


            var shapes = [

                {
                    radiusX:
                        rX,

                    radiusY:
                        rY,

                    level:
                        "AEGL-1",

                    color:
                        "#ffcc00",

                    opacity:
                        0.25,

                    groupId:
                        groupId
                },

                {
                    radiusX:
                        rX * 0.6,

                    radiusY:
                        rY * 0.6,

                    level:
                        "AEGL-2",

                    color:
                        "#ff9900",

                    opacity:
                        0.40,

                    groupId:
                        groupId
                },

                {
                    radiusX:
                        rX * 0.3,

                    radiusY:
                        rY * 0.3,

                    level:
                        "AEGL-3",

                    color:
                        "#cc0000",

                    opacity:
                        0.65,

                    groupId:
                        groupId
                }

            ];


            renderAeglGroup(
                e.latlng,
                shapes,
                windFromDeg,
                windSpeed,
                totalLength
            );


            clearModes();

        }

    }
);


// ========================================================
// AEGL ОТРИСОВКА
// ========================================================

function renderAeglGroup(
    ellipseCenter,
    shapes,
    windFromDeg,
    windSpeed,
    totalL
) {

    shapes.sort(
        function(a,b) {

            return b.radiusX
                - a.radiusX;

        }
    );


    var blowToDeg =
        (
            windFromDeg + 180
        ) % 360;


    var blowToRad =
        blowToDeg
        *
        Math.PI
        /
        180.0;


    shapes.forEach(
        function(s) {

            var points = [];


            for (
                var i = 0;
                i <= 64;
                i++
            ) {

                var angle =
                    (
                        i / 64.0
                    )
                    *
                    2.0
                    *
                    Math.PI;


                var x =
                    s.radiusY
                    *
                    Math.cos(
                        angle
                    );


                var y =
                    s.radiusX
                    *
                    Math.sin(
                        angle
                    );


                var rotatedDx =
                    x
                    *
                    Math.cos(
                        blowToRad
                    )
                    +
                    (
                        y
                        +
                        s.radiusX
                    )
                    *
                    Math.sin(
                        blowToRad
                    );


                var rotatedDy =
                    -x
                    *
                    Math.sin(
                        blowToRad
                    )
                    +
                    (
                        y
                        +
                        s.radiusX
                    )
                    *
                    Math.cos(
                        blowToRad
                    );


                var latOffset =
                    rotatedDy
                    /
                    111320.0;


                var lngOffset =
                    rotatedDx
                    /
                    (
                        111320.0
                        *
                        Math.cos(
                            ellipseCenter.lat
                            *
                            Math.PI
                            /
                            180.0
                        )
                    );


                points.push(
                    [
                        ellipseCenter.lat
                        +
                        latOffset,

                        ellipseCenter.lng
                        +
                        lngOffset
                    ]
                );

            }


            var poly =
                L.polygon(
                    points,
                    {

                        color:
                            'black',

                        weight:
                            1,

                        fillColor:
                            s.color,

                        fillOpacity:
                            s.opacity

                    }
                ).addTo(map);


            var infoTxt =
                "<b>"
                +
                s.level
                +
                "</b><br>"
                +
                "Довжина зони: "
                +
                Math.round(
                    s.radiusX * 2
                )
                +
                " м<br>"
                +
                "Ширина: "
                +
                Math.round(
                    s.radiusY * 2
                )
                +
                " м<br>"
                +
                "Вітер (звідки): "
                +
                windFromDeg
                +
                "°, "
                +
                windSpeed
                +
                " м/с";


            poly.__cbrnType =
                'polygon';


            poly.__cbrnLabel =
                infoTxt;


            poly.bindTooltip(
                infoTxt,
                {
                    permanent: false,

                    direction: 'center'
                }
            );


            attachRemovalClick(
                poly,
                null
            );

        }
    );


    saveMapState();

}


// ========================================================
// RESTORE MAP OBJECTS
// ========================================================

function restoreMapObjects(
    objects
) {

    if (
        !Array.isArray(objects)
    )
        return;


    objects.forEach(
        function(obj) {

            try {

                // ========================================
                // CIRCLE
                // ========================================

                if (
                    obj.type === 'circle'
                ) {

                    var cLayer =
                        L.circle(
                            [
                                obj.lat,
                                obj.lng
                            ],
                            {

                                radius:
                                    obj.radius,

                                color:
                                    obj.color
                                    || '#d97706',

                                fillColor:
                                    obj.fillColor
                                    || '#FFD600',

                                fillOpacity:
                                    obj.fillOpacity
                                    !== undefined
                                    ?
                                    obj.fillOpacity
                                    :
                                    0.35,

                                weight:
                                    obj.weight
                                    || 4

                            }
                        ).addTo(map);


                    cLayer.__cbrnType =
                        'circle';


                    cLayer.__cbrnLabel =
                        obj.label
                        || '';


                    if (
                        cLayer.__cbrnLabel
                    ) {

                        cLayer.bindTooltip(
                            cLayer.__cbrnLabel,
                            {
                                permanent:
                                    true,

                                direction:
                                    'center',

                                className:
                                    'route-label'
                            }
                        );

                    }


                    attachRemovalClick(
                        cLayer,
                        null
                    );

                }


                // ========================================
                // POLYGON
                // ========================================

                else if (
                    obj.type === 'polygon'
                ) {

                    var pLayer =
                        L.polygon(
                            obj.points
                            || [],
                            {

                                color:
                                    obj.color
                                    || 'black',

                                weight:
                                    obj.weight
                                    || 1,

                                fillColor:
                                    obj.fillColor
                                    || '#FFD600',

                                fillOpacity:
                                    obj.fillOpacity
                                    !== undefined
                                    ?
                                    obj.fillOpacity
                                    :
                                    0.35

                            }
                        ).addTo(map);


                    pLayer.__cbrnType =
                        'polygon';


                    pLayer.__cbrnLabel =
                        obj.label
                        || '';


                    if (
                        pLayer.__cbrnLabel
                    ) {

                        pLayer.bindTooltip(
                            pLayer.__cbrnLabel,
                            {
                                permanent:
                                    false,

                                direction:
                                    'center'
                            }
                        );

                    }


                    attachRemovalClick(
                        pLayer,
                        null
                    );

                }


                // ========================================
                // ROUTE
                // ========================================

                else if (
                    obj.type === 'route'
                    ||
                    obj.type === 'autoRoute'
                ) {

                    var rRestored =
                        L.polyline(
                            obj.points
                            || [],
                            {

                                color:
                                    obj.color
                                    || '#d97706',

                                weight:
                                    obj.weight
                                    || 4,

                                dashArray:
                                    obj.dashArray
                                    || '8, 8'

                            }
                        ).addTo(map);


                    rRestored.__cbrnType =
                        obj.type;


                    rRestored.__cbrnLabel =
                        obj.label
                        || '';


                    if (
                        rRestored.__cbrnLabel
                    ) {

                        rRestored.bindTooltip(
                            rRestored.__cbrnLabel,
                            {
                                permanent:
                                    true,

                                direction:
                                    'center',

                                className:
                                    'route-label'
                            }
                        );

                    }


                    attachRemovalClick(
                        rRestored,
                        null
                    );

                }


                // ========================================
                // SIGN
                // ========================================

                else if (
                    obj.type === 'sign'
                ) {

                    var sRestored =
                        L.marker(
                            [
                                obj.lat,
                                obj.lng
                            ],
                            {

                                icon:
                                    L.icon(
                                        {

                                            iconUrl:
                                                obj.icon,

                                            iconSize:
                                                obj.size
                                                || [
                                                    32,
                                                    32
                                                ],

                                            iconAnchor:
                                                [
                                                    16,
                                                    16
                                                ]

                                        }
                                    )

                            }
                        ).addTo(map);


                    sRestored.__cbrnType =
                        'sign';


                    sRestored.__cbrnIcon =
                        obj.icon
                        || '';


                    attachRemovalClick(
                        sRestored,
                        null
                    );

                }


                // ========================================
                // TEXT
                // ========================================

                else if (
                    obj.type === 'text'
                ) {

                    var tRestored =
                        L.marker(
                            [
                                obj.lat,
                                obj.lng
                            ],
                            {

                                icon:
                                    L.divIcon(
                                        {

                                            className:
                                                'leaflet-div-icon',

                                            html:
                                                "<span class='cbrn-military-lbl' style='font-size:13px;'>"
                                                +
                                                obj.text
                                                +
                                                "</span>"

                                        }
                                    )

                            }
                        ).addTo(map);


                    tRestored.__cbrnType =
                        'text';


                    tRestored.__cbrnText =
                        obj.text
                        || '';


                    attachRemovalClick(
                        tRestored,
                        null
                    );

                }


                // ========================================
                // МАРКЕР НАЧАЛА / КОНЦА
                // ========================================

                else if (
                    obj.type ===
                    'route_endpoint'
                ) {

                    var endpoint =
                        createRouteEndpoint(
                            [
                                obj.lat,
                                obj.lng
                            ],

                            obj.endpointType
                            || 'start',

                            obj.label
                            || (
                                obj.endpointType
                                === 'start'
                                ?
                                'Початок маршруту'
                                :
                                'Кінець маршруту'
                            )
                        );


                    endpoint.__routeId =
                        obj.routeId
                        || null;

                }

            }

            catch(restoreErr) {

                console.warn(
                    "Помилка відновлення об'єкта карти:",
                    restoreErr
                );

            }

        }
    );

}


// ========================================================
// ВОССТАНОВЛЕНИЕ
// ========================================================

restoreMapObjects(
    SAVED_MAP_OBJECTS
);


</script>

</body>

</html>
"""


# =========================================================
# ПОДСТАНОВКА ДАННЫХ
# =========================================================

rendered_html = (
    html_map_template

    .replace(
        "__POINTS_JSON__",
        points_json
    )

    .replace(
        "__MAP_OBJECTS_JSON__",
        map_objects_json
    )

    .replace(
        "__SRC_BIOLOGICAL_HAZARD_SITE__",
        SRC_BIOLOGICAL_HAZARD_SITE
    )

    .replace(
        "__SRC_CBRN_CONTAMINATION_AREA__",
        SRC_CBRN_CONTAMINATION_AREA
    )

    .replace(
        "__SRC_CBRN_POST__",
        SRC_CBRN_POST
    )

    .replace(
        "__SRC_CBRN_RECON_AREA__",
        SRC_CBRN_RECON_AREA
    )

    .replace(
        "__SRC_CHEMICAL_HAZARD_SITE__",
        SRC_CHEMICAL_HAZARD_SITE
    )

    .replace(
        "__SRC_DECON_AREA_SPECIAL__",
        SRC_DECON_AREA_SPECIAL
    )

    .replace(
        "__SRC_DECON_POINT_SPECIAL__",
        SRC_DECON_POINT_SPECIAL
    )

    .replace(
        "__SRC_DETECT_BIOLOGICAL__",
        SRC_DETECT_BIOLOGICAL
    )

    .replace(
        "__SRC_DETECT_CHEMICAL__",
        SRC_DETECT_CHEMICAL
    )

    .replace(
        "__SRC_DETECT_RADIATION__",
        SRC_DETECT_RADIATION
    )

    .replace(
        "__SRC_NUCLEAR_BLAST__",
        SRC_NUCLEAR_BLAST
    )

    .replace(
        "__SRC_RADIOACTIVE_SITE__",
        SRC_RADIOACTIVE_SITE
    )
)


# =========================================================
# ВЫВОД КАРТЫ
# =========================================================

with col_map:

    components.html(
        rendered_html,
        height=720,
        scrolling=False
    )
