document.addEventListener('DOMContentLoaded', () => {
    const checkBtn = document.getElementById('check-btn');
    const retryBtn = document.getElementById('retry-btn');
    const initialView = document.getElementById('initial-view');
    const loadingView = document.getElementById('loading-view');
    const resultView = document.getElementById('result-view');
    const loadingText = document.getElementById('loading-text');

    let map = null;
    let userLat, userLon;

    checkBtn.addEventListener('click', startCheck);
    retryBtn.addEventListener('click', resetView);

    function startCheck() {
        initialView.classList.add('hidden');
        loadingView.classList.remove('hidden');
        loadingText.textContent = "Obteniendo ubicación...";

        if (!navigator.geolocation) {
            showError("Tu navegador no soporta geolocalización.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                userLat = latitude;
                userLon = longitude;
                checkHazard(latitude, longitude);
            },
            error => {
                console.error(error);
                showError("No pudimos obtener tu ubicación. Asegúrate de dar permisos.");
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }

    async function checkHazard(lat, lon) {
        loadingText.textContent = "Analizando riesgos...";

        try {
            const response = await fetch('/api/check-hazard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lon })
            });

            if (!response.ok) throw new Error("Error en el servidor");

            const data = await response.json();
            showResult(data);
        } catch (error) {
            console.error(error);
            showError("Hubo un problema al conectar con el servidor.");
        }
    }

    function showResult(data) {
        loadingView.classList.add('hidden');
        resultView.classList.remove('hidden');

        const title = document.getElementById('status-title');
        const message = document.getElementById('status-message');
        const routeInfo = document.getElementById('route-info');

        routeInfo.classList.add('hidden');

        // Update Title & Message
        if (data.safe) {
            title.textContent = "Fuera de Zona de Peligro";
            title.className = "status-safe";
        } else {
            title.textContent = "¡PELIGRO DE TSUNAMI!";
            title.className = "status-danger";
        }
        message.textContent = data.message;

        // Initialize Map
        if (!map) {
            map = L.map('map').setView([userLat, userLon], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
        } else {
            map.invalidateSize();
            map.setView([userLat, userLon], 15);
            // Clear previous layers
            map.eachLayer((layer) => {
                if (layer instanceof L.Marker || layer instanceof L.Polyline || layer instanceof L.GeoJSON) {
                    map.removeLayer(layer);
                }
            });
        }

        // Feature Group for Bounds
        const boundsGroup = new L.featureGroup();

        // User Marker (Blue)
        const userMarker = L.marker([userLat, userLon]).addTo(map)
            .bindPopup("Tu Ubicación").openPopup();
        boundsGroup.addLayer(userMarker);

        // Handle Meeting Point (Green Marker)
        let destination = null;
        if (data.nearest_meeting_point) {
            routeInfo.classList.remove('hidden');
            document.getElementById('route-dist').textContent = data.nearest_meeting_point.distance_meters;
            document.getElementById('route-name').textContent = data.nearest_meeting_point.name;

            const mp = data.nearest_meeting_point;
            destination = mp.destination;

            // Green Icon for Safety Zone
            const greenIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });

            const mpLayer = L.geoJSON(mp.geometry, {
                pointToLayer: function (feature, latlng) {
                    return L.marker(latlng, { icon: greenIcon });
                }
            }).addTo(map).bindPopup("Punto de Encuentro Seguro");

            boundsGroup.addLayer(mpLayer);
        }

        // Handle Route (Line)
        if (data.nearest_route && data.nearest_route.geometry) {
            const routeLayer = L.geoJSON(data.nearest_route.geometry, {
                style: { color: 'blue', weight: 4, dashArray: '10, 10', opacity: 0.6 }
            }).addTo(map);
            boundsGroup.addLayer(routeLayer);

            // Fallback destination if no meeting point
            if (!destination) destination = data.nearest_route.destination;
        }

        // Fit Map Bounds
        try {
            map.fitBounds(boundsGroup.getBounds(), { padding: [50, 50] });
        } catch (e) { console.warn("Could not fit bounds", e); }

        // Google Maps Button
        const existingBtn = document.getElementById('gmaps-btn');
        if (existingBtn) existingBtn.remove();

        if (destination) {
            const btn = document.createElement('a');
            btn.id = 'gmaps-btn';
            btn.className = 'btn google-maps-btn';
            btn.href = `https://www.google.com/maps/dir/?api=1&destination=${destination.lat},${destination.lon}&travelmode=walking`;
            btn.target = '_blank';
            btn.textContent = '📍 Ir a Zona Segura (Google Maps)';
            routeInfo.appendChild(btn);
        }

        // Fix map rendering issues when unhidden
        setTimeout(() => { map.invalidateSize(); }, 200);
    }

    function showError(msg) {
        loadingView.classList.add('hidden');
        resultView.classList.remove('hidden');
        document.getElementById('status-title').textContent = "Error";
        document.getElementById('status-title').className = "status-danger";
        document.getElementById('status-message').textContent = msg;
        document.getElementById('route-info').classList.add('hidden');
    }

    function resetView() {
        resultView.classList.add('hidden');
        initialView.classList.remove('hidden');
    }
});
