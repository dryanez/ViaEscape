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

        if (data.safe) {
            title.textContent = "Zona Segura";
            title.className = "status-safe";
            message.textContent = data.message;
        } else {
            title.textContent = "¡PELIGRO!";
            title.className = "status-danger";
            message.textContent = data.message;
        }

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

        // User Marker
        L.marker([userLat, userLon]).addTo(map)
            .bindPopup("Estás aquí")
            .openPopup();

        // Show route info if available (even if safe, user might want to know)
        if (data.nearest_route) {
            routeInfo.classList.remove('hidden');
            document.getElementById('route-dist').textContent = data.nearest_route.distance_meters;
            document.getElementById('route-name').textContent = data.nearest_route.name;

            // Draw Route Geometry
            if (data.nearest_route.geometry) {
                const routeLayer = L.geoJSON(data.nearest_route.geometry, {
                    style: { color: 'green', weight: 5 }
                }).addTo(map);

                // Fit bounds to show both user and route
                const group = new L.featureGroup([L.marker([userLat, userLon]), routeLayer]);
                try {
                    map.fitBounds(group.getBounds(), { padding: [50, 50] });
                } catch (e) { console.warn("Could not fit bounds", e); }
            }

            // If strictly safe but close to a route, maybe show warning?
            if (data.safe && data.nearest_route.distance_meters < 500) {
                title.textContent = "Precaución";
                title.className = "status-warning";
                message.textContent = "Estás cerca de una vía de evacuación.";
            }

            // Google Maps Button
            if (data.nearest_route.destination) {
                const existingBtn = document.getElementById('gmaps-btn');
                if (existingBtn) existingBtn.remove();

                const btn = document.createElement('a');
                btn.id = 'gmaps-btn';
                btn.className = 'btn google-maps-btn';
                // URL scheme for navigation
                btn.href = `https://www.google.com/maps/dir/?api=1&destination=${data.nearest_route.destination.lat},${data.nearest_route.destination.lon}&travelmode=walking`;
                btn.target = '_blank';
                btn.textContent = '📍 Ir con Google Maps';

                routeInfo.appendChild(btn);
            }
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
