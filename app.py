import streamlit as st
import pandas as pd
import json
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. НАЛАШТУВАННЯ СТОРІНКИ ТА СТИЛІВ STREAMLIT
# ==========================================
st.set_page_config(page_title="Платформа ХБРЯ", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stButton button {
    font-weight: bold; width: 100%; height: 3em; border-radius: 8px; 
    background-color: #FFD600 !important; color: black !important;
    border: 1px solid #cca300 !important;
}
.stButton button:hover { background-color: #ffea00 !important; }
.coord-box {
    background-color: #1e1e1e !important; color: #FFD600 !important; 
    padding: 12px; border-radius: 6px; text-align: center;
    border: 2px solid #FFD600; font-weight: bold; font-size: 16px; margin-bottom: 15px;
}
.info-text {
    font-size: 13px; color: #e0e0e0; font-style: italic; margin-bottom: 15px; line-height: 1.4;
}
.import-btn button {
    background-color: #4CAF50 !important; color: white !important;
    border: 1px solid #388E3C !important;
}
.import-btn button:hover { background-color: #45a049 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 НАЛАШТУВАННЯ ШЛЯХІВ ДО REPO GITHUB (ЧЕРЕЗ JSDELIVR CDN)
# ==========================================
GITHUB_USER = "sergsh1125-dotcom"
GITHUB_REPO = "map-obstanovka"
GITHUB_BRANCH = "main"

GITHUB_BASE_URL = f"https://cdn.jsdelivr.net/gh/{GITHUB_USER}/{GITHUB_REPO}@{GITHUB_BRANCH}/assets/svg"

def get_gh_svg_url(filename):
    return f"{GITHUB_BASE_URL}/{filename}"

SRC_BIOLOGICAL_HAZARD_SITE  = get_gh_svg_url("biological_hazard_site.svg")
SRC_CBRN_CONTAMINATION_AREA = get_gh_svg_url("cbrn_contamination_area.svg")
SRC_CBRN_POST               = get_gh_svg_url("cbrn_post.svg")
SRC_CBRN_RECON_AREA         = get_gh_svg_url("cbrn_recon_area.svg")
SRC_CHEMICAL_HAZARD_SITE    = get_gh_svg_url("chemical_hazard_site.svg")
SRC_DECON_AREA_SPECIAL      = get_gh_svg_url("decon_area_special.svg")
SRC_DECON_POINT_SPECIAL     = get_gh_svg_url("decon_point_special.svg")
SRC_DETECT_BIOLOGICAL       = get_gh_svg_url("detect_biological.svg")
SRC_DETECT_CHEMICAL         = get_gh_svg_url("detect_chemical.svg")
SRC_DETECT_RADIATION        = get_gh_svg_url("detect_radiation.svg")
SRC_NUCLEAR_BLAST           = get_gh_svg_url("nuclear_blast.svg")
SRC_RADIOACTIVE_SITE        = get_gh_svg_url("radioactive_site.svg")

if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = []

if "captured_lat" not in st.session_state:
    st.session_state.captured_lat = 50.4500
if "captured_lng" not in st.session_state:
    st.session_state.captured_lng = 30.5200

# ОБРОБКА ПОВНОГО ОЧИЩЕННЯ
if "clear_all" in st.query_params:
    st.session_state.rkhb_points = []
    st.session_state.captured_lat = 50.4500
    st.session_state.captured_lng = 30.5200
    st.query_params.clear()
    st.rerun()

# ОБРОБКА ВИДАЛЕННЯ ТОЧКИ ЧЕРЕЗ КЛІК НА КАРТІ
if "delete_point_idx" in st.query_params:
    try:
        idx_to_del = int(st.query_params["delete_point_idx"])
        if 0 <= idx_to_del < len(st.session_state.rkhb_points):
            st.session_state.rkhb_points.pop(idx_to_del)
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

st.header("КАРТА ФАКТИЧНОЇ РХБ ОБСТАНОВКИ")
col_map, col_gui = st.columns([3, 1])

# ==========================================
# 2. ПУЛЬТ УПРАВЛІННЯ ДАНИМИ (ПРАВА ПАНЕЛЬ)
# ==========================================
with col_gui:
    st.subheader(" ПАНЕЛЬ УПРАВЛІННЯ ")
    st.markdown("<div class='info-text'>ℹ️ Для нанесення точки РХ забруднення вручну клікніть у визначеній точці на карті та введіть показники.</div>", unsafe_allow_html=True)
    st.markdown(f"<div id='pythonCoordBox' class='coord-box'>📍 {st.session_state.captured_lat:.5f} , {st.session_state.captured_lng:.5f}</div>", unsafe_allow_html=True)
    
    with st.expander("➕ Параметри точки вимірювання", expanded=True):
        m_type = st.radio("Тип забруднення:", ["Радіоактивне", "Хімічне"])
        m_lat = st.number_input("Широта (Lat)", value=st.session_state.captured_lat, format="%.5f", key=f"lat_{st.session_state.captured_lat}")
        m_lon = st.number_input("Довгота (Lon)", value=st.session_state.captured_lng, format="%.5f", key=f"lng_{st.session_state.captured_lng}")
        
        if m_type == "Радіоактивне":
            r_val = st.number_input("Потужність дози", value=0.15, step=0.01)
            r_uni = st.selectbox("Одиниця виміру", ["мкЗв/год", "мЗв/год"])
            lbl = f"{r_val} {r_uni}"
            ico = SRC_DETECT_RADIATION
        else:
            c_sub = st.text_input("Речовина", value="Іприт")
            c_val = st.number_input("Концентрація", value=0.10, step=0.01)
            c_uni = st.selectbox("Одиниця виміру", ["мг/м³", "ppm"])
            lbl = f"{c_sub} - {c_val} {c_uni}"
            ico = SRC_DETECT_CHEMICAL
            
        m_date = datetime.now().strftime("%d.%m.%Y")
        st.caption(f"📅 Дата фіксації (авто): {m_date}")
        
        if st.button("Нанести точку на карту", type="primary"):
            st.session_state.rkhb_points.append({"lat": m_lat, "lng": m_lon, "label": lbl, "date": m_date, "icon": ico})
            st.rerun()

    st.divider()
    
    st.write("📊 **Імпорт бази даних розвідки**")
    file = st.file_uploader("Виберіть CSV файл:", type=["csv"], label_visibility="collapsed")
    if file:
        try:
            df_csv = pd.read_csv(file)
            st.dataframe(df_csv.head(3), use_container_width=True)
            
            st.markdown('<div class="import-btn">', unsafe_allow_html=True)
            if st.button("📥 Додати точки на карту з таблиці"):
                df_csv.columns = [col.strip().lower() for col in df_csv.columns]
                lat_col = 'lat' if 'lat' in df_csv.columns else None
                lng_col = 'lon' if 'lon' in df_csv.columns else ('lng' if 'lng' in df_csv.columns else None)
                val_col = 'value' if 'value' in df_csv.columns else None
                uni_col = 'unit' if 'unit' in df_csv.columns else None
                tim_col = 'time' if 'time' in df_csv.columns else None
                typ_col = 'type' if 'type' in df_csv.columns else None
                sub_col = 'substance' if 'substance' in df_csv.columns else None
                
                if lat_col and lng_col:
                    for idx, row in df_csv.iterrows():
                        val_raw = str(row[val_col]).strip() if (val_col and pd.notna(row[val_col])) else ""
                        uni_raw = str(row[uni_col]).strip() if (uni_col and pd.notna(row[uni_col])) else ""
                        sub_raw = str(row[sub_col]).strip() if (sub_col and pd.notna(row[sub_col])) else ""
                        type_str = str(row[typ_col]).strip().lower() if (typ_col and pd.notna(row[typ_col])) else ""
                        
                        if sub_raw: label_text = f"{sub_raw.capitalize()} - {val_raw} {uni_raw}"
                        else: label_text = f"{val_raw} {uni_raw}".strip()
                        if not label_text: label_text = "Точка розвідки"
                            
                        date_text = str(row[tim_col]).strip() if (tim_col and pd.notna(row[tim_col])) else datetime.now().strftime("%d.%m.%Y")
                        
                        if "хім" in type_str or "chemical" in type_str or "мг/" in uni_raw or "ppm" in uni_raw:
                            icon_url = SRC_DETECT_CHEMICAL
                        elif "біо" in type_str or "biological" in type_str:
                            icon_url = SRC_DETECT_BIOLOGICAL
                        else:
                            icon_url = SRC_DETECT_RADIATION

                        st.session_state.rkhb_points.append({
                            "lat": float(row[lat_col]), "lng": float(row[lng_col]),
                            "label": label_text, "date": date_text, "icon": icon_url
                        })
                    st.rerun()
        except Exception as e:
            st.error(f"Помилка: {str(e)}")

    if st.session_state.rkhb_points:
        pts_only = [p for p in st.session_state.rkhb_points if "lat" in p]
        if pts_only:
            df_view = pd.DataFrame(pts_only)
            st.dataframe(df_view[["date", "label", "lat", "lng"]], use_container_width=True, height=110)

points_json = json.dumps(st.session_state.rkhb_points, ensure_ascii=False)

# ==========================================
# 3. HTML/JS КОД КАРТИ LEAFLET
# ==========================================
html_map_component = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Map Module 1</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    <style>
        html, body { margin: 0; padding: 0; height: 100%; font-family: Arial, sans-serif; background: #fff; }
        #mapContainer { width: 100%; height: 430px; position: relative; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }
        #map { width: 100%; height: 100%; }
        
        #bottomControlsPanel {
            margin-top: 8px; background: #f5f5f5; padding: 10px; border-radius: 8px;
            border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-height: 280px; overflow-y: auto;
        }
        .controls-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
        .controls-row:last-child { margin-bottom: 0; }
        
        .controls-row select, .controls-row input {
            padding: 6px 8px; background: #fff; color: #000; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
        }
        .controls-row label { font-size: 13px; font-weight: bold; color: #333; }
        
        .panel-btn {
            padding: 6px 10px; background: #e0e0e0; color: #000; border: 1px solid #adadad;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 5px;
        }
        .panel-btn:hover { background: #d4d4d4; }
        .btn-stop { background: #ffebee !important; color: #c62828 !important; border-color: #ef9a9a !important; }
        .btn-stop:hover { background: #ffcdd2 !important; }
        .btn-clear-all { background: #b71c1c !important; color: #ffffff !important; border-color: #880e4f !important; }
        .btn-clear-all:hover { background: #d32f2f !important; }
        .btn-autoroute { background: #FFD600 !important; color: #000 !important; border-color: #cca300 !important; }
        .btn-autoroute:hover { background: #ffea00 !important; }

        #windWidget {
            position: absolute; bottom: 15px; left: 10px; z-index: 1000;
            background: rgba(26, 26, 26, 0.9); color: #FFD600; padding: 6px;
            border-radius: 8px; border: 1px solid #FFD600; text-align: center; width: 70px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .wind-arrow { font-size: 20px; display: inline-block; transition: transform 0.5s; }
        .wind-info { font-size: 9px; color: #fff; margin-top: 1px; font-weight: bold; }

        .size-tooltip {
            background: rgba(0, 0, 0, 0.85) !important; border: 1px solid #FFD600 !important;
            color: #fff !important; font-weight: bold; font-size: 12px; padding: 4px 8px; border-radius: 4px;
        }
        
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

        @media (max-width: 600px) {
            #mapContainer { height: 350px; }
            .controls-row { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
            .controls-row label { grid-column: span 2; margin-top: 4px; }
            .controls-row select, .controls-row input { width: 100% !important; box-sizing: border-box; }
            .panel-btn { justify-content: center; width: 100%; box-sizing: border-box; }
        }
    </style></head>
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
                <option value="ICO_RADIOACTIVE_SITE">Радіаціно небезпечний об'єкт (radioactive_site)</option>
                <option value="ICO_CBRN_CONTAMINATION_AREA">Район РХБ забруднення (cbrn_contamination_area)</option>
                <option value="ICO_CBRN_RECON_AREA">Район РХБЗ розвідки (cbrn_recon_area)</option>
                <option value="ICO_DECON_AREA_SPECIAL">Район спеціальної обробки (decon_area_special)</option>
                <option value="ICO_DECON_POINT_SPECIAL">Пункт спеціальної обробки (decon_point_special)</option>
            </select>
            <button class="panel-btn" style="background: #fff3e0; border-color:#d97706; color:#b45309;" id="reconRouteBtn">Маршрут (ручний режим)</button>
            <button class="panel-btn" style="background: #e1f5fe; border-color:#0288d1;" id="textBtn">Текст</button>
            <button class="panel-btn" style="background: #efebe9; border-color:#5d4037;" id="ellipseBtn">Еліпс AEGL</button>
            <button class="panel-btn" style="background: #ffffff; border-color: #616161;" id="stopBtn">ЗАВЕРШИТИ знак</button>
            <button class="panel-btn btn-stop" id="deleteModeBtn">🗑️ ВИДАЛИТИ (кліком)</button>
            <button class="panel-btn btn-clear-all" id="clearAllMapBtn">ОЧИСТИТИ ВСЮ КАРТУ</button>
        </div>
        
        <div class="controls-row">
            <label>МАРШРУТ (через ';'):</label>
            <input type="text" id="autoRouteInput" placeholder="Наприклад: Київ; Фастів; Житомир" style="flex: 1; min-width: 220px;">
            <button class="panel-btn btn-autoroute" id="buildAutoRouteBtn">Маршрут (автоматичний режим)</button>
        </div>

        <div class="controls-row">
            <label>МЕТЕО — Напрямок вітру:</label>
            <input type="number" id="wDegInput" placeholder="Градуси (0-360)" min="0" max="360" value="0" style="width:130px;">
            <label>Швидкість вітру:</label>
            <input type="number" id="wSpeedInput" placeholder="м/с" min="0" value="0" step="0.1" style="width:90px;">
            
            <button class="panel-btn" style="background: #fff59d; border-color:#fbc02d;" id="applyMeteoBtn">🌀 Застосувати</button>
            <button class="panel-btn" style="background: #c8e6c9; border-color:#388e3c; margin-left: 20px;" id="pngBtn">🖼️ Зберегти PNG</button>
            <button class="panel-btn" style="background: #ffcdd2; border-color:#d32f2f;" id="printBtn">🖨️ Друк / PDF</button>
        </div>
    </div>

<script>
    var ico_biological_hazard_site  = SRC_BIOLOGICAL_HAZARD_SITE;
    var ico_cbrn_contamination_area = SRC_CBRN_CONTAMINATION_AREA;
    var ico_cbrn_post               = SRC_CBRN_POST;
    var ico_cbrn_recon_area         = SRC_CBRN_RECON_AREA;
    var ico_chemical_hazard_site    = SRC_CHEMICAL_HAZARD_SITE;
    var ico_decon_area_special      = SRC_DECON_AREA_SPECIAL;
    var ico_decon_point_special     = SRC_DECON_POINT_SPECIAL;
    var ico_detect_biological       = SRC_DETECT_BIOLOGICAL;
    var ico_detect_chemical         = SRC_DETECT_CHEMICAL;
    var ico_detect_radiation        = SRC_DETECT_RADIATION;
    var ico_nuclear_blast           = SRC_NUCLEAR_BLAST;
    var ico_radioactive_site        = SRC_RADIOACTIVE_SITE;

    var map = L.map('map', { zoomControl: true }).setView([48.3, 31.1], 6);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' });
    var satLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', { attribution: '© Google' });
    osmLayer.addTo(map);

    map.pm.addControls({
        position: 'topleft', drawMarker: false, drawCircleMarker: false, drawPolyline: true,
        drawRectangle: true, drawPolygon: true, drawCircle: true, editControls: false
    });

    map.pm.setGlobalOptions({
        measurements: { display: false },
        pathOptions: { color: '#000', fillColor: '#FFD600', fillOpacity: 0.35, weight: 2 },
        pinToMarker: true
    });
    map.pm.setLang('uk');

    map.on('pm:drawstart', function(e) {
        if(e.shape === 'Circle') map.dragging.disable();
    });
    map.on('pm:drawend', function(e) {
        map.dragging.enable();
    });

    var baseMaps = { "🗺️ Карта OSM": osmLayer, "🛰️ Супутник Google": satLayer };
    var dateLayers = {}; 
    var layerControl = L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

    function attachRemovalClick(layer, pointIndex) {
        layer.on('click', function(e) {
            if (map.pm.globalRemovalModeEnabled()) {
                L.DomEvent.stopPropagation(e);
                map.removeLayer(layer);
                if (pointIndex !== undefined && pointIndex !== null) {
                    var url = new URL(window.parent.location.href);
                    url.searchParams.set('delete_point_idx', pointIndex);
                    window.parent.history.replaceState({}, '', url);
                    window.parent.postMessage({type: "streamlit:set_query_params", params: { delete_point_idx: pointIndex.toString() }}, "*");
                }
            }
        });
    }

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
                attachRemovalClick(marker, index);
                marker.addTo(dateLayers[dateStr]);
            }
            else if(pt.is_route && pt.geojson) {
                var rLayer = L.geoJSON(pt.geojson, {
                    style: { color: "#d97706", weight: 4, dashArray: "8, 8" }
                });
                if(pt.label) {
                    rLayer.bindTooltip(pt.label, { permanent: true, direction: 'center', className: 'route-label' });
                }
                attachRemovalClick(rLayer, index);
                rLayer.addTo(dateLayers[dateStr]);
            }
        });
    }

    var activeIcon = ""; var textMode = false; var ellipseMode = false; var isReconMode = false;
    function clearModes() {
        activeIcon = ""; textMode = false; ellipseMode = false; isReconMode = false;
        document.getElementById('signSelect').value = "";
        if(map.pm.globalDrawModeEnabled()) map.pm.disableDraw();
    }

    // МИТТЄВЕ МАРШРУТНЕ ТА ШАРОВЕ ОЧИЩЕННЯ
    document.getElementById('clearAllMapBtn').onclick = function() {
        if (confirm("Ви дійсно бажаєте очистити всі знаки та маршрути з карти?")) {
            map.eachLayer(function(layer) {
                if (layer !== osmLayer && layer !== satLayer) {
                    map.removeLayer(layer);
                }
            });
            Object.keys(dateLayers).forEach(function(k) {
                layerControl.removeLayer(dateLayers[k]);
            });
            dateLayers = {};

            var url = new URL(window.parent.location.href);
            url.searchParams.set('clear_all', '1');
            window.parent.history.replaceState({}, '', url);
            window.parent.postMessage({type: "streamlit:set_query_params", params: { clear_all: '1' }}, "*");
        }
    };

    // ПОДВІЙНЕ ГЕОКОДУВАННЯ (PHOTON + NOMINATIM) ДЛЯ НАДІЙНОГО ПОШУКУ
    async function geocodePlaceJS(query) {
        if (!query) return null;
        query = query.trim();
        
        var parts = query.split(',');
        if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
            return { lat: parseFloat(parts[0].trim()), lng: parseFloat(parts[1].trim()) };
        }
        
        var searchStr = (query.toLowerCase().includes("україна") || query.toLowerCase().includes("ukraine")) ? query : query + ", Україна";
        
        try {
            var pUrl = "https://photon.komoot.io/api/?q=" + encodeURIComponent(searchStr) + "&limit=1";
            var resP = await fetch(pUrl);
            var dataP = await resP.json();
            if (dataP && dataP.features && dataP.features.length > 0) {
                var coordsP = dataP.features[0].geometry.coordinates;
                return { lat: coordsP[1], lng: coordsP[0] };
            }
        } catch(e) {}

        try {
            var nUrl = "https://nominatim.openstreetmap.org/search?format=json&q=" + encodeURIComponent(searchStr) + "&limit=1";
            var resN = await fetch(nUrl, { headers: { 'Accept-Language': 'uk,en' } });
            var dataN = await resN.json();
            if (dataN && dataN.length > 0) {
                return { lat: parseFloat(dataN[0].lat), lng: parseFloat(dataN[0].lon) };
            }
        } catch(e) {}

        return null;
    }

    document.getElementById('buildAutoRouteBtn').onclick = async function() {
        var inputVal = document.getElementById('autoRouteInput').value.trim();
        if (!inputVal) {
            alert("Введіть населені пункти через крапку з комою ';'");
            return;
        }
        var pointsList = inputVal.split(';').map(p => p.trim()).filter(p => p.length > 0);
        if (pointsList.length < 2) {
            alert("Введіть як мінімум 2 населені пункти (наприклад: Київ; Житомир)");
            return;
        }

        var btn = document.getElementById('buildAutoRouteBtn');
        var originalBtnText = "Маршрут (автоматичний режим)";
        
        btn.innerText = "⏳ Пошук та прокладання...";
        btn.disabled = true;

        var coords = [];
        var failedPoint = null;

        for (var p of pointsList) {
            var c = await geocodePlaceJS(p);
            if (c) {
                coords.push(c);
            } else {
                failedPoint = p;
                break;
            }
        }

        if (failedPoint) {
            alert("Не вдалося знайти населений пункт: '" + failedPoint + "'");
            btn.innerText = originalBtnText;
            btn.disabled = false;
            return;
        }

        var coordsStr = coords.map(c => c.lng + "," + c.lat).join(";");
        var osrmUrl = "https://router.project-osrm.org/route/v1/driving/" + coordsStr + "?overview=full&geometries=geojson";

        try {
            var res = await fetch(osrmUrl);
            var resData = await res.json();
            if (resData.code === 'Ok') {
                var routeData = resData.routes[0];
                var distKm = (routeData.distance / 1000).toFixed(2);
                var durMin = Math.round(routeData.duration / 60);
                var labelName = "Маршрут: " + pointsList.join(" ➔ ") + " (" + distKm + " км, ~" + durMin + " хв)";

                var rLayer = L.geoJSON(routeData.geometry, {
                    style: { color: "#d97706", weight: 4, dashArray: "8, 8" }
                }).addTo(map);

                rLayer.bindTooltip(labelName, { permanent: true, direction: 'center', className: 'route-label' });
                attachRemovalClick(rLayer, null);

                map.fitBounds(rLayer.getBounds(), { padding: [30, 30] });

                alert("Маршрут успішно побудовано! Відстань: " + distKm + " км");
            } else {
                alert("Помилка побудови маршруту через сервер OSRM.");
            }
        } catch(err) {
            alert("Помилка при побудові маршруту: " + err);
        } finally {
            btn.innerText = originalBtnText;
            btn.disabled = false;
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
        clearModes();
        isReconMode = true;
        map.pm.enableDraw('Line', {
            snappable: true,
            pathOptions: { color: '#d97706', weight: 4, dashArray: '8, 8' }
        });
    };

    document.getElementById('textBtn').onclick = function() { clearModes(); textMode = true; };
    document.getElementById('ellipseBtn').onclick = function() { clearModes(); ellipseMode = true; };
    document.getElementById('stopBtn').onclick = function() { clearModes(); if(map.pm.globalRemovalModeEnabled()) map.pm.toggleGlobalRemovalMode(); };
    document.getElementById('deleteModeBtn').onclick = function() { clearModes(); map.pm.toggleGlobalRemovalMode(); };

    map.on('click', function(e) {
        var lat = e.latlng.lat;
        var lng = e.latlng.lng;

        if (window.parent && window.parent.document) {
            var targetBox = window.parent.document.getElementById('pythonCoordBox');
            if (targetBox) {
                targetBox.innerHTML = "📍 " + lat.toFixed(5) + " , " + lng.toFixed(5);
            }
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
            attachRemovalClick(m, null);
        }
        if (textMode) {
            var txt = prompt("Введіть оперативно-тактичний підпис:");
            if (txt) {
                var tm = L.marker(e.latlng, {
                    icon: L.divIcon({ className: 'leaflet-div-icon', html: "<span class='cbrn-military-lbl' style='font-size:13px;'>"+txt+"</span>" })
                }).addTo(map);
                attachRemovalClick(tm, null);
            }
        }
        if (ellipseMode) {
            var rX = prompt("Довжина зони AEGL (метри за вітром):", "4000"); if (!rX) return;
            var rY = prompt("Ширина зони AEGL (метри бокова):", "1500"); if (!rY) return;
            var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
            drawCbrnEllipse(e.latlng.lat, e.latlng.lng, parseFloat(rX), parseFloat(rY), deg);
            clearModes(); 
        }
    });

    function drawCbrnEllipse(centerLat, centerLng, rx, ry, deg) {
        var angles = [1, 0.6, 0.3]; var colors = ["#ffcc00", "#ff9900", "#cc0000"]; var opacities = [0.25, 0.4, 0.6];
        var windRad = (deg + 180) * Math.PI / 180;
        angles.forEach(function(scale, idx) {
            var curRx = rx * scale; var curRy = ry * scale; var points = [];
            for (var i = 0; i <= 64; i++) {
                var angle = (i / 64) * 2 * Math.PI;
                var x = curRy * Math.cos(angle); var y = curRx * Math.sin(angle);
                var rotX = x * Math.cos(windRad) + (y + curRx) * Math.sin(windRad);
                var rotY = -x * Math.sin(windRad) + (y + curRx) * Math.cos(windRad);
                var latOffset = rotY / 111320; var lngOffset = rotX / (111320 * Math.cos(centerLat * Math.PI / 180));
                points.push([centerLat + latOffset, centerLng + lngOffset]);
            }
            var poly = L.polygon(points, { color: 'black', weight: 1, fillColor: colors[idx], fillOpacity: opacities[idx] }).addTo(map);
            attachRemovalClick(poly, null);
        });
    }

    document.getElementById('applyMeteoBtn').onclick = function() {
        var deg = parseFloat(document.getElementById('wDegInput').value) || 0; var speed = parseFloat(document.getElementById('wSpeedInput').value) || 0;
        document.getElementById('arrow').style.transform = "rotate(" + ((deg + 180) % 360) + "deg)";
        document.getElementById('degInfo').innerText = deg + "°"; document.getElementById('speedInfo').innerText = speed + " м/с";
    };

    map.on('pm:create', function(e) {
        if (isReconMode || e.shape === 'Line') {
            var latlngs = e.layer.getLatLngs();
            var totalMeters = 0;
            for (var i = 0; i < latlngs.length - 1; i++) {
                totalMeters += latlngs[i].distanceTo(latlngs[i + 1]);
            }
            var distStr = totalMeters >= 1000 ? (totalMeters / 1000).toFixed(2) + " км" : Math.round(totalMeters) + " м";
            var routeName = prompt("Введіть номер/назву маршруту розвідки:", "Маршрут розвідки №1");
            var fullLabel = (routeName ? routeName : "Маршрут розвідки") + " (" + distStr + ")";
            
            e.layer.setStyle({ color: '#d97706', weight: 4, dashArray: '8, 8' });
            e.layer.bindTooltip(fullLabel, { permanent: true, direction: 'center', className: 'route-label' });
            isReconMode = false;
        } else if (e.shape === 'Circle') {
            var radiusMeters = e.layer.getRadius();
            var radiusKm = (radiusMeters / 1000).toFixed(2);
            var labelText = "R = " + radiusKm + " км²";
            var center = e.layer.getLatLng();
            var latOffset = radiusMeters / 111320;
            var topPoint = L.latLng(center.lat + latOffset, center.lng);
            e.layer.bindTooltip(labelText, { permanent: true, direction: 'top', className: 'size-tooltip', offset: [0, -10] });
        }
        attachRemovalClick(e.layer, null);
    });

    document.getElementById('pngBtn').onclick = function() {
        var container = document.getElementById('mapContainer'); var controls = document.querySelector('.leaflet-control-container');
        controls.style.display = 'none';
        html2canvas(container, { useCORS: true, allowTaint: true }).then(function(canvas) {
            var link = document.createElement('a'); link.download = 'CBRN_Map_Export.png'; link.href = canvas.toDataURL(); link.click();
            controls.style.display = 'block';
        });
    };
    document.getElementById('printBtn').onclick = function() { window.print(); };
</script>
</body>
</html>
"""

# ==========================================
# 4. РЕНДЕРИНГ КАРТИ
# ==========================================
with col_map:
    final_html = html_map_component.replace("DATA_FROM_PYTHON", points_json)
    final_html = final_html.replace("SRC_BIOLOGICAL_HAZARD_SITE", f"'{SRC_BIOLOGICAL_HAZARD_SITE}'")
    final_html = final_html.replace("SRC_CBRN_CONTAMINATION_AREA", f"'{SRC_CBRN_CONTAMINATION_AREA}'")
    final_html = final_html.replace("SRC_CBRN_POST", f"'{SRC_CBRN_POST}'")
    final_html = final_html.replace("SRC_CBRN_RECON_AREA", f"'{SRC_CBRN_RECON_AREA}'")
    final_html = final_html.replace("SRC_CHEMICAL_HAZARD_SITE", f"'{SRC_CHEMICAL_HAZARD_SITE}'")
    final_html = final_html.replace("SRC_DECON_AREA_SPECIAL", f"'{SRC_DECON_AREA_SPECIAL}'")
    final_html = final_html.replace("SRC_DECON_POINT_SPECIAL", f"'{SRC_DECON_POINT_SPECIAL}'")
    final_html = final_html.replace("SRC_DETECT_BIOLOGICAL", f"'{SRC_DETECT_BIOLOGICAL}'")
    final_html = final_html.replace("SRC_DETECT_CHEMICAL", f"'{SRC_DETECT_CHEMICAL}'")
    final_html = final_html.replace("SRC_DETECT_RADIATION", f"'{SRC_DETECT_RADIATION}'")
    final_html = final_html.replace("SRC_NUCLEAR_BLAST", f"'{SRC_NUCLEAR_BLAST}'")
    final_html = final_html.replace("SRC_RADIOACTIVE_SITE", f"'{SRC_RADIOACTIVE_SITE}'")
    
    components.html(final_html, height=750, scrolling=False)
