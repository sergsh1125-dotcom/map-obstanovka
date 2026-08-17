import base64
import json
import os
import requests
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Платформа ХБРЯ", layout="wide")

st.markdown(
    """
<style>
#MainMenu, footer, header {visibility: hidden;}

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

st.markdown(
    "<div class='custom-header'>КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ</div>",
    unsafe_allow_html=True,
)

col_map, col_gui = st.columns([3, 1])

GITHUB_USER = "sergsh1125-dotcom"
GITHUB_REPO = "map-obstanovka"
GITHUB_BRANCH = "main"
GITHUB_BASE_URL = f"https://cdn.jsdelivr.net/gh/{GITHUB_USER}/{GITHUB_REPO}@{GITHUB_BRANCH}/assets/svg"

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

# ІНІЦІАЛІЗАЦІЯ СТАНІВ
if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = []

if "routes_list" not in st.session_state:
    st.session_state.routes_list = []

if "captured_lat" not in st.session_state:
    st.session_state.captured_lat = 50.4500
if "captured_lng" not in st.session_state:
    st.session_state.captured_lng = 30.5200

# ОБРОБКА ДАНИХ З URL
if "add_route_data" in st.query_params:
    try:
        r_data = json.loads(st.query_params["add_route_data"])
        st.session_state.routes_list.append(r_data)
        st.query_params.clear()
        st.rerun()
    except Exception:
        pass

if "clear_all" in st.query_params:
    st.session_state.rkhb_points = []
    st.session_state.routes_list = []
    st.session_state.captured_lat = 50.4500
    st.session_state.captured_lng = 30.5200
    st.query_params.clear()
    st.rerun()

if "delete_point_idx" in st.query_params:
    try:
        idx_to_del = int(st.query_params["delete_point_idx"])
        if 0 <= idx_to_del < len(st.session_state.rkhb_points):
            st.session_state.rkhb_points.pop(idx_to_del)
        st.query_params.clear()
        st.rerun()
    except (ValueError, TypeError):
        pass

if "delete_route_idx" in st.query_params:
    try:
        idx_r_del = int(st.query_params["delete_route_idx"])
        if 0 <= idx_r_del < len(st.session_state.routes_list):
            st.session_state.routes_list.pop(idx_r_del)
        st.query_params.clear()
        st.rerun()
    except (ValueError, TypeError):
        pass

if "click_lat" in st.query_params and "click_lng" in st.query_params:
    try:
        st.session_state.captured_lat = float(st.query_params["click_lat"])
        st.session_state.captured_lng = float(st.query_params["click_lng"])
    except (ValueError, TypeError):
        pass

# ГЕОКОДИНГ ТА ПОБУДОВА МАРШРУТУ OSRM
def geocode_place_py(query):
    query = query.strip()
    if not query:
        return None
    
    parts = query.split(',')
    if len(parts) == 2:
        try:
            return {"lat": float(parts[0].strip()), "lng": float(parts[1].strip())}
        except ValueError:
            pass
            
    search_str = query if ("україна" in query.lower() or "ukraine" in query.lower()) else f"{query}, Україна"
    headers = {'User-Agent': 'CBRN_Map_App/1.0'}
    
    try:
        res = requests.get(f"https://photon.komoot.io/api/?q={requests.utils.quote(search_str)}&limit=1", headers=headers, timeout=5)
        data = res.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return {"lat": coords[1], "lng": coords[0]}
    except Exception:
        pass

    try:
        res = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&q={requests.utils.quote(search_str)}&limit=1", headers=headers, timeout=5)
        data = res.json()
        if data:
            return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
    except Exception:
        pass

    return None

def build_autoroute_py(points_str):
    names = [p.strip() for p in points_str.split(';') if p.strip()]
    if len(names) < 2:
        return None, "Введіть як мінімум 2 населені пункти!"
    
    coords = []
    for name in names:
        c = geocode_place_py(name)
        if not c:
            return None, f"Не вдалося знайти координати для: '{name}'"
        coords.append(c)
        
    coords_str = ";".join([f"{c['lng']},{c['lat']}" for c in coords])
    osrm_url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    
    try:
        res = requests.get(osrm_url, timeout=10)
        res_data = res.json()
        if res_data.get("code") == "Ok":
            route_data = res_data["routes"][0]
            dist_km = round(route_data["distance"] / 1000, 2)
            dur_min = round(route_data["duration"] / 60)
            label_name = f"Маршрут: {' ➔ '.join(names)} ({dist_km} км, ~{dur_min} хв)"
            
            # Конвертуємо GeoJSON [lon, lat] у Leaflet [lat, lon]
            raw_coords = route_data["geometry"]["coordinates"]
            latlng_coords = [[c[1], c[0]] for c in raw_coords]
            
            return {
                "type": "manual",
                "coords": latlng_coords,
                "label": label_name
            }, None
        else:
            return None, "Помилка побудови маршруту сервером OSRM."
    except Exception as e:
        return None, f"Помилка мережі при побудові маршруту: {str(e)}"

# ==========================================
# ПАНЕЛЬ УПРАВЛІННЯ
# ==========================================
with col_gui:
    st.subheader("⚙️ ПАНЕЛЬ УПРАВЛІННЯ")
    st.markdown(
        "<div class='info-text'>ℹ️ Для вибору координат клікніть мишкою на карті.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div id='pythonCoordBox' class='coord-box'>📍 {st.session_state.captured_lat:.5f} , {st.session_state.captured_lng:.5f}</div>",
        unsafe_allow_html=True,
    )

    # 1. НАНОСЕННЯ ТОЧОК ВИМІРЮВАННЯ
    with st.expander("➕ Параметри точки вимірювання", expanded=True):
        m_type = st.radio("Тип забруднення:", ["Радіоактивне", "Хімічне"], key="m_type_radio")
        m_lat = st.number_input("Широта (Lat)", value=st.session_state.captured_lat, format="%.5f", key="m_lat_input")
        m_lon = st.number_input("Довгота (Lon)", value=st.session_state.captured_lng, format="%.5f", key="m_lon_input")

        if m_type == "Радіоактивне":
            r_val = st.number_input("Потужність дози", value=0.15, step=0.01, key="r_val_input")
            r_uni = st.selectbox("Одиниця виміру", ["мкЗв/год", "мЗв/год", "Р/год", "мР/год"], key="r_uni_select")
            lbl = f"{r_val} {r_uni}"
            ico = SRC_DETECT_RADIATION
        else:
            c_sub = st.text_input("Речовина", value="Іприт", key="c_sub_input")
            c_val = st.number_input("Концентрація", value=0.10, step=0.01, key="c_val_input")
            c_uni = st.selectbox("Одиниця виміру", ["мг/м³", "ppm", "мг/л"], key="c_uni_select")
            lbl = f"{c_sub} - {c_val} {c_uni}"
            ico = SRC_DETECT_CHEMICAL

        m_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        st.caption(f"📅 Дата та час фіксації: {m_date}")

        if st.button("📍 Нанести точку на карту", type="primary", use_container_width=True):
            st.session_state.rkhb_points.append({
                "lat": float(m_lat),
                "lng": float(m_lon),
                "label": str(lbl),
                "date": datetime.now().strftime("%d.%m.%Y"),
                "icon": str(ico),
            })
            st.success(f"Точку '{lbl}' успішно додано!")
            st.rerun()

    # 2. АВТОМАТИЧНИЙ МАРШРУТ
    with st.expander("🚗 Побудова автоматичного маршруту", expanded=False):
        auto_route_input = st.text_input("Населені пункти (через ';'):", value="Київ; Фастів; Житомир", key="auto_route_txt")
        if st.button("🛣️ Побудувати маршрут", use_container_width=True):
            with st.spinner("Запит геоданих та розрахунок OSRM..."):
                route_obj, err_msg = build_autoroute_py(auto_route_input)
                if err_msg:
                    st.error(err_msg)
                else:
                    st.session_state.routes_list.append(route_obj)
                    st.success("Маршрут успішно нанесено!")
                    st.rerun()

    # 3. ІМПОРТ CSV
    with st.expander("📊 Імпорт бази даних розвідки (CSV)", expanded=False):
        file = st.file_uploader("Виберіть CSV файл:", type=["csv"], label_visibility="collapsed")
        if file:
            try:
                df_csv = pd.read_csv(file)
                st.dataframe(df_csv.head(3), use_container_width=True)

                if st.button("📥 Додати точки з CSV", use_container_width=True):
                    df_csv.columns = [col.strip().lower() for col in df_csv.columns]
                    lat_col = "lat" if "lat" in df_csv.columns else None
                    lng_col = "lon" if "lon" in df_csv.columns else ("lng" if "lng" in df_csv.columns else None)
                    val_col = "value" if "value" in df_csv.columns else None
                    uni_col = "unit" if "unit" in df_csv.columns else None
                    tim_col = "time" if "time" in df_csv.columns else None
                    typ_col = "type" if "type" in df_csv.columns else None
                    sub_col = "substance" if "substance" in df_csv.columns else None

                    if lat_col and lng_col:
                        for idx, row in df_csv.iterrows():
                            val_raw = str(row[val_col]).strip() if (val_col and pd.notna(row[val_col])) else ""
                            uni_raw = str(row[uni_col]).strip() if (uni_col and pd.notna(row[uni_col])) else ""
                            sub_raw = str(row[sub_col]).strip() if (sub_col and pd.notna(row[sub_col])) else ""
                            type_str = str(row[typ_col]).strip().lower() if (typ_col and pd.notna(row[typ_col])) else ""

                            label_text = f"{sub_raw.capitalize()} - {val_raw} {uni_raw}" if sub_raw else f"{val_raw} {uni_raw}".strip()
                            if not label_text:
                                label_text = "Точка розвідки"

                            date_text = str(row[tim_col]).strip() if (tim_col and pd.notna(row[tim_col])) else datetime.now().strftime("%d.%m.%Y")

                            if "хім" in type_str or "chemical" in type_str or "мг/" in uni_raw or "ppm" in uni_raw:
                                icon_url = SRC_DETECT_CHEMICAL
                            elif "біо" in type_str or "biological" in type_str:
                                icon_url = SRC_DETECT_BIOLOGICAL
                            else:
                                icon_url = SRC_DETECT_RADIATION

                            st.session_state.rkhb_points.append({
                                "lat": float(row[lat_col]),
                                "lng": float(row[lng_col]),
                                "label": label_text,
                                "date": date_text,
                                "icon": icon_url,
                            })
                        st.success("Дані з CSV успішно імпортовано!")
                        st.rerun()
            except Exception as e:
                st.error(f"Помилка зчитування CSV: {str(e)}")

    # 4. ТАБЛИЦЯ ТОЧОК
    if st.session_state.rkhb_points:
        st.markdown("---")
        st.write("📋 **Перелік активних точок:**")
        pts_only = [p for p in st.session_state.rkhb_points if "lat" in p]
        if pts_only:
            df_view = pd.DataFrame(pts_only)
            st.dataframe(df_view[["date", "label", "lat", "lng"]], use_container_width=True, height=130)

points_json = json.dumps(st.session_state.rkhb_points, ensure_ascii=False)
routes_json = json.dumps(st.session_state.routes_list, ensure_ascii=False)

# ==========================================
# LEAFLET MAP HTML
# ==========================================
html_map_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Map Module CBRN</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    <style>
        html, body { margin: 0; padding: 0; height: 100%; font-family: Arial, sans-serif; background: #fff; overflow: hidden; }
        #mapContainer { width: 100%; height: 550px; position: relative; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }
        #map { width: 100%; height: 100%; }
        
        #bottomControlsPanel {
            margin-top: 6px; background: #f9f9f9; padding: 8px 10px; border-radius: 8px;
            border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1); box-sizing: border-box;
        }
        .controls-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; flex-wrap: wrap; }
        .controls-row select, .controls-row input { padding: 5px 8px; background: #fff; color: #000; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
        .controls-row label { font-size: 13px; font-weight: bold; color: #333; }
        
        .panel-btn {
            padding: 5px 10px; background: #e0e0e0; color: #000; border: 1px solid #adadad;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 5px;
        }
        .panel-btn:hover { background: #d4d4d4; }
        .btn-stop { background: #ffebee !important; color: #c62828 !important; border-color: #ef9a9a !important; }
        .btn-clear-all { background: #b71c1c !important; color: #ffffff !important; border-color: #880e4f !important; }

        #windWidget {
            position: absolute; bottom: 15px; left: 10px; z-index: 1000;
            background: rgba(26, 26, 26, 0.9); color: #FFD600; padding: 6px;
            border-radius: 8px; border: 1px solid #FFD600; text-align: center; width: 70px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .wind-arrow { font-size: 22px; display: inline-block; transition: transform 0.3s ease; }
        .wind-info { font-size: 10px; color: #fff; margin-top: 1px; font-weight: bold; }

        .route-label {
            background: rgba(0, 0, 0, 0.85) !important; border: 1px solid #d97706 !important;
            color: #fff !important; font-size: 11px !important; font-weight: bold !important;
            padding: 2px 6px !important; border-radius: 4px !important; white-space: nowrap !important;
        }

        .leaflet-div-icon { background: transparent !important; border: none !important; box-shadow: none !important; }
        .cbrn-military-lbl {
            font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; color: #000 !important;
            text-align: center; display: inline-block; white-space: nowrap; line-height: 1.3; background: transparent !important;
        }
        .cbrn-line-divider { border-bottom: 2px solid #000 !important; width: 100%; display: block; margin: 2px 0; }
        .cbrn-date-sub { font-size: 11px; font-weight: bold; color: #000 !important; display: block; }
    </style>
</head>
<body>

    <div id="mapContainer">
        <div id="map"></div>
        <div id="windWidget">
            <div class="wind-arrow" id="arrow">↑</div>
            <div class="wind-info" id="degInfo">0°</div>
            <div class="wind-info" id="speedInfo">0 м/с</div>
        </div>
    </div>

    <div id="bottomControlsPanel">
        <div class="controls-row">
            <label>🧭 УМОВНІ ЗНАКИ РХБЗ:</label>
            <select id="signSelect">
                <option value="">-- Оберіть умовний знак для встановлення кліком --</option>
                <option value="ICO_DETECT_RADIATION">Точка рад. забруднення (detect_radiation)</option>
                <option value="ICO_DETECT_CHEMICAL">Точка хім. забруднення (detect_chemical)</option>
                <option value="ICO_DETECT_BIOLOGICAL">Точка біо. зараження (detect_biological)</option>
                <option value="ICO_CBRN_POST">Пост РХ спостереження (cbrn_post)</option>
                <option value="ICO_NUCLEAR_BLAST">Епіцентр ядерного вибуху (nuclear_blast)</option>
                <option value="ICO_BIOLOGICAL_HAZARD_SITE">Біологічно небезпечний об'єкт (biological_hazard_site)</option>
                <option value="ICO_CHEMICAL_HAZARD_SITE">Хімічно небезпечний об'єкт (chemical_hazard_site)</option>
                <option value="ICO_RADIOACTIVE_SITE">Радіаційно небезпечний об'єкт (radioactive_site)</option>
                <option value="ICO_CBRN_CONTAMINATION_AREA">Район РХБ забруднення (cbrn_contamination_area)</option>
                <option value="ICO_CBRN_RECON_AREA">Район РХБЗ розвідки (cbrn_recon_area)</option>
                <option value="ICO_DECON_AREA_SPECIAL">Район спеціальної обробки (decon_area_special)</option>
                <option value="ICO_DECON_POINT_SPECIAL">Пункт спеціальної обробки (decon_point_special)</option>
            </select>
            <button class="panel-btn" style="background: #fff3e0; border-color:#d97706; color:#b45309;" id="reconRouteBtn">Маршрут (ручний)</button>
            <button class="panel-btn" style="background: #e1f5fe; border-color:#0288d1;" id="textBtn">Текст</button>
            <button class="panel-btn" style="background: #efebe9; border-color:#5d4037;" id="ellipseBtn">Еліпс AEGL</button>
            <button class="panel-btn" style="background: #ffffff; border-color: #616161;" id="stopBtn">ЗАВЕРШИТИ знак</button>
            <button class="panel-btn btn-stop" id="deleteModeBtn">🗑️ ВИДАЛИТИ (кліком)</button>
            <button class="panel-btn btn-clear-all" id="clearAllMapBtn">ОЧИСТИТИ ВСЮ КАРТУ</button>
        </div>

        <div class="controls-row">
            <label>МЕТЕО — Напрямок вітру (звідки дме):</label>
            <input type="number" id="windInput" placeholder="Градуси (0-360)" min="0" max="360" value="0" style="width:120px;">
            <label>Швидкість вітру:</label>
            <input type="number" id="windSpeedInput" placeholder="м/с" min="0" value="2.0" step="0.1" style="width:90px;">
            
            <button class="panel-btn" style="background: #fff59d; border-color:#fbc02d;" id="applyMeteoBtn">🌀 Застосувати</button>
            <button class="panel-btn" style="background: #c8e6c9; border-color:#388e3c; margin-left: 15px;" id="pngBtn">🖼️ Зберегти PNG</button>
            <button class="panel-btn" style="background: #ffcdd2; border-color:#d32f2f;" id="printBtn">🖨️ Друк / PDF</button>
        </div>
    </div>

<script>
    var DATA_FROM_PYTHON = __POINTS_JSON__;
    var ROUTES_FROM_PYTHON = __ROUTES_JSON__;

    var ico_biological_hazard_site  = "__SRC_BIOLOGICAL_HAZARD_SITE__";
    var ico_cbrn_contamination_area = "__SRC_CBRN_CONTAMINATION_AREA__";
    var ico_cbrn_post               = "__SRC_CBRN_POST__";
    var ico_cbrn_recon_area         = "__SRC_CBRN_RECON_AREA__";
    var ico_chemical_hazard_site    = "__SRC_CHEMICAL_HAZARD_SITE__";
    var ico_decon_area_special      = "__SRC_DECON_AREA_SPECIAL__";
    var ico_decon_point_special     = "__SRC_DECON_POINT_SPECIAL__";
    var ico_detect_biological       = "__SRC_DETECT_BIOLOGICAL__";
    var ico_detect_chemical         = "__SRC_DETECT_CHEMICAL__";
    var ico_detect_radiation        = "__SRC_DETECT_RADIATION__";
    var ico_nuclear_blast           = "__SRC_NUCLEAR_BLAST__";
    var ico_radioactive_site        = "__SRC_RADIOACTIVE_SITE__";

    var map = L.map('map', { zoomControl: true }).setView([50.45, 30.52], 7);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' });
    var satLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', { attribution: '© Google' });
    osmLayer.addTo(map);

    map.pm.addControls({
        position: 'topleft', drawMarker: false, drawCircleMarker: false, drawPolyline: true,
        drawRectangle: true, drawPolygon: true, drawCircle: true, editControls: false
    });

    map.pm.setGlobalOptions({
        measurements: { display: true },
        pathOptions: { color: '#d97706', fillColor: '#FFD600', fillOpacity: 0.35, weight: 4 },
        pinToMarker: true
    });
    map.pm.setLang('uk');

    function saveRouteToPython(routeData) {
        var strData = JSON.stringify(routeData);
        var url = new URL(window.parent.location.href);
        url.searchParams.set('add_route_data', strData);
        window.parent.history.replaceState({}, '', url);
        window.parent.postMessage({type: "streamlit:set_query_params", params: { add_route_data: strData }}, "*");
    }

    map.on('pm:create', function(e) {
        var layer = e.layer;
        if (e.shape === 'Line' || layer instanceof L.Polyline) {
            var rawLatLngs = layer.getLatLngs();
            var coordsArray = [];
            
            rawLatLngs.forEach(function(ll) {
                if (coordsArray.length === 0) {
                    coordsArray.push([ll.lat, ll.lng]);
                } else {
                    var last = coordsArray[coordsArray.length - 1];
                    if (Math.abs(last[0] - ll.lat) > 0.00001 || Math.abs(last[1] - ll.lng) > 0.00001) {
                        coordsArray.push([ll.lat, ll.lng]);
                    }
                }
            });

            if (coordsArray.length < 2) {
                return;
            }

            var totalDist = 0;
            for (var i = 0; i < coordsArray.length - 1; i++) {
                var p1 = L.latLng(coordsArray[i][0], coordsArray[i][1]);
                var p2 = L.latLng(coordsArray[i+1][0], coordsArray[i+1][1]);
                totalDist += p1.distanceTo(p2);
            }
            var distKm = (totalDist / 1000).toFixed(2);
            var labelTxt = "Маршрут розвідки: " + distKm + " км";
            
            saveRouteToPython({
                type: 'manual',
                coords: coordsArray,
                label: labelTxt
            });
            return;
        }
        attachRemovalClick(layer, null);
    });

    var baseMaps = { "🗺️ Карта OSM": osmLayer, "🛰️ Супутник Google": satLayer };
    var dateLayers = {}; 
    var layerControl = L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

    function attachRemovalClick(layer, pointIndex, routeIndex) {
        layer.on('click', function(e) {
            if (map.pm.globalRemovalModeEnabled() || routeIndex !== undefined) {
                L.DomEvent.stopPropagation(e);
                if (confirm("Ви дійсно бажаєте видалити цей елемент з карти?")) {
                    map.removeLayer(layer);
                    if (pointIndex !== undefined && pointIndex !== null) {
                        var url = new URL(window.parent.location.href);
                        url.searchParams.set('delete_point_idx', pointIndex);
                        window.parent.history.replaceState({}, '', url);
                        window.parent.postMessage({type: "streamlit:set_query_params", params: { delete_point_idx: pointIndex.toString() }}, "*");
                    } else if (routeIndex !== undefined && routeIndex !== null) {
                        var url = new URL(window.parent.location.href);
                        url.searchParams.set('delete_route_idx', routeIndex);
                        window.parent.history.replaceState({}, '', url);
                        window.parent.postMessage({type: "streamlit:set_query_params", params: { delete_route_idx: routeIndex.toString() }}, "*");
                    }
                }
            }
        });
    }

    var allBounds = [];

    var inputPoints = DATA_FROM_PYTHON;
    if(Array.isArray(inputPoints)) {
        inputPoints.forEach(function(pt, index) {
            var dateStr = pt.date || "Базові дані";
            if (!dateLayers[dateStr]) {
                dateLayers[dateStr] = L.layerGroup().addTo(map);
                layerControl.addOverlay(dateLayers[dateStr], "📅 " + dateStr);
            }

            if(pt.lat && pt.lng) {
                var customIcon = L.icon({ iconUrl: pt.icon, iconSize: [32, 32], iconAnchor: [16, 16] });
                var marker = L.marker([pt.lat, pt.lng], { icon: customIcon });
                var labelHtml = "<div class='cbrn-military-lbl'><span>" + pt.label + "</span><div class='cbrn-line-divider'></div><span class='cbrn-date-sub'>" + dateStr + "</span></div>";
                marker.bindTooltip(labelHtml, { permanent: true, direction: 'bottom', offset: [0, 16], className: 'leaflet-div-icon' });
                attachRemovalClick(marker, index, null);
                marker.addTo(dateLayers[dateStr]);
                allBounds.push([pt.lat, pt.lng]);
            }
        });
    }

    var inputRoutes = ROUTES_FROM_PYTHON;
    if (Array.isArray(inputRoutes)) {
        inputRoutes.forEach(function(rData, rIdx) {
            var rLayer;
            if (rData.coords && rData.coords.length > 0) {
                rLayer = L.polyline(rData.coords, { color: '#d97706', weight: 4, dashArray: '8, 8' }).addTo(map);
                rData.coords.forEach(c => allBounds.push(c));
                if (rLayer) {
                    rLayer.bindTooltip(rData.label, { permanent: true, direction: 'center', className: 'route-label' });
                    attachRemovalClick(rLayer, null, rIdx);
                }
            }
        });
    }

    if (allBounds.length > 0) {
        map.fitBounds(L.latLngBounds(allBounds), { padding: [30, 30] });
    }

    var activeIcon = ""; var textMode = false; var ellipseMode = false; var isReconMode = false;
    function clearModes() {
        activeIcon = ""; textMode = false; ellipseMode = false; isReconMode = false;
        document.getElementById('signSelect').value = "";
        if(map.pm.globalDrawModeEnabled()) map.pm.disableDraw();
    }

    document.getElementById('clearAllMapBtn').onclick = function() {
        if (confirm("Ви дійсно бажаєте очистити всі знаки та маршрути з карти?")) {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('clear_all', '1');
            window.parent.history.replaceState({}, '', url);
            window.parent.postMessage({type: "streamlit:set_query_params", params: { clear_all: '1' }}, "*");
        }
    };

    document.getElementById('signSelect').onchange = function(e) {
        var val = e.target.value;
        if(val === "ICO_DETECT_RADIATION") activeIcon = ico_detect_radiation;
        else if(val === "ICO_DETECT_CHEMICAL") activeIcon = ico_detect_chemical;
        else if(val === "ICO_DETECT_BIOLOGICAL") activeIcon = ico_detect_biological;
        else if(val === "ICO_CBRN_POST") activeIcon = ico_cbrn_post;
        else if(val === "ICO_NUCLEAR_BLAST") activeIcon = ico_nuclear_blast;
        else if(val === "ICO_BIOLOGICAL_HAZARD_SITE") activeIcon = ico_biological_hazard_site;
        else if(val === "ICO_CHEMICAL_HAZARD_SITE") activeIcon = ico_chemical_hazard_site;
        else if(val === "ICO_RADIOACTIVE_SITE") activeIcon = ico_radioactive_site;
        else if(val === "ICO_CBRN_CONTAMINATION_AREA") activeIcon = ico_cbrn_contamination_area;
        else if(val === "ICO_CBRN_RECON_AREA") activeIcon = ico_cbrn_recon_area;
        else if(val === "ICO_DECON_AREA_SPECIAL") activeIcon = ico_decon_area_special;
        else if(val === "ICO_DECON_POINT_SPECIAL") activeIcon = ico_decon_point_special;
        else activeIcon = "";
        textMode = false; ellipseMode = false; isReconMode = false;
    };
    
    document.getElementById('reconRouteBtn').onclick = function() {
        clearModes(); isReconMode = true;
        map.pm.enableDraw('Line', { snappable: true, pathOptions: { color: '#d97706', weight: 4, dashArray: '8, 8' } });
    };

    document.getElementById('textBtn').onclick = function() { clearModes(); textMode = true; };
    document.getElementById('ellipseBtn').onclick = function() { clearModes(); ellipseMode = true; };
    document.getElementById('stopBtn').onclick = function() { clearModes(); if(map.pm.globalRemovalModeEnabled()) map.pm.toggleGlobalRemovalMode(); };
    document.getElementById('deleteModeBtn').onclick = function() { clearModes(); map.pm.toggleGlobalRemovalMode(); };

    document.getElementById('applyMeteoBtn').onclick = function() {
        var windFromDeg = parseFloat(document.getElementById('windInput').value) || 0;
        var windSpeed = parseFloat(document.getElementById('windSpeedInput').value) || 0;
        var blowToDeg = (windFromDeg + 180) % 360;
        
        document.getElementById('arrow').style.transform = 'rotate(' + blowToDeg + 'deg)';
        document.getElementById('degInfo').innerText = windFromDeg + '°';
        document.getElementById('speedInfo').innerText = windSpeed + ' м/с';
    };

    document.getElementById('pngBtn').onclick = function() {
        html2canvas(document.getElementById('mapContainer')).then(function(canvas) {
            var a = document.createElement('a');
            a.href = canvas.toDataURL('image/png');
            a.download = 'cbrn_map.png';
            a.click();
        });
    };

    document.getElementById('printBtn').onclick = function() { window.print(); };

    map.on('click', function(e) {
        var lat = e.latlng.lat;
        var lng = e.latlng.lng;

        if (window.parent && window.parent.document) {
            var targetBox = window.parent.document.getElementById('pythonCoordBox');
            if (targetBox) targetBox.innerHTML = "📍 " + lat.toFixed(5) + " , " + lng.toFixed(5);
        }

        if (!activeIcon && !textMode && !ellipseMode && !isReconMode) {
            if (map.pm.globalRemovalModeEnabled()) return;
            var url = new URL(window.parent.location.href);
            url.searchParams.set('click_lat', lat.toFixed(5));
            url.searchParams.set('click_lng', lng.toFixed(5));
            window.parent.history.replaceState({}, '', url);
            window.parent.postMessage({type: "streamlit:set_query_params", params: {click_lat: lat.toFixed(5), click_lng: lng.toFixed(5)}}, "*");
            return;
        }

        if (activeIcon) {
            var m = L.marker(e.latlng, { icon: L.icon({ iconUrl: activeIcon, iconSize: [32, 32], iconAnchor: [16, 16] }) }).addTo(map);
            attachRemovalClick(m, null, null);
        }
        if (textMode) {
            var txt = prompt("Введіть оперативно-тактичний підпис:");
            if (txt) {
                var tm = L.marker(e.latlng, {
                    icon: L.divIcon({ className: 'leaflet-div-icon', html: "<span class='cbrn-military-lbl' style='font-size:13px;'>"+txt+"</span>" })
                }).addTo(map);
                attachRemovalClick(tm, null, null);
            }
        }
    });
</script>
</body>
</html>"""

rendered_html = (
    html_map_template.replace("__POINTS_JSON__", points_json)
    .replace("__ROUTES_JSON__", routes_json)
    .replace("__SRC_BIOLOGICAL_HAZARD_SITE__", SRC_BIOLOGICAL_HAZARD_SITE)
    .replace("__SRC_CBRN_CONTAMINATION_AREA__", SRC_CBRN_CONTAMINATION_AREA)
    .replace("__SRC_CBRN_POST__", SRC_CBRN_POST)
    .replace("__SRC_CBRN_RECON_AREA__", SRC_CBRN_RECON_AREA)
    .replace("__SRC_CHEMICAL_HAZARD_SITE__", SRC_CHEMICAL_HAZARD_SITE)
    .replace("__SRC_DECON_AREA_SPECIAL__", SRC_DECON_AREA_SPECIAL)
    .replace("__SRC_DECON_POINT_SPECIAL__", SRC_DECON_POINT_SPECIAL)
    .replace("__SRC_DETECT_BIOLOGICAL__", SRC_DETECT_BIOLOGICAL)
    .replace("__SRC_DETECT_CHEMICAL__", SRC_DETECT_CHEMICAL)
    .replace("__SRC_DETECT_RADIATION__", SRC_DETECT_RADIATION)
    .replace("__SRC_NUCLEAR_BLAST__", SRC_NUCLEAR_BLAST)
    .replace("__SRC_RADIOACTIVE_SITE__", SRC_RADIOACTIVE_SITE)
)

with col_map:
    components.html(rendered_html, height=720, scrolling=False)
