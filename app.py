import streamlit as st
import streamlit.components.v1 as components

# Налаштування сторінки
st.set_page_config(
    page_title="Платформа ХБРЯ - Мобільна версія 2.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Стилі для приховання стандартних відступів Streamlit, щоб карта займала весь екран
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        iframe {
            display: block;
            border: none;
            height: 100vh;
            width: 100vw;
        }
    </style>
""", unsafe_allow_html=True)

# HTML/JS код платформи
html_code = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>Платформа ХБРЯ - Мобільна версія 2.0</title>
    
    <!-- Leaflet Core -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <!-- Geoman -->
    <link rel="stylesheet" href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.css" />
    <script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.14.0/dist/leaflet-geoman.min.js"></script>

    <!-- html2canvas -->
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>

    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }
        #capture_area {
            width: 100%;
            height: 100vh;
            position: relative;
            display: flex;
            flex-direction: column;
        }
        #map {
            flex-grow: 1;
            width: 100%;
            background: #e5e3df;
        }

        .leaflet-div-icon, .cbrn-text-container {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Текстові підписи для маршрутів */
        .route-label {
            background: rgba(0, 0, 0, 0.85) !important;
            border: 1px solid #d97706 !important;
            color: #fff !important;
            font-size: 11px !important;
            font-weight: bold !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            white-space: nowrap !important;
        }

        /* --- НИЖНЯ ПАНЕЛЬ УПРАВЛІННЯ --- */
        #panel {
            background: #1a1a1a; 
            color: #fff;
            padding: 8px 12px;
            box-shadow: 0 -4px 15px rgba(0,0,0,0.5);
            border-top: 2px solid #FFD600;
            z-index: 9999;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .panel-row {
            display: flex;
            flex-wrap: nowrap;
            gap: 6px;
            align-items: center;
            width: 100%;
        }

        #panel select, #panel input {
            padding: 6px;
            border-radius: 4px;
            border: 1px solid #444;
            background: #333;
            color: #fff;
            font-size: 12px;
            height: 32px;
            box-sizing: border-box;
        }

        #symbolSelect {
            flex-grow: 2;
            min-width: 120px;
        }
        .btn-group-main {
            display: flex;
            gap: 4px;
            flex-grow: 1;
            flex-wrap: nowrap;
        }
        .btn-group-main button {
            height: 32px;
            padding: 0 8px;
            background: #444;
            color: #fff;
            border: 1px solid #555;
            cursor: pointer;
            font-size: 11px;
            font-weight: bold;
            border-radius: 4px;
            white-space: nowrap;
        }
        .btn-group-main button:hover { background: #555; }

        .btn-finish-mode {
            background: #d32f2f !important;
            border: 1px solid #b71c1c !important;
            color: #fff !important;
        }
        .btn-finish-mode:hover { background: #f44336 !important; }

        .input-container {
            display: flex;
            align-items: center;
            gap: 4px;
            background: #252525;
            padding: 0 6px;
            border-radius: 4px;
            border: 1px solid #333;
            height: 32px;
            box-sizing: border-box;
        }
        .input-container span {
            font-size: 10px;
            color: #aaa;
            font-weight: bold;
            white-space: nowrap;
        }
        .input-container input {
            width: 50px !important;
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            text-align: center;
        }

        #panel .btn-action {
            background: #FFD600;
            color: #000;
            border: none;
            font-size: 11px;
            font-weight: bold;
            height: 32px;
            padding: 0 8px;
            border-radius: 4px;
            cursor: pointer;
            white-space: nowrap;
        }
        #panel .btn-action:hover { background: #e6c000; }

        .btn-export {
            height: 32px;
            padding: 0 6px;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            font-weight: bold;
        }

        /* --- ВІДЖЕТ ВІТРУ --- */
        #windWidget {
            position: absolute;
            left: 10px;
            bottom: 130px;
            z-index: 9998;
            background: rgba(26, 26, 26, 0.9);
            color: #FFD600;
            padding: 6px;
            border-radius: 8px;
            border: 1px solid #FFD600;
            text-align: center;
            width: 75px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .wind-arrow {
            font-size: 22px;
            margin: 0;
            transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: inline-block;
        }
        .wind-deg { font-size: 11px; font-weight: bold; }
        
        .wind-speed-table {
            border-top: 1px dashed #FFD600;
            margin-top: 4px;
            padding-top: 4px;
            font-size: 10px;
            text-align: left;
        }
        .wind-speed-row {
            display: flex;
            justify-content: space-between;
        }
        .wind-speed-val { color: #fff; font-weight: bold; }

        .leaflet-top.leaflet-left { top: 10px; }

        @media print {
            #panel { display: none !important; }
            #windWidget { border: 1px solid #000; color: #000; background: white; bottom: 10px; }
            .wind-speed-val { color: #000; }
        }

        @media (max-width: 480px) {
            #panel { padding: 6px; }
            .panel-row { gap: 4px; flex-wrap: wrap; }
            #panel select, #panel input, .btn-group-main button, #panel .btn-action, .btn-export { font-size: 10px; height: 30px; }
            .input-container { height: 30px; padding: 0 3px; }
            .input-container input { width: 35px !important; }
            #windWidget { bottom: 135px; width: 70px; }
        }
    </style>
</head>
<body>

<div id="capture_area">
    <div id="map"></div>

    <div id="windWidget">
        <div class="wind-arrow" id="windArrow">↑</div>
        <div class="wind-deg" id="windDeg">0°</div>
        <div class="wind-speed-table">
            <div class="wind-speed-row"><span>м/с:</span><span class="wind-speed-val" id="speedMs">0</span></div>
            <div class="wind-speed-row"><span>км/г:</span><span class="wind-speed-val" id="speedKmh">0</span></div>
        </div>
    </div>

    <div id="panel">
        <!-- РЯДОК 1: Автомаршрут з проміжними точками через ; -->
        <div class="panel-row" style="border-bottom: 1px solid #333; padding-bottom: 4px;">
            <div class="input-container" style="flex-grow: 1;">
                <span>Маршрут:</span>
                <input id="routePoints" type="text" placeholder="Київ; Фастів; Житомир або 50.45,30.52; 50.25,28.65" style="width: 100% !important; text-align: left;">
            </div>
            <button class="btn-action" style="background:#2563eb; color:#fff;" onclick="buildAutoRoute()">🚗 Автомаршрут</button>
        </div>

        <!-- РЯДОК 2: Основні знаки та Ручний режим -->
        <div class="panel-row">
            <select id="symbolSelect">
                <option value="">-- Знак РХБЗ --</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/detect_radiation.svg">Точка радіоактивного забруднення</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/detect_chemical.svg">Точка хімічного забруднення</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/detect_biological.svg">Точка біологічного зараження</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/nuclear_blast.svg">Епіцентр ядерного вибуху</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/radioactive_site.svg">Радіаційно небезпечний об’єкт</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/chemical_hazard_site.svg">Хімічно небезпечний об’єкт</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/biological_hazard_site.svg">Біологічно небезпечний об’єкт</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/cbrn_recon_area.svg">Район РХБ розвідки</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/decon_area_special.svg">Район спецобробки</option>
                <option value="https://cdn.jsdelivr.net/gh/sergsh1125-dotcom/CBRN-PROTECTION-SUPPORT-portal@main/assets/svg/cbrn_post.svg">Пост спостереження РХБ</option>
            </select>

            <div class="btn-group-main">
                <button style="background:#d97706;" onclick="enableReconRoute()">✍️ Маршрут (ручний)</button>
                <button onclick="enableText()">Текст</button>
                <button style="background:#5c3a21;" onclick="enableEllipseMode()">Еліпс</button>
                <button class="btn-finish-mode" onclick="deactivateDrawTools()">Завершити знак</button>
                <button style="background:#8b0000;" onclick="clearAll()">Очистити</button>
            </div>
        </div>

        <!-- РЯДОК 3: Метео та Експорт -->
        <div class="panel-row">
            <div class="input-container">
                <span>Вітер°:</span>
                <input id="windInput" type="number" min="0" max="360" value="0">
            </div>

            <div class="input-container">
                <span>м/с:</span>
                <input id="windSpeedInput" type="number" min="0" max="50" step="0.1" value="0">
            </div>

            <button class="btn-action" onclick="applyWind()">Оновити Метео</button>
            
            <div style="flex-grow: 1;"></div> 
            <button class="btn-export" style="background:#2e7d32;" onclick="exportPNG()">📸 PNG</button>
            <button class="btn-export" style="background:#1565c0;" onclick="window.print()">🖨 PDF</button>
        </div>
    </div>
</div>

<script>
    let state = { objects: [], shapes: [] };
    let selectedIcon = "";
    let textMode = false;
    let ellipseMode = false;
    let isDrawingRecon = false;

    // --- ІНІЦІАЛІЗАЦІЯ КАРТИ ТА ШАРІВ ---
    let map = L.map('map', { zoomControl: true }).setView([48.3, 31.1], 6);

    let osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    let satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles © Esri'
    });

    L.control.layers({
        "Схема (OSM)": osmLayer,
        "Супутник": satelliteLayer
    }, null, { position: 'topright' }).addTo(map);

    let drawnItems = new L.FeatureGroup().addTo(map);
    let markersGroup = L.layerGroup().addTo(map);

    // --- НАЛАШТУВАННЯ GEOMAN ---
    map.pm.addControls({
        position: 'topleft',
        drawMarker: false,
        drawCircleMarker: false,
        drawPolyline: true,
        drawRectangle: false,
        drawPolygon: true,
        drawCircle: true,
        editMode: true,
        dragMode: false,
        cutPolygon: false,
        removalMode: true
    });

    map.pm.setGlobalOptions({ 
        measurements: { display: true, totalLength: true, segmentLength: true, radius: true, area: true } 
    });
    map.pm.setLang('uk');

    function saveState() { localStorage.setItem("cbrn_state", JSON.stringify(state)); }
    
    function loadState() {
        let saved = localStorage.getItem("cbrn_state");
        if (saved) {
            try {
                state = JSON.parse(saved);
                if (!state.objects) state.objects = [];
                if (!state.shapes) state.shapes = [];
            } catch(e) {
                state = { objects: [], shapes: [] };
            }
        }
    }

    function stopGeomanDraw() {
        if (map.pm.globalDrawModeEnabled()) map.pm.disableDraw();
        if (map.pm.globalEditModeEnabled()) map.pm.disableGlobalEditMode();
        if (map.pm.globalRemovalModeEnabled()) map.pm.disableGlobalRemovalMode();
    }

    function deactivateDrawTools() {
        stopGeomanDraw();
        textMode = false;
        ellipseMode = false;
        isDrawingRecon = false;
        selectedIcon = "";
        document.getElementById("symbolSelect").value = "";
    }

    // 1) РУЧНИЙ РЕЖИМ МАРШРУТУ
    function enableReconRoute() {
        deactivateDrawTools();
        isDrawingRecon = true;
        map.pm.enableDraw('Line', {
            snappable: true,
            pathOptions: { color: '#d97706', weight: 4, dashArray: '8, 8' }
        });
    }

    // 2) АВТОМАТИЧНИЙ РЕЖИМ МАРШРУТУ (Підтримка кількох точок через ;)
    async function geocodeInput(query) {
        query = query.trim();
        if (!query) return null;

        let coordMatch = query.match(/^([-+]?\d+\.?\d*)[,\s]+([-+]?\d+\.?\d*)$/);
        if (coordMatch) {
            return [parseFloat(coordMatch[1]), parseFloat(coordMatch[2])];
        }

        try {
            let response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
            let data = await response.json();
            if (data && data.length > 0) {
                return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
            }
        } catch (e) {
            console.error("Помилка геокодування:", e);
        }
        return null;
    }

    async function buildAutoRoute() {
        let rawInput = document.getElementById("routePoints").value;
        if (!rawInput.trim()) {
            alert("Введіть точки маршруту через крапку з комою (;), наприклад: Київ; Фастів; Житомир");
            return;
        }

        let parts = rawInput.split(';').map(p => p.trim()).filter(p => p.length > 0);
        if (parts.length < 2) {
            alert("Потрібно ввести мінімум 2 точки, розділені знаком ';'");
            return;
        }

        let coordinatesList = [];
        let validNames = [];

        for (let part of parts) {
            let coords = await geocodeInput(part);
            if (!coords) {
                alert(`Не вдалося знайти точку: "${part}"`);
                return;
            }
            coordinatesList.push(`${coords[1]},${coords[0]}`);
            validNames.push(part);
        }

        try {
            let coordsString = coordinatesList.join(';');
            let osrmUrl = `https://router.project-osrm.org/route/v1/driving/${coordsString}?overview=full&geometries=geojson`;
            let response = await fetch(osrmUrl);
            let data = await response.json();

            if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
                let route = data.routes[0];
                let distKm = (route.distance / 1000).toFixed(2);
                let durationMin = Math.round(route.duration / 60);

                let geojson = {
                    type: "Feature",
                    geometry: route.geometry,
                    properties: {}
                };

                let routeName = `${validNames.join(' ➔ ')} (${distKm} км, ~${durationMin} хв)`;

                let shapeData = {
                    id: Date.now(),
                    geojson: geojson,
                    isRoute: true,
                    routeName: routeName
                };

                state.shapes.push(shapeData);
                saveState();
                restoreShapes();

                let tempLayer = L.geoJSON(geojson);
                map.fitBounds(tempLayer.getBounds(), { padding: [30, 30] });

            } else {
                alert("Не вдалося прокласти автомобільний маршрут через зазначені точки!");
            }
        } catch (e) {
            alert("Помилка з'єднання з сервісом маршрутизації OSRM!");
            console.error(e);
        }
    }

    function calculatePolylineLength(latlngs) {
        let total = 0;
        for (let i = 0; i < latlngs.length - 1; i++) {
            total += latlngs[i].distanceTo(latlngs[i + 1]);
        }
        return total >= 1000 ? (total / 1000).toFixed(2) + " км" : Math.round(total) + " м";
    }

    map.on('pm:create', function(e) {
        let layer = e.layer;
        let shapeData = { id: Date.now(), geojson: layer.toGeoJSON(), isCircle: false, isEllipse: false, isRoute: false };

        if (isDrawingRecon || e.shape === 'Line') {
            shapeData.isRoute = true;
            let latlngs = layer.getLatLngs();
            let distStr = calculatePolylineLength(latlngs);
            let name = prompt("Введіть назву/номер маршруту розвідки:", "Маршрут розвідки (ручний)");
            shapeData.routeName = (name ? name : "Маршрут розвідки") + ` (${distStr})`;
            isDrawingRecon = false;
        } else if (e.shape === 'Circle') {
            shapeData.isCircle = true;
            shapeData.circleRadius = layer.getRadius();
            let latlng = layer.getLatLng();
            shapeData.circleCenter = [latlng.lat, latlng.lng];
        }

        map.removeLayer(layer);
        state.shapes.push(shapeData);
        saveState();
        restoreShapes();
    });

    function restoreShapes() {
        drawnItems.clearLayers();
        if (!state || !state.shapes || state.shapes.length === 0) return;

        let ellipses = state.shapes.filter(s => s && s.isEllipse && s.radiusX && s.radiusY);
        let otherShapes = state.shapes.filter(s => s && (!s.isEllipse || !s.radiusX || !s.radiusY));

        otherShapes.forEach((s) => {
            let layer;
            if (s.isRoute && s.geojson) {
                layer = L.geoJSON(s.geojson, {
                    style: { color: "#d97706", weight: 4, dashArray: "8, 8" }
                });
                if (s.routeName) {
                    layer.bindTooltip(s.routeName, { permanent: true, direction: 'center', className: 'route-label' });
                }
            } else if (s.isCircle && s.circleRadius) {
                let center = s.circleCenter ? s.circleCenter : [s.geojson.geometry.coordinates[1], s.geojson.geometry.coordinates[0]];
                layer = L.circle(center, { radius: s.circleRadius, color: "black", weight: 2, fillColor: "yellow", fillOpacity: 0.3 });
            } else if (s.geojson) {
                layer = L.geoJSON(s.geojson, { style: { color: "black", weight: 2, fillColor: "yellow", fillOpacity: 0.3 } });
            }

            if (layer) {
                layer.addTo(drawnItems);
                layer.on("click", function(e) {
                    if (map.pm.globalRemovalModeEnabled()) {
                        L.DomEvent.stopPropagation(e);
                        state.shapes = state.shapes.filter(shape => shape.id !== s.id);
                        saveState();
                        restoreShapes();
                    }
                });
            }
        });

        // Еліпси (AEGL)
        let groupedEllipses = {};
        ellipses.forEach(s => {
            let gId = s.groupId || s.id;
            if (!groupedEllipses[gId]) groupedEllipses[gId] = [];
            groupedEllipses[gId].push(s);
        });

        for (let gId in groupedEllipses) {
            let currentGroup = groupedEllipses[gId];
            currentGroup.sort((a, b) => b.radiusX - a.radiusX);

            currentGroup.forEach((s, index) => {
                if (!s.ellipseCenter) return;
                let points = [];
                let centerLat = s.ellipseCenter[0];
                let centerLng = s.ellipseCenter[1];
                let windRad = (s.tilt || 0) * Math.PI / 180;
                let angleRad = windRad + Math.PI; 

                for (let i = 0; i < 64; i++) {
                    let angle = (i / 64) * 2 * Math.PI;
                    let x = s.radiusY * Math.cos(angle); 
                    let y = s.radiusX * Math.sin(angle); 

                    let rotatedDx = x * Math.cos(angleRad) + (y + s.radiusX) * Math.sin(angleRad);
                    let rotatedDy = -x * Math.sin(angleRad) + (y + s.radiusX) * Math.cos(angleRad);

                    let latOffset = rotatedDy / 111320;
                    let lngOffset = rotatedDx / (111320 * Math.cos(centerLat * Math.PI / 180));

                    points.push([centerLat + latOffset, centerLng + lngOffset]);
                }

                let zoneColor = "#ffcc00"; 
                let zoneOpacity = 0.3;

                if (currentGroup.length === 2) {
                    zoneColor = (index === 0) ? "#ff9900" : "#cc0000"; 
                    zoneOpacity = (index === 0) ? 0.35 : 0.55;
                } else if (currentGroup.length >= 3) {
                    if (index === 0) { zoneColor = "#ffcc00"; zoneOpacity = 0.25; } 
                    else if (index === 1) { zoneColor = "#ff9900"; zoneOpacity = 0.45; } 
                    else { zoneColor = "#cc0000"; zoneOpacity = 0.65; }
                }

                let polygonLayer = L.polygon(points, {
                    color: zoneColor === "#cc0000" ? "#8b0000" : "black", 
                    weight: 2, fillColor: zoneColor, fillOpacity: zoneOpacity
                }).addTo(drawnItems);

                polygonLayer.on("click", function(e) {
                    L.DomEvent.stopPropagation(e);
                    if (confirm(`Видалити цю хмару забруднення AEGL?`)) {
                        state.shapes = state.shapes.filter(shape => (shape.groupId || shape.id) != gId);
                        saveState();
                        restoreShapes();
                    }
                });
            });
        }
    }

    document.getElementById("symbolSelect").onchange = function(e) {
        selectedIcon = e.target.value;
        textMode = false; 
        ellipseMode = false;
        isDrawingRecon = false;
        if (selectedIcon) stopGeomanDraw();
    };

    function enableText() { 
        textMode = true; 
        ellipseMode = false; 
        isDrawingRecon = false;
        selectedIcon = ""; 
        document.getElementById("symbolSelect").value = ""; 
        stopGeomanDraw(); 
    }
    
    function enableEllipseMode() { 
        ellipseMode = true; 
        textMode = false; 
        isDrawingRecon = false;
        selectedIcon = ""; 
        document.getElementById("symbolSelect").value = ""; 
        stopGeomanDraw(); 
    }
    
    function clearAll() {
        if(confirm("Очистити всю обстановку на карті?")) {
            state = { objects: [], shapes: [] };
            localStorage.removeItem("cbrn_state");
            drawnItems.clearLayers();
            markersGroup.clearLayers();
            location.reload();
        }
    }

    function render() {
        markersGroup.clearLayers();
        if (!state || !state.objects) return;

        state.objects.forEach((obj, index) => {
            let marker;
            if (obj.type === "text") {
                marker = L.marker([obj.lat, obj.lng], {
                    icon: L.divIcon({ 
                        className: "cbrn-text-container", 
                        html: `<span style="display: inline-block; white-space: nowrap; font-size: 13px; font-weight: bold; color: #000; text-shadow: 1px 1px 0px #fff, -1px -1px 0px #fff, 1px -1px 0px #fff, -1px 1px 0px #fff !important;">${obj.text}</span>`,
                        iconSize: null, iconAnchor: [10, 10]  
                    })
                });
            } else if (obj.type === "symbol" && obj.icon) {
                marker = L.marker([obj.lat, obj.lng], {
                    icon: L.icon({ iconUrl: obj.icon, iconSize: [28, 28], iconAnchor: [14, 14] })
                });
            }

            if (marker) {
                marker.addTo(markersGroup);
                marker.on("click", function(e) {
                    L.DomEvent.stopPropagation(e);
                    state.objects.splice(index, 1);
                    saveState();
                    render();
                });
            }
        });
    }

    map.on("click", function(e) {
        if (map.pm.globalDrawModeEnabled() || map.pm.globalRemovalModeEnabled()) return;

        if (textMode) {
            let txt = prompt("Введіть текст:");
            if (!txt) return;
            state.objects.push({ type: "text", lat: e.latlng.lat, lng: e.latlng.lng, text: txt });
            saveState();
            render();
            textMode = false;
            return;
        }

        if (ellipseMode) {
            let rX = prompt("Довжина зони AEGL (радіус X за вітром) в метрах:", "5000");
            if (!rX) return;
            let rY = prompt("Ширина зони AEGL (радіус Y) в метрах:", "2000");
            if (!rY) return;
            
            let windInputVal = document.getElementById("windInput").value;
            let angle = windInputVal !== "" ? parseFloat(windInputVal) : 0;
            let groupId = Date.now();

            state.shapes.push({ id: groupId + "_1", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: parseFloat(rX), radiusY: parseFloat(rY), tilt: angle });
            state.shapes.push({ id: groupId + "_2", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: parseFloat(rX) * 0.6, radiusY: parseFloat(rY) * 0.6, tilt: angle });
            state.shapes.push({ id: groupId + "_3", groupId: groupId, isEllipse: true, ellipseCenter: [e.latlng.lat, e.latlng.lng], radiusX: parseFloat(rX) * 0.3, radiusY: parseFloat(rY) * 0.3, tilt: angle });

            saveState();
            restoreShapes();
            ellipseMode = false;
            return;
        }

        if (selectedIcon) {
            state.objects.push({ type: "symbol", lat: e.latlng.lat, lng: e.latlng.lng, icon: selectedIcon });
            saveState();
            render();
        }
    });

    function exportPNG() {
        const area = document.getElementById("capture_area");
        document.getElementById("panel").style.display = "none";
        document.getElementById("windWidget").style.bottom = "10px";
        
        html2canvas(area, { useCORS: true, allowTaint: true, scale: 2 }).then(function(canvas) {
            const link = document.createElement("a");
            link.download = `CBRN_Mobile_SITREP_${Date.now()}.png`;
            link.href = canvas.toDataURL("image/png");
            link.click();
            document.getElementById("panel").style.display = "flex";
            document.getElementById("windWidget").style.bottom = "130px";
        });
    }

    function updateWindWidget(deg, speedMs) {
        let visualAngle = (deg + 180) % 360;
        document.getElementById("windArrow").style.transform = `rotate(${visualAngle}deg)`;
        document.getElementById("windDeg").innerText = deg + "°";
        let ms = parseFloat(speedMs) || 0;
        let kmh = Math.round(ms * 3.6 * 10) / 10;
        document.getElementById("speedMs").innerText = ms;
        document.getElementById("speedKmh").innerText = kmh;
    }

    function applyWind() {
        let degVal = document.getElementById("windInput").value;
        let speedVal = document.getElementById("windSpeedInput").value;
        let deg = degVal !== "" ? parseInt(degVal) : 0;
        deg = ((deg % 360) + 360) % 360;
        let speed = speedVal !== "" ? parseFloat(speedVal) : 0;
        if (speed < 0) speed = 0;
        updateWindWidget(deg, speed);
    }

    loadState();
    restoreShapes();
    render();
    updateWindWidget(0, 0);
</script>
</body>
</html>
"""

# Відображення картографічного інтерфейсу у Streamlit
components.html(html_code, height=800, scrolling=False)
