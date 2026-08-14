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
html_map_component = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Map Module - AEGL Ellipse</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <link rel="stylesheet" href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css" />
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js"></script>

    <style>
        html, body {{ margin: 0; padding: 0; height: 100%; font-family: Arial, sans-serif; background: #fff; }}
        #mapContainer {{ width: 100%; height: 430px; position: relative; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }}
        #map {{ width: 100%; height: 100%; }}
        
        #bottomControlsPanel {{
            margin-top: 8px; background: #f5f5f5; padding: 10px; border-radius: 8px;
            border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            max-height: 280px; overflow-y: auto;
        }}
        .controls-row {{ display: flex; gap: 8px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }}
        .controls-row label {{ font-size: 13px; font-weight: bold; color: #333; }}
        .controls-row input {{ padding: 6px 8px; background: #fff; color: #000; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }}
        
        .panel-btn {{
            padding: 6px 10px; background: #e0e0e0; color: #000; border: 1px solid #adadad;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 5px;
        }}
        .panel-btn:hover {{ background: #d4d4d4; }}
        .btn-clear-all {{ background: #b71c1c !important; color: #ffffff !important; border-color: #880e4f !important; }}
        .btn-clear-all:hover {{ background: #d32f2f !important; }}

        #windWidget {{
            position: absolute; bottom: 15px; left: 10px; z-index: 1000;
            background: rgba(26, 26, 26, 0.9); color: #FFD600; padding: 6px;
            border-radius: 8px; border: 1px solid #FFD600; text-align: center; width: 75px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}
        .wind-arrow {{ font-size: 20px; display: inline-block; transition: transform 0.3s ease; }}
        .wind-info {{ font-size: 9px; color: #fff; margin-top: 1px; font-weight: bold; }}

        @media (max-width: 600px) {{
            #mapContainer {{ height: 350px; }}
            .controls-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }}
            .controls-row label {{ grid-column: span 2; }}
            .controls-row input, .panel-btn {{ width: 100%; box-sizing: border-box; }}
        }}
    </style>
</head>
<body>
    <div id="mapContainer">
        <div id="map"></div>
        <div id="windWidget">
            <div class="wind-arrow" id="windArrow">↑</div>
            <div class="wind-info" id="windText">0° | 0 м/с</div>
        </div>
    </div>

    <div id="bottomControlsPanel">
        <div class="controls-row">
            <label>Метеопараметри:</label>
            <input type="number" id="windInput" placeholder="Напрямок (°)" style="width: 110px;" oninput="updateWindWidget()">
            <input type="number" id="windSpeedInput" placeholder="Швидкість (м/с)" style="width: 120px;" oninput="updateWindWidget()">
            <button class="panel-btn" onclick="enableEllipseMode()">Побудувати еліпс AEGL</button>
            <button class="panel-btn btn-clear-all" onclick="clearAllShapes()">Очистити все</button>
        </div>
    </div>

    <script>
        var map = L.map('map').setView([50.45, 30.52], 10);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }}).addTo(map);

        var ellipseMode = false;
        var state = {{ shapes: [], objects: [] }};
        var createdLayers = {{}};

        function updateWindWidget() {{
            let deg = parseFloat(document.getElementById("windInput").value) || 0;
            let spd = parseFloat(document.getElementById("windSpeedInput").value) || 0;
            
            // Стрілка вказує КУДИ дме вітер (додаємо 180° до метеорологічного напрямку)
            document.getElementById("windArrow").style.transform = "rotate(" + (deg + 180) + "deg)";
            document.getElementById("windText").innerText = deg + "° | " + spd + " м/с";
        }}

        function enableEllipseMode() {{ 
            ellipseMode = true; 
            alert("Клікніть на карті у точці джерела викиду для побудови еліпса AEGL.");
        }}

        function clearAllShapes() {{
            for (let id in createdLayers) {{
                map.removeLayer(createdLayers[id]);
            }}
            createdLayers = {{}};
            state.shapes = [];
            state.objects = [];
            saveState();
        }}

        function getEllipsePoints(lat, lng, rX, rY, tiltDeg) {{
            let points = [];
            let tiltRad = tiltDeg * Math.PI / 180;
            
            // Центр еліпса зміщується на напіввісь rX за напрямком перенесення вітром
            let centerLat = lat + (rX * Math.cos(tiltRad)) / 111111;
            let centerLng = lng + (rX * Math.sin(tiltRad)) / (111111 * Math.cos(lat * Math.PI / 180));

            for (let i = 0; i <= 360; i += 5) {{
                let rad = i * Math.PI / 180;
                let x = rX * Math.cos(rad);
                let y = rY * Math.sin(rad);

                // Поворот точок відносно осі перенесення
                let rotX = x * Math.cos(tiltRad) - y * Math.sin(tiltRad);
                let rotY = x * Math.sin(tiltRad) + y * Math.cos(tiltRad);

                let pLat = centerLat + (rotX / 111111);
                let pLng = centerLng + (rotY / (111111 * Math.cos(centerLat * Math.PI / 180)));
                points.push([pLat, pLng]);
            }}
            return points;
        }}

        function render() {{
            // Очищення вилучених шарів
            for (let id in createdLayers) {{
                let exists = state.shapes.some(s => s.id === id);
                if (!exists) {{
                    map.removeLayer(createdLayers[id]);
                    delete createdLayers[id];
                }}
            }}

            // Побудова зон AEGL
            state.shapes.forEach(shape => {{
                if (shape.isEllipse && !createdLayers[shape.id]) {{
                    let pts = getEllipsePoints(shape.ellipseCenter[0], shape.ellipseCenter[1], shape.radiusX, shape.radiusY, shape.tilt);
                    
                    let color = "#ef4444"; // AEGL-3 (Червоний - висока небезпека)
                    if (shape.id.endsWith("_2")) color = "#f97316"; // AEGL-2 (Помаранчевий - середня небезпека)
                    if (shape.id.endsWith("_3")) color = "#eab308"; // AEGL-1 (Жовтий - пороговий рівень)

                    let polygon = L.polygon(pts, {{
                        color: color,
                        weight: 2,
                        fillColor: color,
                        fillOpacity: 0.25
                    }}).addTo(map);

                    createdLayers[shape.id] = polygon;
                }}
            }});
        }}

        function saveState() {{
            if (window.parent && window.parent.postMessage) {{
                window.parent.postMessage({{ type: "streamlit:setComponentValue", value: state }}, "*");
            }}
        }}

        map.on("click", function(e) {{
            if (map.pm && (map.pm.globalDrawModeEnabled() || map.pm.globalRemovalModeEnabled())) return;

            if (ellipseMode) {{
                let lengthInput = prompt("Введіть глибину/довжину розповсюдження (у метрах):", "5000");
                if (!lengthInput || isNaN(parseFloat(lengthInput))) {{
                    ellipseMode = false;
                    return;
                }}

                let totalLength = parseFloat(lengthInput);
                let rX = totalLength / 2;

                let windDegVal = document.getElementById("windInput").value;
                let windSpeedVal = document.getElementById("windSpeedInput").value;

                let windDeg = windDegVal !== "" ? parseFloat(windDegVal) : 0;
                let windSpeed = windSpeedVal !== "" ? parseFloat(windSpeedVal) : 0;

                // Розрахунок ширини факела від швидкості вітру
                let widthFactor = 0.25;
                if (windSpeed <= 1.5) {{
                    widthFactor = 0.40;
                }} else if (windSpeed > 1.5 && windSpeed <= 4.0) {{
                    widthFactor = 0.25;
                }} else {{
                    widthFactor = 0.15;
                }}

                let rY = rX * widthFactor;
                let groupId = Date.now();

                // Порядок додавання: AEGL-3 (найбільший), AEGL-2, AEGL-1 (найменший)
                state.shapes.push({{ id: groupId + "_1", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: rX, radiusY: rY, tilt: windDeg }});
                state.shapes.push({{ id: groupId + "_2", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: rX * 0.6, radiusY: rY * 0.6, tilt: windDeg }});
                state.shapes.push({{ id: groupId + "_3", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: rX * 0.3, radiusY: rY * 0.3, tilt: windDeg }});

                saveState();
                render();
                ellipseMode = false;
            }}
        }});
    </script>
</body>
</html>
"""
