/**
 * Módulo de Filtros
 * Gestiona el filtrado y búsqueda de tarjetas en el tablero
 */

export class FilterManager {
    constructor(kanbanBoard) {
        this.kanbanBoard = kanbanBoard;
        this.searchInput = document.getElementById('searchInput');
        this.filterButtons = document.querySelectorAll('.filter-btn'); // Si existen botones de filtro rápido

        this.init();
    }

    init() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.filterCards(e.target.value);
            });
        }

        if (this.filterButtons) {
            this.filterButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.handleFilterClick(e);
                });
            });
        }
    }

    filterCards(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const cards = document.querySelectorAll('.person-card');

        cards.forEach(card => {
            const name = card.querySelector('.person-name').textContent.toLowerCase();
            const info = card.querySelector('.person-info').textContent.toLowerCase();
            // También podríamos buscar en tags ocultos o data attributes

            const matches = name.includes(term) || info.includes(term);

            if (matches) {
                card.style.display = '';
                card.classList.remove('filtered-out');
            } else {
                card.style.display = 'none';
                card.classList.add('filtered-out');
            }
        });

        this.updateCounters();
    }

    handleFilterClick(e) {
        // Lógica para filtros por categoría (ej. "Solo Hombres", "Con Hijos")
        const btn = e.target.closest('.filter-btn');
        const filterType = btn.dataset.filter;

        // Toggle active state
        this.filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const cards = document.querySelectorAll('.person-card');

        cards.forEach(card => {
            if (filterType === 'all') {
                card.style.display = '';
                return;
            }

            let match = false;

            if (filterType.startsWith('estado-')) {
                const estado = filterType.replace('estado-', '');
                match = card.dataset.estado === estado;
            } else if (filterType === 'hijos') {
                match = card.dataset.hijos === 'true';
            } else {
                // Fallback generic check
                match = card.dataset[filterType] === 'true' || card.dataset.category === filterType;
            }

            if (match) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });

        this.updateCounters();
    }

    updateCounters() {
        // Actualizar contadores de listas basados en tarjetas visibles
        document.querySelectorAll('.kanban-list').forEach(list => {
            const visibleCards = list.querySelectorAll('.person-card:not(.filtered-out):not([style*="display: none"])').length;
            const counter = list.querySelector('.list-count');
            if (counter) {
                counter.textContent = visibleCards;
            }
        });
    }
}
