import streamlit as st
import pandas as pd
import json
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. НАЛАШТУВАННЯ СТОРІНКИ ТА СТИЛІВ STREAMLIT
# ==========================================
st.set_page_config(page_title="РХБ ОБСТАНОВКА - АВТОНОМНА КАРТА", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stButton button {
    font-weight: bold; width: 100%; height: 3em; border-radius: 8px; 
    background-color: #FFD600 !important; color: black !important;
    border: 1px solid #cca300 !important;
}
.stButton button:hover { background-color: #ffea00 !important; }
</style>
""", unsafe_allow_html=True)

# Ініціалізація бази точок розвідки
if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = [
        {"lat": 50.45, "lng": 30.52, "label": "Хімія: Зарин 0.05 мг/м³", "date": "17.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"},
        {"lat": 50.46, "lng": 30.53, "label": "Радіація: 0.25 мкЗв/год", "date": "16.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"}
    ]

st.header("☢️ МОДУЛЬ 1: ФАКТИЧНА РХБ ОБСТАНОВКА ПО ДНЯХ РОЗВІДКИ")

col_map, col_gui = st.columns([3, 1])

# ==========================================
# 2. ПУЛЬТ УПРАВЛІННЯ ДАНИМИ (БІЧНА ПАНЕЛЬ)
# ==========================================
with col_gui:
    st.subheader("⚙️ УПРАВЛІННЯ ДАНИМИ")
    
    with st.expander("➕ Додати точку розвідки вручну"):
        m_type = st.radio("Тип забруднення:", ["Радіоактивне", "Хімічне"])
        m_lat = st.number_input("Широта (Lat)", value=50.4500, format="%.5f")
        m_lon = st.number_input("Довгота (Lon)", value=30.5200, format="%.5f")
        
        if m_type == "Радіоактивне":
            r_val = st.number_input("Показник радіації", value=0.15)
            r_uni = st.selectbox("Одиниця виміру", ["мкЗв/год", "мЗв/год"])
            lbl = f"Радіація: {r_val} {r_uni}"
            ico = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"
        else:
            c_sub = st.text_input("Речовина", value="Іприт")
            c_val = st.number_input("Концентрація", value=0.1)
            c_uni = st.selectbox("Одиниця виміру", ["мг/м³", "ppm"])
            lbl = f"Хімія: {c_sub} {c_val} {c_uni}"
            ico = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"
            
        m_date = st.date_input("Дата розвідки", value=datetime.now()).strftime("%d.%m.%Y")
        
        if st.button("Зберегти точку в базу"):
            st.session_state.rkhb_points.append({"lat": m_lat, "lng": m_lon, "label": lbl, "date": m_date, "icon": ico})
            st.rerun()

    st.divider()
    
    file = st.file_uploader("📥 Імпорт розвідки з CSV", type=["csv"])
    if file:
        df_csv = pd.read_csv(file)
        for _, row in df_csv.iterrows():
            st.session_state.rkhb_points.append({
                "lat": float(row['lat']), "lng": float(row['lng']),
                "label": str(row['label']), "date": str(row['date']), "icon": str(row['icon'])
            })
        st.success("Дані успішно імпортовано!")
        st.rerun()

    if st.button("🗑️ Очистити ВСІ точки"):
        st.session_state.rkhb_points = []
        st.rerun()

    if st.session_state.rkhb_points:
        st.markdown("### 📊 Поточні точки:")
        df_view = pd.DataFrame(st.session_state.rkhb_points)
        st.dataframe(df_view[["date", "label", "lat", "lng"]], use_container_width=True, height=180)
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

    <style>
        html, body { margin: 0; padding: 0; height: 100%; font-family: sans-serif; overflow: hidden; }
        #map { width: 100%; height: 100vh; background: #e5e3df; }
        
        #mapControlsPanel {
            position: absolute; top: 10px; right: 10px; z-index: 1000;
            background: rgba(26, 26, 26, 0.9); color: #fff; padding: 10px;
            border-radius: 8px; border: 2px solid #FFD600; width: 220px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        #mapControlsPanel select, #mapControlsPanel input {
            width: 100%; padding: 5px; margin-top: 5px; margin-bottom: 8px;
            background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; font-size: 12px;
            box-sizing: border-box;
        }
        #mapControlsPanel label { font-size: 11px; font-weight: bold; color: #FFD600; }
        .panel-btn {
            width: 100%; padding: 6px; background: #444; color: #fff; border: 1px solid #555;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 11px; margin-bottom: 4px;
        }
        .panel-btn:hover { background: #555; }
        
        #windWidget {
            position: absolute; bottom: 40px; left: 10px; z-index: 1000;
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
        .cbrn-text-lbl {
            font-size: 12px; font-weight: bold; color: blue; white-space: nowrap;
            text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
            border-bottom: 2px solid blue; display: inline-block;
        }
    </style>
</head>
<body>

    <div id="map"></div>

    <div id="windWidget">
        <div class="wind-arrow" id="arrow">↑</div>
        <div class="wind-info" id="degInfo">0°</div>
        <div class="wind-info" id="speedInfo">0 м/с</div>
    </div>

    <div id="mapControlsPanel">
        <label>⚙️ ОПЕРАТИВНИЙ РЕЖИМ</label>
        <select id="signSelect">
            <option value="">-- Оберіть умовний знак --</option>
            <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg">Точка радіоактивного забруднення</option>
            <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg">Точка хімічного забруднення</option>
            <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_biological.svg">Точка біологічного зараження</option>
            <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/nuclear_blast.svg">Епіцентр ядерного вибуху</option>
            <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/cbrn_post.svg">Пост спостереження РХБ</option>
        </select>

        <button class="panel-btn" style="background: #5c3a21;" id="ellipseBtn">Побудувати Еліпс AEGL</button>
        <button class="panel-btn" style="background: #1565c0;" id="textBtn">Додати Текст</button>
        
        <hr style="border: 0; border-top: 1px dashed #555; margin: 8px 0;">
        
        <label>💨 НАЛАШТУВАННЯ МЕТЕО</label>
        <input type="number" id="wDegInput" placeholder="Напрямок вітру (0-360)" min="0" max="360" value="0">
        <input type="number" id="wSpeedInput" placeholder="Швидкість вітру (м/с)" min="0" value="0" step="0.1">
        <button class="panel-btn" style="background: #FFD600; color:#000;" id="applyMeteoBtn">Застосувати метео</button>
    </div>

<script>
    // Ініціалізація карти (виправлені фігурні дужки для підключення тайлів)
    var map = L.map('map', { zoomControl: true }).setView([48.3, 31.1], 6);
    
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19, attribution: '© OpenStreetMap'
    }).addTo(map);

    var satLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        attribution: '© Google'
    });

    // Налаштування лінійок та вимірювань Geoman (OSM)
    map.pm.addControls({
        position: 'topleft',
        drawMarker: false, drawCircleMarker: false, drawPolyline: true,
        drawRectangle: true, drawPolygon: true, drawCircle: true,
        removalMode: true, editMode: false, dragMode: false
    });
    
    map.pm.setGlobalOptions({
        measurements: { display: true, radius: true, totalLength: true, segmentLength: true }
    });
    map.pm.setLang('uk');

    var baseMaps = { "🗺️ Карта OSM": osmLayer, "🛰️ Супутник Google": satLayer };
    var dateLayers = {}; 
    var layerControl = L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

    // Отримання бази точок розвідки з Python (безпечна заміна)
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
            
            var labelHtml = "<div class='cbrn-text-lbl'>" + pt.label + "<br><span style='font-weight:normal; font-size:10px; color:#555;'>" + dateStr + "</span></div>";
            marker.bindTooltip(labelHtml, { permanent: true, direction: 'bottom', offset: [0, 10], className: 'leaflet-div-icon' });
            
            marker.addTo(dateLayers[dateStr]);
        });
    }

    // Робота зі знаками, текстом та еліпсами
    var activeIcon = ""; var textMode = false; var ellipseMode = false;

    document.getElementById('signSelect').onchange = function(e) {
        activeIcon = e.target.value; textMode = false; ellipseMode = false;
    };
    document.getElementById('textBtn').onclick = function() {
        textMode = true; ellipseMode = false; activeIcon = ""; document.getElementById('signSelect').value = "";
    };
    document.getElementById('ellipseBtn').onclick = function() {
        ellipseMode = true; textMode = false; activeIcon = ""; document.getElementById('signSelect').value = "";
    };

    map.on('click', function(e) {
        if (activeIcon) {
            L.marker(e.latlng, { icon: L.icon({ iconUrl: activeIcon, iconSize: [28, 28], iconAnchor: [14, 14] }) }).addTo(map);
        }
        if (textMode) {
            var txt = prompt("Введіть оперативно-тактичний підпис:");
            if (txt) {
                L.marker(e.latlng, {
                    icon: L.divIcon({ className: 'leaflet-div-icon', html: "<span class='cbrn-text-lbl'>" + txt + "</span>" })
                }).addTo(map);
            }
            textMode = false;
        }
        if (ellipseMode) {
            var rX = prompt("Довжина зони AEGL (метри за вітром):", "4000"); if (!rX) return;
            var rY = prompt("Ширина зони AEGL (метри бокова):", "1500"); if (!rY) return;
            var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
            
            drawCbrnEllipse(e.latlng.lat, e.latlng.lng, parseFloat(rX), parseFloat(rY), deg);
            ellipseMode = false;
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
            var poly = L.polygon(points, { color: 'black', weight: 1, fillColor: colors[idx], fillOpacity: opacities[idx] }).addTo(map);
            poly.on('click', function(ev) { L.DomEvent.stopPropagation(ev); if(confirm("Видалити зону хімічного забруднення?")) map.removeLayer(poly); });
        });
    }

    document.getElementById('applyMeteoBtn').onclick = function() {
        var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
        var speed = parseFloat(document.getElementById('wSpeedInput').value) || 0;
        document.getElementById('arrow').style.transform = "rotate(" + ((deg + 180) % 360) + "deg)";
        document.getElementById('degInfo').innerText = deg + "°";
        document.getElementById('speedInfo').innerText = speed + " м/с";
    };

    // Відображення радіуса кіл
    map.on('pm:create', function(e) {
        if (e.shape === 'Circle') {
            var radius = e.layer.getRadius();
            var txt = "Радіус: " + (radius >= 1000 ? (radius/1000).toFixed(2) + " км" : Math.round(radius) + " м");
            e.layer.bindTooltip(txt, { permanent: true, direction: 'center', className: 'size-tooltip' }).openTooltip();
        }
    });
</script>
</body>
</html>
"""

# ==========================================
# 4. РЕНДЕРИНГ КОМПОНЕНТА КАРТИ В STREAMLIT
# ==========================================
with col_map:
    # Безпечно замінюємо маркер на реальний масив даних із сесії Python
    final_html = html_map_component.replace("DATA_FROM_PYTHON", points_json)
    
    # Виводимо карту на екран
    components.html(final_html, height=750, scrolling=False)
