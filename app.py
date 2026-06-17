import streamlit as st
import pandas as pd
import json
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. НАЛАШТУВАННЯ СТОРІНКИ ТА СТИЛІВ STREAMLIT
# ==========================================
st.set_page_config(page_title="РХБ ОБСТАНОВКА", layout="wide")

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
/* Стиль для додаткової кнопки імпорту */
.import-btn button {
    background-color: #4CAF50 !important; color: white !important;
    border: 1px solid #388E3C !important;
}
.import-btn button:hover { background-color: #45a049 !important; }
</style>
""", unsafe_allow_html=True)

# Ініціалізація бази точок розвідки
if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = [
        {"lat": 50.45, "lng": 30.52, "label": "Іприт - 0.05 мг/м³", "date": "17.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"},
        {"lat": 50.46, "lng": 30.53, "label": "0.25 мкЗв/год", "date": "16.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"}
    ]

# Буферні змінні координат
if "captured_lat" not in st.session_state:
    st.session_state.captured_lat = 50.4500
if "captured_lng" not in st.session_state:
    st.session_state.captured_lng = 30.5200

# Зчитування нових координат з URL-параметрів карти
if "click_lat" in st.query_params and "click_lng" in st.query_params:
    try:
        st.session_state.captured_lat = float(st.query_params["click_lat"])
        st.session_state.captured_lng = float(st.query_params["click_lng"])
    except (ValueError, TypeError):
        pass

st.header("☢️ МОДУЛЬ 1: ФАКТИЧНА РХБ ОБСТАНОВКА")

col_map, col_gui = st.columns([3, 1])

# ==========================================
# 2. ПУЛЬТ УПРАВЛІННЯ ДАНИМИ (БІЧНА ПАНЕЛЬ)
# ==========================================
with col_gui:
    st.subheader("⚙️ УПРАВЛІННЯ ДАНИМИ")
    
    st.markdown(f"<div class='coord-box'>📍 {st.session_state.captured_lat:.5f} , {st.session_state.captured_lng:.5f}</div>", unsafe_allow_html=True)
    
    with st.expander("➕ Параметри точки вимірювання", expanded=True):
        m_type = st.radio("Тип забруднення:", ["Радіоактивне", "Хімічне"])
        
        m_lat = st.number_input("Широта (Lat)", value=st.session_state.captured_lat, format="%.5f", key=f"lat_{st.session_state.captured_lat}")
        m_lon = st.number_input("Довгота (Lon)", value=st.session_state.captured_lng, format="%.5f", key=f"lng_{st.session_state.captured_lng}")
        
        if m_type == "Радіоактивне":
            r_val = st.number_input("Показник радіації", value=0.15, step=0.01)
            r_uni = st.selectbox("Одиниця виміру", ["мкЗв/год", "мЗв/год"])
            lbl = f"{r_val} {r_uni}"
            ico = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"
        else:
            c_sub = st.text_input("Речовина", value="Іприт")
            c_val = st.number_input("Концентрація", value=0.10, step=0.01)
            c_uni = st.selectbox("Одиниця виміру", ["мг/м³", "ppm"])
            lbl = f"{c_sub} - {c_val} {c_uni}"
            ico = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"
            
        m_date = datetime.now().strftime("%d.%m.%Y")
        st.caption(f"📅 Дата фіксації (авто): {m_date}")
        
        if st.button("Нанести точку на карту", type="primary"):
            st.session_state.rkhb_points.append({"lat": m_lat, "lng": m_lon, "label": lbl, "date": m_date, "icon": ico})
            st.rerun()

    st.divider()
    
    # ОКРЕМИЙ БЛОК ДЛЯ ЗАВАНТАЖЕННЯ ТА НАНЕСЕННЯ ТОЧОК З CSV
    st.write("📊 **Імпорт бази даних розвідки**")
    file = st.file_uploader("Виберіть CSV файл:", type=["csv"], label_visibility="collapsed")
    if file:
        try:
            df_csv = pd.read_csv(file)
            st.dataframe(df_csv.head(3), use_container_width=True) # Коротке прев'ю
            
            st.markdown('<div class="import-btn">', unsafe_allow_html=True)
            if st.button("📥 Додати точки на карту з таблиці"):
                orig_cols = list(df_csv.columns)
                df_csv.columns = [col.strip().lower() for col in df_csv.columns]
                
                lat_col = next((c for c in df_csv.columns if c in ['lat', 'latitude', 'широта']), None)
                lng_col = next((c for c in df_csv.columns if c in ['lng', 'lon', 'longitude', 'довгота']), None)
                lbl_col = next((c for c in df_csv.columns if c in ['label', 'text', 'напис', 'показник']), None)
                dat_col = next((c for c in df_csv.columns if c in ['date', 'дата']), None)
                ico_col = next((c for c in df_csv.columns if c in ['icon', 'іконка', 'знак']), None)
                
                if lat_col and lng_col:
                    for idx, row in df_csv.iterrows():
                        real_lat_name = orig_cols[list(df_csv.columns).index(lat_col)]
                        real_lng_name = orig_cols[list(df_csv.columns).index(lng_col)]
                        real_lbl_name = orig_cols[list(df_csv.columns).index(lbl_col)] if lbl_col else None
                        real_dat_name = orig_cols[list(df_csv.columns).index(dat_col)] if dat_col else None
                        real_ico_name = orig_cols[list(df_csv.columns).index(ico_col)] if ico_col else None
                        
                        label_text = str(row[real_lbl_name]) if real_lbl_name else "Точка розвідки"
                        date_text = str(row[real_dat_name]) if real_dat_name else datetime.now().strftime("%d.%m.%Y")
                        
                        if real_ico_name and pd.notna(row[real_ico_name]):
                            icon_url = str(row[real_ico_name])
                        else:
                            if "мг/" in label_text or "ppm" in label_text or "іприт" in label_text.lower():
                                icon_url = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"
                            else:
                                icon_url = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"

                        st.session_state.rkhb_points.append({
                            "lat": float(row[real_lat_name]), "lng": float(row[real_lng_name]),
                            "label": label_text, "date": date_text, "icon": icon_url
                        })
                    st.success(f"Успішно нанесено {len(df_csv)} точок!")
                    st.rerun()
                else:
                    st.error("Помилка! У файлі відсутні колонки координат.")
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Помилка читання CSV: {str(e)}")

    if st.button("🗑️ Очистити ВСІ точки"):
        st.session_state.rkhb_points = []
        st.session_state.captured_lat = 50.4500
        st.session_state.captured_lng = 30.5200
        st.query_params.clear()
        st.rerun()

    if st.session_state.rkhb_points:
        df_view = pd.DataFrame(st.session_state.rkhb_points)
        st.dataframe(df_view[["date", "label", "lat", "lng"]], use_container_width=True, height=110)
        st.download_button("💾 Експорт бази в CSV", df_view.to_csv(index=False), "rkhb_data.csv", "text/csv")


# Підготовка JSON-даних для передачі в карту
points_json = json.dumps(st.session_state.rkhb_points, ensure_ascii=False)

# ==========================================
# 3. АВТОНОМНИЙ HTML/JS КОД КАРТИ LEAFLET
# ==========================================
html_map_component = """
<!DOCTYPE html>
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
        #mapContainer { width: 100%; height: 580px; position: relative; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }
        #map { width: 100%; height: 100%; }
        
        #bottomControlsPanel {
            margin-top: 12px; background: #f5f5f5; padding: 12px; border-radius: 8px;
            border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .controls-row { display: flex; gap: 12px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
        .controls-row:last-child { margin-bottom: 0; }
        
        .controls-row select, .controls-row input {
            padding: 6px 10px; background: #fff; color: #000; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
        }
        .controls-row label { font-size: 13px; font-weight: bold; color: #333; }
        
        .panel-btn {
            padding: 6px 12px; background: #e0e0e0; color: #000; border: 1px solid #adadad;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 5px;
        }
        .panel-btn:hover { background: #d4d4d4; }
        
        .btn-stop { background: #ffcdd2 !important; color: #b71c1c !important; border-color: #e57373 !important; }
        .btn-stop:hover { background: #ef9a9a !important; }

        #windWidget {
            position: absolute; bottom: 20px; left: 10px; z-index: 1000;
            background: rgba(26, 26, 26, 0.9); color: #FFD600; padding: 8px;
            border-radius: 8px; border: 1px solid #FFD600; text-align: center; width: 80px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .wind-arrow { font-size: 24px; display: inline-block; transition: transform 0.5s; }
        .wind-info { font-size: 10px; color: #fff; margin-top: 2px; font-weight: bold; }

        .size-tooltip {
            background: rgba(0, 0, 0, 0.8) !important; border: 1px solid #FFD600 !important;
            color: #fff !important; font-weight: bold; font-size: 11px; padding: 3px 6px; border-radius: 4px;
        }
        
        .leaflet-div-icon {
            background: transparent !important; border: none !important; box-shadow: none !important;
        }
        .cbrn-military-lbl {
            font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; color: #000 !important;
            text-align: center; display: inline-block; white-space: nowrap; line-height: 1.3; background: transparent !important;
        }
        .cbrn-line-divider {
            border-bottom: 2px solid #000 !important; width: 100%; display: block; margin: 2px 0;
        }
        .cbrn-date-sub {
            font-size: 11px; font-weight: bold; color: #000 !important; display: block;
        }
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
            <label>🧭 ОПЕРАТИВНІ ЕЛЕМЕНТИ:</label>
            <select id="signSelect">
                <option value="">-- Оберіть умовний знак для встановлення кліком --</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg">Точка радіоактивного забруднення</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg">Точка хімічного забруднення</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_biological.svg">Точка біологічного зараження</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/nuclear_blast.svg">Епіцентр ядерного вибуху</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/cbrn_post.svg">Пост спостереження РХБ</option>
            </select>
            <button class="panel-btn" style="background: #e1f5fe; border-color:#0288d1;" id="textBtn">📝 Додати Текст</button>
            <button class="panel-btn" style="background: #efebe9; border-color:#5d4037;" id="ellipseBtn">📐 Еліпс AEGL</button>
            <button class="panel-btn btn-stop" id="stopBtn">🛑 СТОП</button>
        </div>
        
        <div class="controls-row">
            <label>💨 МЕТЕО — Напрямок вітру:</label>
            <input type="number" id="wDegInput" placeholder="Градуси (0-360)" min="0" max="360" value="0" style="width:130px;">
            <label>Швидкість вітру:</label>
            <input type="number" id="wSpeedInput" placeholder="м/с" min="0" value="0" step="0.1" style="width:90px;">
            
            <button class="panel-btn" style="background: #fff59d; border-color:#fbc02d;" id="applyMeteoBtn">🌀 Застосувати</button>
            
            <button class="panel-btn" style="background: #c8e6c9; border-color:#388e3c; margin-left: 20px;" id="pngBtn">🖼️ Зберегти PNG</button>
            <button class="panel-btn" style="background: #ffcdd2; border-color:#d32f2f;" id="printBtn">🖨️ Зберегти PDF / Друк</button>
        </div>
    </div>

<script>
    var map = L.map('map', { zoomControl: true }).setView([48.3, 31.1], 6);
    
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '© OpenStreetMap'
    }).addTo(map);

    var satLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        attribution: '© Google'
    });

    // СТАНДАРТНІ КНОПКИ ДЛЯ КОРИГУВАННЯ, ПЕРЕТЯГУВАННЯ ТА ВИДАЛЕННЯ ФІГУР
    map.pm.addControls({
        position: 'topleft',
        drawMarker: false, drawCircleMarker: false, drawPolyline: true,
        drawRectangle: true, drawPolygon: true, drawCircle: true,
        editMode: true,    // Кнопка редагування геометрії фігур
        dragMode: true,    // Кнопка перетягування фігур
        removalMode: true  // Кнопка видалення обраних фігур
    });
    
    map.pm.setGlobalOptions({
        measurements: { display: true, radius: true, totalLength: true, segmentLength: true },
        pathOptions: { color: '#000', fillColor: '#FFD600', fillOpacity: 0.4, weight: 2 }
    });
    map.pm.setLang('uk');

    var baseMaps = { "🗺️ Карта OSM": osmLayer, "🛰️ Супутник Google": satLayer };
    var dateLayers = {}; 
    var layerControl = L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

    var inputPoints = DATA_FROM_PYTHON;
    
    if(Array.isArray(inputPoints)) {
        inputPoints.forEach(function(pt) {
            var dateStr = pt.date || "Базові дані";
            if (!dateLayers[dateStr]) {
                dateLayers[dateStr] = L.layerGroup().addTo(map);
                layerControl.addOverlay(dateLayers[dateStr], "📅 " + dateStr);
            }
            
            var customIcon = L.icon({ iconUrl: pt.icon, iconSize: [28, 28], iconAnchor: [14, 14] });
            var marker = L.marker([pt.lat, pt.lng], { icon: customIcon });
            
            var labelHtml = "<div class='cbrn-military-lbl'>" + 
                                "<span>" + pt.label + "</span>" + 
                                "<div class='cbrn-line-divider'></div>" + 
                                "<span class='cbrn-date-sub'>" + dateStr + "</span>" + 
                            "</div>";
                            
            marker.bindTooltip(labelHtml, { permanent: true, direction: 'bottom', offset: [0, 14], className: 'leaflet-div-icon' });
            marker.addTo(dateLayers[dateStr]);
        });
    }

    var activeIcon = ""; var textMode = false; var ellipseMode = false;

    function clearModes() {
        activeIcon = ""; textMode = false; ellipseMode = false;
        document.getElementById('signSelect').value = "";
    }

    document.getElementById('signSelect').onchange = function(e) {
        activeIcon = e.target.value; textMode = false; ellipseMode = false;
    };
    document.getElementById('textBtn').onclick = function() {
        textMode = true; ellipseMode = false; activeIcon = ""; document.getElementById('signSelect').value = "";
    };
    document.getElementById('ellipseBtn').onclick = function() {
        ellipseMode = true; textMode = false; activeIcon = ""; document.getElementById('signSelect').value = "";
    };
    document.getElementById('stopBtn').onclick = function() {
        clearModes();
    };

    map.on('click', function(e) {
        // Якщо інструменти вимкнені — працює передача координат кліку
        if (!activeIcon && !textMode && !ellipseMode) {
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            
            var url = new URL(window.parent.location.href);
            url.searchParams.set('click_lat', lat.toFixed(5));
            url.searchParams.set('click_lng', lng.toFixed(5));
            window.parent.history.replaceState({}, '', url);
            
            window.parent.postMessage({type: "streamlit:set_query_params", params: {click_lat: lat.toFixed(5), click_lng: lng.toFixed(5)}}, "*");
            return;
        }

        if (activeIcon) {
            L.marker(e.latlng, { icon: L.icon({ iconUrl: activeIcon, iconSize: [28, 28], iconAnchor: [14, 14] }) }).addTo(map);
        }
        if (textMode) {
            var txt = prompt("Введіть оперативно-тактичний підпис:");
            if (txt) {
                L.marker(e.latlng, {
                    icon: L.divIcon({ className: 'leaflet-div-icon', html: "<span class='cbrn-military-lbl' style='font-size:13px; background:transparent;'>️" + txt + "</span>" })
                }).addTo(map);
            }
        }
        if (ellipseMode) {
            var rX = prompt("Довжина зони AEGL (метри за вітром):", "4000"); if (!rX) return;
            var rY = prompt("Ширина зони AEGL (метри бокова):", "1500"); if (!rY) return;
            var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
            drawCbrnEllipse(e.latlng.lat, e.latlng.lng, parseFloat(rX), parseFloat(rY), deg);
        }
    });

    function drawCbrnEllipse(centerLat, centerLng, rx, ry, deg) {
        var angles = [1, 0.6, 0.3];
        var colors = ["#ffcc00", "#ff9900", "#cc0000"];
        var opacities = [0.25, 0.4, 0.6];
        var windRad = (deg + 180) * Math.PI / 180;

        angles.forEach(function(scale, idx) {
            var curRx = rx * scale; var curRy = ry * scale;
            var points = [];
            for (var i = 0; i <= 64; i++) {
                var angle = (i / 64) * 2 * Math.PI;
                var x = curRy * Math.cos(angle);
                var y = curRx * Math.sin(angle);
                var rotX = x * Math.cos(windRad) + (y + curRx) * Math.sin(windRad);
                var rotY = -x * Math.sin(windRad) + (y + curRx) * Math.cos(windRad);
                var latOffset = rotY / 111320;
                var lngOffset = rotX / (111320 * Math.cos(centerLat * Math.PI / 180));
                points.push([centerLat + latOffset, centerLng + lngOffset]);
            }
            L.polygon(points, { color: 'black', weight: 1, fillColor: colors[idx], fillOpacity: opacities[idx] }).addTo(map);
        });
    }

    document.getElementById('applyMeteoBtn').onclick = function() {
        var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
        var speed = parseFloat(document.getElementById('wSpeedInput').value) || 0;
        document.getElementById('arrow').style.transform = "rotate(" + ((deg + 180) % 360) + "deg)";
        document.getElementById('degInfo').innerText = deg + "°";
        document.getElementById('speedInfo').innerText = speed + " м/с";
    };

    map.on('pm:create', function(e) {
        if (e.shape === 'Circle') {
            var radius = e.layer.getRadius();
            var txt = "Радіус: " + (radius >= 1000 ? (radius/1000).toFixed(2) + " км" : Math.round(radius) + " м");
            e.layer.bindTooltip(txt, { permanent: true, direction: 'center', className: 'size-tooltip' }).openTooltip();
        }
    });

    document.getElementById('pngBtn').onclick = function() {
        var container = document.getElementById('mapContainer');
        var controls = document.querySelector('.leaflet-control-container');
        controls.style.display = 'none';
        html2canvas(container, { useCORS: true, allowTaint: true }).then(function(canvas) {
            var link = document.createElement('a');
            link.download = 'CBRN_Map_Export.png';
            link.href = canvas.toDataURL();
            link.click();
            controls.style.display = 'block';
        });
    };

    document.getElementById('printBtn').onclick = function() {
        window.print();
    };
</script>
</body>
</html>
"""

# ==========================================
# 4. РЕНДЕРИНГ КОМПОНЕНТА КАРТИ В STREAMLIT
# ==========================================
with col_map:
    final_html = html_map_component.replace("DATA_FROM_PYTHON", points_json)
    components.html(final_html, height=720, scrolling=False)
