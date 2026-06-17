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
</style>
""", unsafe_allow_html=True)

# Ініціалізація бази точок розвідки
if "rkhb_points" not in st.session_state:
    st.session_state.rkhb_points = [
        {"lat": 50.45, "lng": 30.52, "label": "Іприт - 0.05 мг/м³", "date": "17.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"},
        {"lat": 50.46, "lng": 30.53, "label": "Радіація: 0.25 мкЗв/год", "date": "16.06.2026", "icon": "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg"}
    ]

# Виключено слова "по днях розвідки"
st.header("☢️ МОДУЛЬ 1: ФАКТИЧНА РХБ ОБСТАНОВКА")

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
            lbl = f"{c_sub} - {c_val} {c_uni}"
            ico = "https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg"
            
        m_date = st.date_input("Дата розвідки", value=datetime.now()).strftime("%d.%m.%Y")
        
        # Назву змінено на "Нанести точку на карту"
        if st.button("Нанести точку на карту"):
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
        st.dataframe(df_view[["date", "label", "lat", "lng"]], use_container_width=True, height=150)
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

    <style>
        html, body { margin: 0; padding: 0; font-family: Arial, sans-serif; background: #fff; }
        #mapContainer { width: 100%; height: 600px; position: relative; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }
        #map { width: 100%; height: 100%; }
        
        /* НОВА ПАНЕЛЬ ПІД КАРТОЮ В 2 РЯДКИ */
        #bottomControlsPanel {
            margin-top: 15px; background: #f5f5f5; padding: 12px; border-radius: 8px;
            border: 1px solid #ddd; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .controls-row { display: flex; gap: 15px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
        .controls-row:last-child { margin-bottom: 0; }
        
        .controls-row select, .controls-row input {
            padding: 6px 10px; background: #fff; color: #000; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;
        }
        .controls-row label { font-size: 12px; font-weight: bold; color: #333; }
        
        .panel-btn {
            padding: 6px 12px; background: #e0e0e0; color: #000; border: 1px solid #adadad;
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 5px;
        }
        .panel-btn:hover { background: #d4d4d4; }
        
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
        
        /* НОВИЙ ФОРМАТ ПІДПИСУ ТОЧОК ЗА СТАНДАРТОМ (ЧОРНИЙ ТЕКСТ ТА ЛІНІЯ НА ДОВЖИНУ ТЕКСТУ) */
        .cbrn-military-lbl {
            font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; color: #000 !important;
            text-align: center; display: inline-block; white-space: nowrap; line-height: 1.2;
        }
        .cbrn-line-divider {
            border-bottom: 2px solid #000 !important; width: 100%; display: block; margin: 2px 0;
        }
        .cbrn-date-sub {
            font-size: 10px; font-weight: normal; color: #000 !important; display: block;
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
            <label>🧭 НАНЕСЕННЯ ЕЛЕМЕНТІВ:</label>
            <select id="signSelect">
                <option value="">-- Оберіть умовний знак для кліку на карту --</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_radiation.svg">Точка радіоактивного забруднення</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_chemical.svg">Точка хімічного забруднення</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/detect_biological.svg">Точка біологічного зараження</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/nuclear_blast.svg">Епіцентр ядерного вибуху</option>
                <option value="https://raw.githubusercontent.com/sergsh1125-dotcom/CBRN-panel/main/assets/svg/cbrn_post.svg">Пост спостереження РХБ</option>
            </select>
            <button class="panel-btn" style="background: #e1f5fe; border-color:#0288d1;" id="textBtn">📝 Додати Текст (Чорний)</button>
            <button class="panel-btn" style="background: #efebe9; border-color:#5d4037;" id="ellipseBtn">📐 Побудувати Еліпс AEGL</button>
        </div>
        
        <div class="controls-row">
            <label>💨 НАЛАШТУВАННЯ МЕТЕО:</label>
            <input type="number" id="wDegInput" placeholder="Напрямок вітру (°)" min="0" max="360" value="0" style="width:140px;">
            <input type="number" id="wSpeedInput" placeholder="Швидкість (м/с)" min="0" value="0" step="0.1" style="width:120px;">
            <button class="panel-btn" style="background: #fff59d; border-color:#fbc02d;" id="applyMeteoBtn">🌀 Застосувати метео</button>
            
            <div style="margin-left: auto; display: flex; gap: 8px;">
                <button class="panel-btn" style="background: #c8e6c9; border-color:#388e3c;" id="pngBtn">🖼️ Експорт в PNG</button>
                <button class="panel-btn" style="background: #ffcdd2; border-color:#d32f2f;" id="pdfBtn">📄 Експорт в PDF</button>
            </div>
        </div>
    </div>

<script>
    // Ініціалізація карти
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
            
            // НОВИЙ ФОРМАТ: Чорний текст, лінія чітко по довжині, дата під лінією
            var labelHtml = "<div class='cbrn-military-lbl'>" + 
                                "<span>" + pt.label + "</span>" + 
                                "<div class='cbrn-line-divider'></div>" + 
                                "<span class='cbrn-date-sub'>" + dateStr + "</span>" + 
                            "</div>";
                            
            marker.bindTooltip(labelHtml, { permanent: true, direction: 'bottom', offset: [0, 14], className: 'leaflet-div-icon' });
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
            var m = L.marker(e.latlng, { icon: L.icon({ iconUrl: activeIcon, iconSize: [28, 28], iconAnchor: [14, 14] }) }).addTo(map);
            // ФУНКЦІЯ ОЧИЩЕННЯ ЗНАКУ КЛІКОМ
            m.on('click', function(ev) { L.DomEvent.stopPropagation(ev); if(confirm("Видалити цей умовний знак з карти?")) map.removeLayer(m); });
        }
        if (textMode) {
            var txt = prompt("Введіть оперативно-тактичний підпис:");
            if (txt) {
                // ТЕКСТ ЗРОБЛЕНО ЧОРНИМ (cbrn-military-lbl)
                var tm = L.marker(e.latlng, {
                    icon: L.divIcon({ className: 'leaflet-div-icon', html: "<span class='cbrn-military-lbl' style='font-size:13px;'>" + txt + "</span>" })
                }).addTo(map);
                // ФУНКЦІЯ ОЧИЩЕННЯ ТЕКСТУ КЛІКОМ
                tm.on('click', function(ev) { L.DomEvent.stopPropagation(ev); if(confirm("Видалити цей текст з карти?")) map.removeLayer(tm); });
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
            // ФУНКЦІЯ ОЧИЩЕННЯ ЕЛІПСА КЛІКОМ
            poly.on('click', function(ev) { L.DomEvent.stopPropagation(ev); if(confirm("Видалити цю зону хімічного забруднення?")) map.removeLayer(poly); });
        });
    }

    document.getElementById('applyMeteoBtn').onclick = function() {
        var deg = parseFloat(document.getElementById('wDegInput').value) || 0;
        var speed = parseFloat(document.getElementById('wSpeedInput').value) || 0;
        document.getElementById('arrow').style.transform = "rotate(" + ((deg + 180) % 360) + "deg)";
        document.getElementById('degInfo').innerText = deg + "°";
        document.getElementById('speedInfo').innerText = speed + " м/с";
    };

    // Відображення радіуса кіл Geoman
    map.on('pm:create', function(e) {
        if (e.shape === 'Circle') {
            var radius = e.layer.getRadius();
            var txt = "Радіус: " + (radius >= 1000 ? (radius/1000).toFixed(2) + " км" : Math.round(radius) + " м");
            e.layer.bindTooltip(txt, { permanent: true, direction: 'center', className: 'size-tooltip' }).openTooltip();
        }
        // Очищення ліній/фігур Geoman за допомогою кліку у режимі видалення
        e.layer.on('click', function(ev) {
            if(map.pm.globalRemovalModeEnabled()) {
                map.removeLayer(e.layer);
            }
        });
    });

    // ЛОГІКА ЕКСПОРТУ КАРТИ В PNG
    document.getElementById('pngBtn').onclick = function() {
        var container = document.getElementById('mapContainer');
        // Тимчасово ховаємо інтерфейс управління лінійками для гарного знімку
        var controls = document.querySelector('.leaflet-control-container');
        controls.style.display = 'none';
        
        html2canvas(container, { useCORS: true, allowTaint: true }).then(function(canvas) {
            var link = document.createElement('a');
            link.download = 'CBRN_Map_Export.png';
            link.href = canvas.toDataURL();
            link.click();
            controls.style.display = 'block'; // Повертаємо кнопки назад
        });
    };

    // ЛОГІКА ЕКСПОРТУ КАРТИ В PDF REPORT
    document.getElementById('pdfBtn').onclick = function() {
        var container = document.getElementById('mapContainer');
        var controls = document.querySelector('.leaflet-control-container');
        controls.style.display = 'none';

        html2canvas(container, { useCORS: true, allowTaint: true }).then(function(canvas) {
            controls.style.display = 'block';
            var imgData = canvas.toDataURL('image/png');
            const { jsPDF } = window.jspdf;
            var pdf = new jsPDF('l', 'mm', 'a4'); // Альбомний формат А4
            
            pdf.setFont("Helvetica", "bold");
            pdf.setFontSize(16);
            pdf.text("CBRN SITUATION REPORT / ДОНЕСЕННЯ РХБ ОБСТАНОВКИ", 15, 15);
            pdf.setFontSize(10);
            pdf.setFont("Helvetica", "normal");
            pdf.text("Generated: " + new Date().toLocaleString(), 15, 22);
            
            // Вставляємо карту в лист PDF
            pdf.addImage(imgData, 'PNG', 15, 25, 267, 165);
            pdf.save('CBRN_Report.pdf');
        });
    };
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
    
    # Виводимо карту та нову нижню панель на екран
    components.html(final_html, height=730, scrolling=False)
