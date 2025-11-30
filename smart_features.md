# Smart Features & Geographic Clustering Plan

## 1. Smart Geographic Clustering (Requested)
**Goal**: Group people into lists based on physical proximity, with constraints on group size.

### Implementation Strategy
1.  **Data Enhancement**:
    -   Update `Persona` model to store `latitud` and `longitud`.
    -   Implement a "Geocoding Batch Process" to convert addresses to coordinates (using Google Maps API).
2.  **Clustering Algorithm (Backend)**:
    -   Input: List of people with coordinates, `max_distance` (miles), `min_size`, `max_size`.
    -   Logic:
        -   Use a spatial clustering algorithm (e.g., constrained K-Means or a greedy "seed-based" approach).
        -   Iteratively form groups that satisfy the constraints.
        -   Handle "outliers" (people too far to fit in a group).
3.  **User Interface**:
    -   **Map View**: Add a "Smart Grouping" button.
    -   **Configuration Modal**: Sliders for "Search Radius" and "Group Size".
    -   **Preview**: Show proposed clusters as colored circles on the map *before* creating lists.
    -   **Action**: "Create Lists" button that generates the actual Kanban lists from the clusters.

## 2. Additional "Intelligent" Suggestions

### A. Route Optimization (Pastoral Visits)
-   **Function**: Select a list of people (e.g., "Sick" or "New Members") and generate the optimal driving route to visit them all.
-   **Tech**: Google Maps Directions API (Waypoints optimization).
-   **Value**: Saves time for pastoral care teams.

### B. Smart Deduplication & Cleaning
-   **Function**: Scan the database for potential duplicates (similar names, same phone/email) and suggest merges.
-   **Tech**: Fuzzy string matching (Levenshtein distance).
-   **Value**: Maintains data integrity.

### C. Family Auto-Linking
-   **Function**: Detect people with the same address and last name who aren't linked as spouses/children and suggest linking them.
-   **Tech**: Pattern matching on address/name fields.
-   **Value**: Saves manual data entry effort.

### D. Natural Language Search
-   **Function**: Allow searching by phrases like "Hombres casados con hijos en el Centro" instead of using complex filters.
-   **Tech**: Simple NLP / Regex parsing to map words to filters.
-   **Value**: Makes the app more accessible to non-technical users.

## Recommended Roadmap
1.  **Phase 1**: Implement **Geographic Clustering** (Priority).
2.  **Phase 2**: Implement **Route Optimization** (High value for this domain).
3.  **Phase 3**: Implement **Smart Deduplication**.
