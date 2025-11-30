# Smart Geographic Clustering Implementation Plan

## Goal Description
Implement a "Smart Geographic Clustering" feature that groups people into Kanban lists based on their physical proximity. This involves geocoding addresses, calculating distances, and automatically creating lists and moving cards.

## User Review Required
> [!IMPORTANT]
> **Geocoding Strategy Change**: Due to Google Maps API key restrictions (referer-based), geocoding has been moved to the **client-side (browser)**. This ensures the API key works correctly without server-side "REQUEST_DENIED" errors.

## Proposed Changes

### Backend (`app/`)
#### [MODIFY] [routes.py](file:///Users/joserea/tu_proyecto_LIMPIO/app/tableros/routes.py)
- Added `/api/geocoding/get_uncoded` to retrieve people needing coordinates.
- Added `/api/personas/update_coords` to save coordinates from the frontend.
- Added `/api/clustering/preview` to calculate clusters based on existing coordinates.
- Added `/api/clustering/apply` to create lists and move people.

#### [NEW] [clustering.py](file:///Users/joserea/tu_proyecto_LIMPIO/app/utils/clustering.py)
- `ClusteringManager` class.
- `create_clusters`: Greedy spatial clustering algorithm.
- `calculate_distance`: Haversine formula.

#### [MODIFY] [models.py](file:///Users/joserea/tu_proyecto_LIMPIO/app/models.py)
- Updated `Tarjeta` to include `latitud` and `longitud`.
- Updated serialization/deserialization to handle these new fields.

### Frontend (`app/static/js/`)
#### [MODIFY] [maps.js](file:///Users/joserea/tu_proyecto_LIMPIO/app/static/js/modules/maps.js)
- Implemented `batchGeocode` using the browser's `google.maps.Geocoder`.
- Implemented `previewClusters` to visualize groups on the map.
- Implemented `applyClusters` to trigger list creation.
- Added UI feedback (status messages) and removed blocking `confirm` dialogs.

#### [MODIFY] [ver.html](file:///Users/joserea/tu_proyecto_LIMPIO/app/templates/tableros/ver.html)
- Added "Smart Clustering" button (Magic Wand).
- Added `modalSmartCluster` for configuration (radius, group size).

## Verification Plan

### Automated Tests
- **Geocoding**: Verified via browser subagent adding a person with an address and clicking "Actualizar Coordenadas".
- **Clustering**: Verified via browser subagent clicking "Ver Vista Previa" and checking for cluster markers.
- **List Creation**: Verified via browser subagent clicking "Crear Listas" and confirming new lists appear on the board.

### Manual Verification
- User confirmed "Vista Previa" works.
- User reported issues with "Crear Listas" which were resolved by removing the confirm dialog and adding better feedback.
