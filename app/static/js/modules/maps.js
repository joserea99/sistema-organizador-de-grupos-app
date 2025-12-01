/**
 * Módulo de Mapas
 * Gestiona la integración con Google Maps
 */

export class MapManager {
    constructor() {
        console.log('MapManager constructor called');
        this.map = null;
        this.markers = [];
        this.markerCluster = null;

        // Escuchar evento de carga de API
        window.addEventListener('google-maps-loaded', () => {
            console.log('Event google-maps-loaded received');
            this.initMap();
        });

        // Si la API ya estaba cargada (caso raro de race condition o caché)
        if (window.googleMapsLoaded || (window.google && window.google.maps)) {
            console.log('Google Maps already loaded, initializing immediately');
            this.initMap();
        } else {
            console.log('Waiting for Google Maps API to load...');
            // Fallback si no carga en 5 segundos
            setTimeout(() => {
                if (!this.map && !window.googleMapsLoaded) {
                    console.error('Google Maps API failed to load or timed out');
                    const mapElement = document.getElementById('map');
                    if (mapElement) {
                        mapElement.innerHTML = '<div class="p-4 text-center text-error">No se pudo cargar el mapa. Verifique su conexión o la clave de API.</div>';
                    }
                }
            }, 5000);
        }
    }

    initMap() {
        console.log('initMap called');
        const mapElement = document.getElementById('map');
        if (!mapElement) {
            console.error('Map element not found!');
            return;
        }

        console.log('Creating Google Map...');
        // Coordenadas por defecto (Centro de México o configurable)
        const defaultCenter = { lat: 19.4326, lng: -99.1332 };

        this.map = new google.maps.Map(mapElement, {
            zoom: 5,
            center: defaultCenter,
            styles: this.getMapStyles(), // Estilos personalizados según el tema
            mapTypeControl: false,
            streetViewControl: false
        });

        console.log('Google Map created successfully');

        // Clusterer desactivado por solicitud del usuario
        this.markerCluster = null;

        this.loadMarkers();
        this.initFilters();
    }

    getMapStyles() {
        return [
            {
                "featureType": "poi",
                "elementType": "all",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "transit",
                "elementType": "all",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "road",
                "elementType": "labels.icon",
                "stylers": [
                    { "visibility": "off" }
                ]
            },
            {
                "featureType": "landscape",
                "elementType": "geometry",
                "stylers": [
                    { "color": "#f5f5f5" }
                ]
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [
                    { "color": "#c9ecfc" }
                ]
            }
        ];
    }

    loadMarkers() {
        // Obtener todas las tarjetas que tienen dirección
        const cards = document.querySelectorAll('.person-card');
        const geocoder = new google.maps.Geocoder();

        // Limpiar marcadores existentes
        this.clearMarkers();

        console.log(`Found ${cards.length} cards for map`);
        cards.forEach(card => {
            const personData = {
                id: card.dataset.id,
                name: card.querySelector('.person-name')?.textContent,
                address: card.querySelector('.detail-value')?.textContent, // Asumiendo que es el primer detalle
                phone: card.dataset.phone,
                email: card.dataset.email,
                color: card.dataset.color || '#3b82f6',
                listId: card.dataset.listId,
                listName: card.dataset.listName,
                initials: card.querySelector('.person-avatar')?.textContent?.trim() || '??',
                conyuge: card.dataset.conyuge,
                edadConyuge: card.dataset.edadConyuge,
                codigoPostal: card.dataset.codigoPostal,
                estado: card.dataset.estado, // Para filtrado
                hijos: card.dataset.hijos    // Para filtrado
            };

            const lat = parseFloat(card.dataset.lat);
            const lng = parseFloat(card.dataset.lng);

            if (!isNaN(lat) && !isNaN(lng)) {
                console.log(`Adding marker from coords: ${lat}, ${lng}`);
                // Usar coordenadas existentes
                this.addMarker({ lat, lng }, personData);
            } else if (personData.address && personData.address.trim()) {
                console.log(`Geocoding address: ${personData.address}`);
                // Geocodificar si no hay coordenadas
                this.geocodeAndAddMarker(geocoder, personData.address, personData);
            }
        });

        // Ajustar vista para mostrar todos los marcadores
        console.log(`Total markers: ${this.markers.length}`);
        if (this.markers.length > 0) {
            const bounds = new google.maps.LatLngBounds();
            this.markers.forEach(marker => bounds.extend(marker.getPosition()));
            this.map.fitBounds(bounds);
            console.log('Map bounds fitted');
        }
    }

    addMarker(position, personData) {
        // Crear icono SVG personalizado con el color de la lista
        const svgMarker = {
            path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
            fillColor: personData.color,
            fillOpacity: 1,
            strokeWeight: 1,
            strokeColor: "#FFFFFF",
            rotation: 0,
            scale: 2,
            anchor: new google.maps.Point(12, 22),
        };

        const marker = new google.maps.Marker({
            position: position,
            title: personData.name,
            icon: svgMarker,
            animation: google.maps.Animation.DROP
        });

        // Contenido enriquecido del InfoWindow
        const contentString = `
            <div class="map-info-window" style="min-width: 250px; padding: 5px;">
                <div style="display: flex; align-items: center; margin-bottom: 10px; border-bottom: 2px solid ${personData.color}; padding-bottom: 8px;">
                    <div style="background-color: ${personData.color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                        ${personData.initials}
                    </div>
                    <div>
                        <h3 style="margin: 0; font-size: 16px; font-weight: bold;">${personData.name}</h3>
                        <span style="font-size: 12px; color: #666; background-color: ${personData.color}20; padding: 2px 6px; border-radius: 4px;">
                            ${personData.listName}
                        </span>
                    </div>
                </div>
                
                <div style="margin-bottom: 12px; font-size: 13px;">
                    <div style="margin-bottom: 4px;"><i class="fas fa-map-marker-alt" style="width: 16px; color: #666;"></i> ${personData.address}</div>
                    ${personData.phone ? `<div style="margin-bottom: 4px;"><i class="fas fa-phone" style="width: 16px; color: #666;"></i> ${personData.phone}</div>` : ''}
                    ${personData.email ? `<div style="margin-bottom: 4px;"><i class="fas fa-envelope" style="width: 16px; color: #666;"></i> ${personData.email}</div>` : ''}
                    
                    ${personData.conyuge ? `
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #eee;">
                        <div style="font-weight: 600; margin-bottom: 2px;">Cónyuge:</div>
                        <div><i class="fas fa-user-friends" style="width: 16px; color: #666;"></i> ${personData.conyuge} ${personData.edadConyuge ? `(${personData.edadConyuge} años)` : ''}</div>
                    </div>
                    ` : ''}
                </div>

                <button onclick="window.scrollToCard('${personData.listId}', '${personData.id}')" 
                        style="width: 100%; background-color: ${personData.color}; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; font-weight: 500; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-list-ul" style="margin-right: 6px;"></i> Ver en Lista
                </button>
            </div>
        `;

        const infoWindow = new google.maps.InfoWindow({
            content: contentString
        });

        marker.addListener('click', () => {
            infoWindow.open(this.map, marker);
        });

        this.markers.push(marker);
        marker.setMap(this.map);

        // Agregar al clusterer si existe
        if (this.markerCluster) {
            this.markerCluster.addMarker(marker);
        }

        // Store data for filtering (CRITICAL FIX)
        marker.personData = personData;
    }

    clearMarkers() {
        if (this.markerCluster) {
            this.markerCluster.clearMarkers();
        }
        this.markers.forEach(m => m.setMap(null));
        this.markers = [];
    }

    geocodeAndAddMarker(geocoder, address, personData) {
        geocoder.geocode({ 'address': address }, (results, status) => {
            if (status === 'OK') {
                // Crear icono SVG personalizado con el color de la lista
                const svgMarker = {
                    path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
                    fillColor: personData.color,
                    fillOpacity: 1,
                    strokeWeight: 1,
                    strokeColor: "#FFFFFF",
                    rotation: 0,
                    scale: 2,
                    anchor: new google.maps.Point(12, 22),
                };

                const marker = new google.maps.Marker({
                    position: results[0].geometry.location,
                    title: personData.name,
                    icon: svgMarker,
                    animation: google.maps.Animation.DROP
                });

                // Contenido enriquecido del InfoWindow
                const contentString = `
                    <div class="map-info-window" style="min-width: 250px; padding: 5px;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px; border-bottom: 2px solid ${personData.color}; padding-bottom: 8px;">
                            <div style="background-color: ${personData.color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px;">
                                ${personData.initials}
                            </div>
                            <div>
                                <h3 style="margin: 0; font-size: 16px; font-weight: bold;">${personData.name}</h3>
                                <span style="font-size: 12px; color: #666; background-color: ${personData.color}20; padding: 2px 6px; border-radius: 4px;">
                                    ${personData.listName}
                                </span>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 12px; font-size: 13px;">
                            <div style="margin-bottom: 4px;"><i class="fas fa-map-marker-alt" style="width: 16px; color: #666;"></i> ${personData.address}</div>
                            ${personData.codigoPostal ? `<div style="margin-bottom: 4px;"><i class="fas fa-mail-bulk" style="width: 16px; color: #666;"></i> CP: ${personData.codigoPostal}</div>` : ''}
                            ${personData.phone ? `<div style="margin-bottom: 4px;"><i class="fas fa-phone" style="width: 16px; color: #666;"></i> ${personData.phone}</div>` : ''}
                            ${personData.email ? `<div style="margin-bottom: 4px;"><i class="fas fa-envelope" style="width: 16px; color: #666;"></i> ${personData.email}</div>` : ''}
                            
                            ${personData.conyuge ? `
                            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #eee;">
                                <div style="font-weight: 600; margin-bottom: 2px;">Cónyuge:</div>
                                <div><i class="fas fa-user-friends" style="width: 16px; color: #666;"></i> ${personData.conyuge} ${personData.edadConyuge ? `(${personData.edadConyuge} años)` : ''}</div>
                            </div>
                            ` : ''}
                        </div>

                        <button onclick="window.scrollToCard('${personData.listId}', '${personData.id}')" 
                                style="width: 100%; background-color: ${personData.color}; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; font-weight: 500; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-list-ul" style="margin-right: 6px;"></i> Ver en Lista
                        </button>
                    </div>
                `;

                const infoWindow = new google.maps.InfoWindow({
                    content: contentString
                });

                marker.addListener('click', () => {
                    // Cerrar otros infoWindows si es necesario (opcional)
                    infoWindow.open(this.map, marker);
                });

                this.markers.push(marker);
                marker.setMap(this.map);

                // Store data for filtering
                marker.personData = personData;
            }
        });
    }

    filterMarkers(filter) {
        console.log('Filtering map markers by:', filter);
        this.markers.forEach(marker => {
            if (!marker.personData) return;

            let isVisible = false;

            if (filter === 'all') {
                isVisible = true;
            } else if (filter === 'estado-casado') {
                isVisible = marker.personData.estado === 'casado';
            } else if (filter === 'estado-soltero') {
                isVisible = marker.personData.estado === 'soltero';
            } else if (filter === 'hijos') {
                // Debug log for children filter
                // console.log(`Checking children for ${marker.personData.name}: ${marker.personData.hijos}`);
                const tieneHijos = marker.personData.hijos;
                isVisible = tieneHijos === 'true' || tieneHijos === 'True' || tieneHijos === true;
            }

            marker.setVisible(isVisible);
        });

        // Re-cluster if clustering is enabled (optional, if using clusterer)
        if (this.markerCluster) {
            this.markerCluster.repaint();
        }
    }

    centerMap() {
        if (this.markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        this.markers.forEach(marker => {
            bounds.extend(marker.getPosition());
        });
        this.map.fitBounds(bounds);
    }

    initFilters() {
        const buttons = document.querySelectorAll('.map-filter-btn');
        buttons.forEach(btn => {
            // Skip buttons that are not filters (like center or cluster)
            if (!btn.dataset.filter) return;

            btn.addEventListener('click', (e) => {
                buttons.forEach(b => {
                    if (b.dataset.filter) b.classList.remove('active');
                });
                e.currentTarget.classList.add('active');

                const filter = e.currentTarget.dataset.filter;
                this.filterMarkers(filter);
            });
        });

        // Botón Centrar
        const btnCenter = document.getElementById('btnCenterMap');
        if (btnCenter) {
            btnCenter.addEventListener('click', () => {
                this.centerMap();
            });
        }

        // Botón Smart Cluster
        const btnSmartCluster = document.getElementById('btnSmartCluster');
        const modalSmartCluster = document.getElementById('modalSmartCluster');

        if (btnSmartCluster && modalSmartCluster) {
            btnSmartCluster.addEventListener('click', () => {
                modalSmartCluster.classList.add('active');
            });

            // Cerrar modal
            modalSmartCluster.querySelector('.modal-close').addEventListener('click', () => {
                modalSmartCluster.classList.remove('active');
            });

            // Sliders
            const radiusInput = document.getElementById('clusterRadius');
            const radiusValue = document.getElementById('radiusValue');
            if (radiusInput) {
                radiusInput.addEventListener('input', (e) => {
                    radiusValue.textContent = e.target.value + ' mi';
                });
            }

            // Botones de acción
            document.getElementById('btnGeocodeBatch').addEventListener('click', () => this.batchGeocode());
            document.getElementById('btnPreviewClusters').addEventListener('click', () => this.previewClusters());
            document.getElementById('btnApplyClusters').addEventListener('click', () => this.applyClusters());
        }
    }

    async batchGeocode() {
        const btn = document.getElementById('btnGeocodeBatch');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Iniciando...';
        btn.disabled = true;

        try {
            // Obtener ID del tablero de la URL de forma robusta
            const pathParts = window.location.pathname.split('/');
            let tableroId = pathParts.pop();
            if (!tableroId) tableroId = pathParts.pop(); // Manejar trailing slash

            console.log('Starting batch geocode for tablero:', tableroId);

            if (!tableroId) {
                throw new Error('No se pudo identificar el tablero');
            }

            // 1. Obtener personas que necesitan geocodificación
            console.log('Fetching uncoded people...');
            const response = await fetch('/tableros/api/geocoding/get_uncoded', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tablero_id: tableroId })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (!data.success || data.count === 0) {
                console.log('No uncoded people found or error:', data);
                alert('No hay direcciones nuevas para procesar.');
                btn.innerHTML = originalText;
                btn.disabled = false;
                return;
            }

            const total = data.count;
            let processed = 0;
            let successCount = 0;
            const geocoder = new google.maps.Geocoder();

            btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>0/${total}`;

            // 2. Procesar cada persona (secuencialmente para no saturar API)
            for (const persona of data.personas) {
                try {
                    const result = await this.geocodeAddress(geocoder, persona.direccion);
                    if (result) {
                        // 3. Guardar coordenadas
                        await fetch('/tableros/api/personas/update_coords', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                tablero_id: tableroId,
                                persona_id: persona.id,
                                lat: result.lat,
                                lng: result.lng
                            })
                        });
                        successCount++;
                    }
                } catch (err) {
                    console.error(`Error geocoding ${persona.nombre}:`, err);
                }

                processed++;
                btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${processed}/${total}`;

                // Pequeña pausa para respetar rate limits
                await new Promise(r => setTimeout(r, 300));
            }

            alert(`Proceso completado. Se actualizaron ${successCount} de ${total} personas.`);
            this.loadMarkers();

        } catch (error) {
            console.error('Error batch geocoding:', error);
            alert('Error de conexión al iniciar el proceso.');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }

    geocodeAddress(geocoder, address) {
        return new Promise((resolve, reject) => {
            geocoder.geocode({ 'address': address }, (results, status) => {
                if (status === 'OK' && results[0]) {
                    resolve({
                        lat: results[0].geometry.location.lat(),
                        lng: results[0].geometry.location.lng()
                    });
                } else {
                    console.warn(`Geocode failed for ${address}: ${status}`);
                    resolve(null); // No fallar todo el proceso, solo retornar null
                }
            });
        });
    }

    async previewClusters() {
        const btn = document.getElementById('btnPreviewClusters');
        const previewDiv = document.getElementById('clusterPreview');
        const previewText = document.getElementById('previewText');
        const btnApply = document.getElementById('btnApplyClusters');

        btn.disabled = true;
        previewDiv.classList.remove('hidden');
        previewText.textContent = 'Calculando clusters...';

        try {
            const tableroId = window.location.pathname.split('/').pop();
            const maxDistance = document.getElementById('clusterRadius').value;
            const minSize = document.getElementById('clusterMin').value;
            const maxSize = document.getElementById('clusterMax').value;

            const response = await fetch('/tableros/api/clustering/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tablero_id: tableroId,
                    max_distance: maxDistance,
                    min_size: minSize,
                    max_size: maxSize
                })
            });

            const data = await response.json();
            if (data.success) {
                this.currentClusters = data.clusters;
                previewText.innerHTML = `
                    <strong>Se encontraron ${data.clusters.length} grupos posibles.</strong><br>
                    Total personas agrupadas: ${data.total_clustered}<br>
                    <small>Los grupos se muestran como círculos en el mapa.</small>
                `;
                btnApply.classList.remove('hidden');

                // Dibujar en mapa
                this.drawClusterPreview(data.clusters);

                // No cerrar el modal automáticamente para que el usuario pueda dar click en "Crear Listas"
                // document.getElementById('modalSmartCluster').classList.remove('active');
            } else {
                previewText.textContent = 'Error: ' + (data.message || data.error);
            }
        } catch (error) {
            console.error('Error previewing:', error);
            previewText.textContent = 'Error de conexión';
        } finally {
            btn.disabled = false;
        }
    }

    drawClusterPreview(clusters) {
        // Limpiar previews anteriores
        if (this.previewCircles) {
            this.previewCircles.forEach(c => c.setMap(null));
        }
        this.previewCircles = [];

        clusters.forEach((cluster, index) => {
            if (cluster.is_outlier) return;

            const color = '#10b981'; // Verde

            // Dibujar círculo
            const circle = new google.maps.Circle({
                strokeColor: color,
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: color,
                fillOpacity: 0.35,
                map: this.map,
                center: cluster.center,
                radius: 1609.34 * 0.5 // Radio visual aproximado (0.5 millas en metros)
            });

            this.previewCircles.push(circle);

            // Info window para el cluster
            const infoWindow = new google.maps.InfoWindow({
                content: `<div style="color: #000000; font-weight: bold;">Grupo Propuesto ${index + 1}<br><span style="font-weight: normal;">${cluster.count} personas</span></div>`,
                position: cluster.center
            });
            infoWindow.open(this.map);
        });
    }

    async applyClusters() {
        console.log('applyClusters called');

        if (!this.currentClusters || this.currentClusters.length === 0) {
            this.showStatus('No hay grupos para crear.', 'error');
            return;
        }

        // Removed confirm dialog to avoid popup issues
        // if (!confirm('¿Estás seguro?...')) return;

        const btn = document.getElementById('btnApplyClusters');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Creando...';
        this.showStatus('Creando listas...', 'info');

        try {
            const tableroId = window.location.pathname.split('/').pop();
            console.log('Sending apply request for tablero:', tableroId);

            const response = await fetch('/tableros/api/clustering/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tablero_id: tableroId,
                    clusters: this.currentClusters
                })
            });

            const data = await response.json();
            if (data.success) {
                this.showStatus(data.message, 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showStatus('Error: ' + data.error, 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check mr-2"></i>Crear Listas';
            }
        } catch (error) {
            console.error('Error applying:', error);
            this.showStatus('Error de conexión', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check mr-2"></i>Crear Listas';
        }
    }

    showStatus(message, type) {
        let statusDiv = document.getElementById('clusterStatus');
        if (!statusDiv) {
            const modalBody = document.querySelector('#modalSmartCluster .modal-body');
            statusDiv = document.createElement('div');
            statusDiv.id = 'clusterStatus';
            statusDiv.className = 'mt-4 p-3 rounded text-sm';
            modalBody.appendChild(statusDiv);
        }

        statusDiv.className = `mt-4 p-3 rounded text-sm ${type === 'error' ? 'bg-red-100 text-red-700' : type === 'success' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`;
        statusDiv.textContent = message;
    }
    highlightMarker(cardId) {
        const marker = this.markers.find(m => m.personData.id === cardId);
        if (marker) {
            // Centrar mapa en el marcador
            this.map.panTo(marker.getPosition());
            this.map.setZoom(15); // Acercar un poco

            // Animación de rebote
            marker.setAnimation(google.maps.Animation.BOUNCE);
            setTimeout(() => {
                marker.setAnimation(null);
            }, 1500);

            // Abrir InfoWindow
            google.maps.event.trigger(marker, 'click');
        } else {
            console.warn('Marker not found for card:', cardId);
        }
    }
}

// Función global para scroll
window.scrollToCard = function (listId, cardId) {
    const listElement = document.querySelector(`.kanban-list[data-list-id="${listId}"]`);
    const cardElement = document.querySelector(`.person-card[data-id="${cardId}"]`);

    if (listElement && cardElement) {
        // Scroll horizontal al contenedor de listas
        listElement.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });

        // Scroll vertical dentro de la lista
        cardElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Resaltar tarjeta temporalmente
        cardElement.style.transition = 'all 0.5s';
        const originalTransform = cardElement.style.transform;
        const originalBoxShadow = cardElement.style.boxShadow;

        cardElement.style.transform = 'scale(1.05)';
        cardElement.style.boxShadow = '0 0 15px rgba(59, 130, 246, 0.5)';

        setTimeout(() => {
            cardElement.style.transform = originalTransform;
            cardElement.style.boxShadow = originalBoxShadow;
        }, 1500);
    } else {
        console.warn('List or card not found:', listId, cardId);
    }
};

// Expose highlight function globally
window.highlightMapMarker = function (cardId) {
    if (window.mapManager) {
        window.mapManager.highlightMarker(cardId);
    }
};
