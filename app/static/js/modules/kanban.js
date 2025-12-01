/**
 * Módulo Kanban
 * Gestiona la funcionalidad del tablero, drag & drop y tarjetas
 */

export class KanbanBoard {
    constructor() {
        console.log('KanbanBoard constructor called');
        this.lists = document.querySelectorAll('.kanban-list-items');
        this.boardContainer = document.querySelector('.kanban-lists-container');

        // Inicializar tableroId
        if (window.appConfig && window.appConfig.tableroId) {
            this.tableroId = window.appConfig.tableroId;
        } else {
            const boardEl = document.querySelector('.kanban-board');
            if (boardEl) {
                this.tableroId = boardEl.dataset.tableroId;
            }
        }
        console.log('Tablero ID:', this.tableroId);

        console.log(`Found ${this.lists.length} kanban lists`);
        this.isDragging = false;
        this.initSortable();
        this.initListSortable(); // Nueva función para ordenar listas
        this.initCreateList();
        this.initCreatePerson(); // Inicializar creación de personas
        this.initListEditing(); // Inicializar edición de listas
        this.initPersonSearch();
        this.initCardInteractions();
        console.log('KanbanBoard initialized');
    }

    initPersonSearch() {
        const input = document.getElementById('buscarPersonaInput');
        const resultsDiv = document.getElementById('resultadosBusqueda');
        const form = document.getElementById('formNuevaPersona');

        if (!input || !resultsDiv || !form) return;

        let debounceTimer;

        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();

            clearTimeout(debounceTimer);

            if (query.length < 2) {
                resultsDiv.classList.add('hidden');
                resultsDiv.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`/tableros/api/buscar_personas?q=${encodeURIComponent(query)}`);
                    const personas = await response.json();

                    resultsDiv.innerHTML = '';

                    if (personas.length > 0) {
                        personas.forEach(p => {
                            const div = document.createElement('div');
                            div.className = 'p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0';
                            div.innerHTML = `
                                <div class="font-bold text-sm">${p.nombre} ${p.apellido || ''}</div>
                                <div class="text-xs text-gray-500">${p.email || 'Sin email'} • ${p.telefono || 'Sin teléfono'}</div>
                            `;
                            div.addEventListener('click', () => {
                                // Rellenar formulario
                                form.querySelector('[name="nombre"]').value = p.nombre || '';
                                form.querySelector('[name="apellido"]').value = p.apellido || '';
                                form.querySelector('[name="email"]').value = p.email || '';
                                form.querySelector('[name="telefono"]').value = p.telefono || '';
                                form.querySelector('[name="direccion"]').value = p.direccion || '';

                                if (p.fecha_nacimiento) {
                                    form.querySelector('[name="fecha_nacimiento"]').value = p.fecha_nacimiento;
                                }

                                // Estado civil y cónyuge
                                const estadoSelect = form.querySelector('[name="estado_civil"]');
                                if (estadoSelect) {
                                    estadoSelect.value = p.estado_civil || 'Soltero';
                                    // Disparar evento change para mostrar campos de cónyuge si es necesario
                                    const event = new Event('change');
                                    estadoSelect.dispatchEvent(event);

                                    // Llamar manualmente a toggleSpouseFields si existe en el scope global
                                    if (typeof window.toggleSpouseFields === 'function') {
                                        window.toggleSpouseFields(p.estado_civil);
                                    }
                                }

                                if (p.nombre_conyuge) form.querySelector('[name="nombre_conyuge"]').value = p.nombre_conyuge;
                                if (p.numero_hijos) form.querySelector('[name="numero_hijos"]').value = p.numero_hijos;

                                // Checkboxes
                                if (p.bautizado) form.querySelector('[name="bautizado"]').checked = true;
                                if (p.es_lider) form.querySelector('[name="es_lider"]').checked = true;
                                if (p.ministerio) form.querySelector('[name="ministerio"]').value = p.ministerio;

                                // Ocultar resultados y limpiar buscador
                                resultsDiv.classList.add('hidden');
                                input.value = '';

                                // Visual feedback
                                input.placeholder = `Datos de ${p.nombre} cargados`;
                                input.classList.add('bg-green-50');
                                setTimeout(() => input.classList.remove('bg-green-50'), 1000);
                            });
                            resultsDiv.appendChild(div);
                        });
                        resultsDiv.classList.remove('hidden');
                    } else {
                        resultsDiv.innerHTML = '<div class="p-3 text-sm text-gray-500">No se encontraron personas</div>';
                        resultsDiv.classList.remove('hidden');
                    }
                } catch (error) {
                    console.error('Error buscando personas:', error);
                }
            }, 300);
        });

        // Cerrar resultados al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.classList.add('hidden');
            }
        });
    }

    initCreateList() {
        const form = document.getElementById('formNuevaLista');
        if (form) {
            form.addEventListener('submit', (e) => this.handleCreateList(e));
        }
    }

    async handleCreateList(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        console.log('Attempting to create list...');
        console.log('Tablero ID:', this.tableroId);

        if (!this.tableroId) {
            alert('Error interno: ID del tablero no encontrado. Por favor recarga la página.');
            return;
        }

        try {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creando...';

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.tablero_id = this.tableroId;

            console.log('Sending data:', data);

            const response = await fetch('/tableros/agregar_lista', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Response data:', result);

            if (response.ok) {
                console.log('List created successfully, reloading...');
                window.location.reload();
            } else {
                console.error('Server error:', result.error);
                alert('Error: ' + (result.error || 'Error desconocido'));
                // Reset overflow in case modal gets stuck
                document.body.style.overflow = '';
            }
        } catch (error) {
            console.error('Network/JS error creating list:', error);
            alert('Error de conexión al crear la lista');
            document.body.style.overflow = '';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    initCreatePerson() {
        const form = document.getElementById('formNuevaPersona');
        if (form) {
            form.addEventListener('submit', (e) => this.handleCreatePerson(e));
        }
    }

    async handleCreatePerson(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]') || document.querySelector('button[form="formNuevaPersona"]');
        const originalText = submitBtn ? submitBtn.textContent : 'Guardar';

        console.log('Attempting to create person...');

        try {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Guardando...';
            }

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.tablero_id = this.tableroId; // Add tablero ID

            // Validar lista_id
            if (!data.lista_id) {
                alert('Por favor selecciona una lista de destino');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
                return;
            }

            console.log('Sending person data:', data);

            const response = await fetch('/tableros/agregar_tarjeta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                console.log('Person created successfully, reloading...');
                window.location.reload();
            } else {
                console.error('Server error:', result.error);
                alert('Error: ' + (result.error || 'Error desconocido'));
            }
        } catch (error) {
            console.error('Network/JS error creating person:', error);
            alert('Error de conexión al crear la persona');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    }

    initListSortable() {
        if (this.boardContainer && typeof Sortable !== 'undefined') {
            new Sortable(this.boardContainer, {
                animation: 150,
                handle: '.list-header', // Arrastrar desde el encabezado
                draggable: '.kanban-list', // Elemento arrastrable
                ghostClass: 'sortable-ghost',
                direction: 'horizontal', // Forzar dirección horizontal
                onEnd: (evt) => {
                    console.log('Lista reordenada');
                    const listId = evt.item.dataset.listId;
                    const newIndex = evt.newIndex;

                    fetch('/tableros/mover_lista', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            lista_id: listId,
                            nueva_posicion: newIndex
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                console.log('Orden de listas guardado');
                            } else {
                                console.error('Error guardando orden:', data.error);
                                // Revertir si es necesario (opcional)
                            }
                        })
                        .catch(error => console.error('Error de red:', error));
                }
            });
        }
    }

    initSortable() {
        if (typeof Sortable === 'undefined') {
            console.warn('Sortable.js no está cargado aún, reintentando en 500ms...');
            if (this.retryCount === undefined) this.retryCount = 0;
            if (this.retryCount < 10) {
                this.retryCount++;
                setTimeout(() => this.initSortable(), 500);
            } else {
                console.error('No se pudo cargar Sortable.js después de 5 segundos');
            }
            return;
        }
        console.log('Sortable.js loaded, initializing lists...');

        this.lists.forEach(list => {
            new Sortable(list, {
                group: 'kanban', // Permite mover entre listas
                animation: 150,
                ghostClass: 'sortable-ghost',
                dragClass: 'sortable-drag',
                handle: '.person-card', // Solo permitir drag desde la tarjeta misma
                draggable: '.person-card', // Solo las tarjetas son arrastrables
                delay: 100, // Delay para evitar conflicto con clicks
                delayOnTouchOnly: false,
                touchStartThreshold: 5,
                onStart: (evt) => {
                    console.log('Drag started:', evt.item.dataset.id);
                    this.isDragging = true;
                    this.dragOriginListId = evt.from.closest('.kanban-list').dataset.listId;
                    // Colapsar la tarjeta si está expandida
                    evt.item.classList.remove('expanded');
                },
                onEnd: (evt) => {
                    this.handleDrop(evt);
                    // Pequeño timeout para evitar que el click se dispare inmediatamente
                    setTimeout(() => {
                        this.isDragging = false;
                    }, 100);
                }
            });
            console.log('Sortable initialized for list');
        });
    }

    handleDrop(evt) {
        const itemEl = evt.item;
        const newListId = evt.to.closest('.kanban-list').dataset.listId;
        const personId = itemEl.dataset.id;

        // Aquí iría la llamada al backend para actualizar el estado
        console.log(`Movida persona ${personId} a lista ${newListId}`);

        this.updatePersonStatus(personId, newListId);
    }

    async updatePersonStatus(personId, listId) {
        try {
            const response = await fetch('/tableros/mover_tarjeta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tarjeta_id: personId,
                    lista_origen_id: this.dragOriginListId,
                    lista_destino_id: listId
                })
            });

            if (!response.ok) {
                throw new Error('Error al mover la tarjeta');
            }

            const data = await response.json();
            // Mostrar notificación de éxito (usaremos un sistema de toast luego)
            console.log('Actualización exitosa:', data);

            // Actualizar color de la tarjeta visualmente
            const card = document.querySelector(`.person-card[data-id="${personId}"]`);
            const newList = document.querySelector(`.kanban-list[data-list-id="${listId}"]`);

            if (card && newList) {
                const newColor = newList.dataset.color;
                // Actualizar borde izquierdo
                const header = card.querySelector('.card-header');
                if (header) header.style.borderLeftColor = newColor;

                // Actualizar avatar
                const avatar = card.querySelector('.person-avatar');
                if (avatar) {
                    avatar.style.color = newColor;
                    avatar.style.background = newColor + '15'; // 15 es opacidad hex
                }

                // Actualizar data attribute para referencia futura
                card.dataset.color = newColor;
            }

            // Actualizar mapa si está cargado
            if (window.app && window.app.mapManager) {
                console.log('Refreshing map markers...');
                window.app.mapManager.loadMarkers();
            }

        } catch (error) {
            console.error('Error:', error);
            // Revertir movimiento si falla (opcional, requiere lógica extra)
            alert('Error al mover la tarjeta. Por favor recarga la página.');
        }
    }

    initCardInteractions() {
        document.addEventListener('click', (e) => {
            // Manejar expansión de tarjetas
            const card = e.target.closest('.person-card');

            // Ignorar si está siendo arrastrado (tiene clase sortable-drag)
            // Ignorar si está siendo arrastrado (tiene clase sortable-drag)
            if (card && !this.isDragging &&
                !document.body.classList.contains('selection-mode') && // Ignorar si está en modo selección
                !card.classList.contains('sortable-drag') &&
                !card.classList.contains('sortable-ghost') &&
                !e.target.closest('.action-btn') &&
                !e.target.closest('.card-checkbox') && // Ignorar checkbox de selección
                !e.target.closest('.card-selection-overlay') && // Ignorar overlay de selección
                !e.target.closest('a')) { // Ignorar enlaces

                // Si el click es dentro de card-details, no hacer toggle (para permitir seleccionar texto)
                if (e.target.closest('.card-details')) {
                    return;
                }

                console.log('Click en tarjeta:', card.dataset.id);
                this.toggleCard(card);
            }

            // Manejar botones de acción
            if (e.target.closest('.action-btn.delete')) {
                console.log('Delete button clicked');
                const card = e.target.closest('.person-card');
                const personId = card.dataset.id;
                console.log('Deleting person:', personId);

                // Usar modal personalizado en lugar de confirm()
                this.personToDeleteId = personId;
                this.cardToDeleteElement = card;

                const modal = document.getElementById('modalConfirmDelete');
                if (modal) {
                    console.log('Opening delete modal');
                    // Abrir modal (usando la lógica de ModalManager si es posible, o manual)
                    modal.style.display = 'flex';
                    // Force reflow
                    void modal.offsetWidth;
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                } else {
                    console.error('Delete modal not found!');
                }
            }
        });

        // Listener para el botón de confirmar eliminación
        const btnConfirmDelete = document.getElementById('btnConfirmDelete');
        if (btnConfirmDelete) {
            btnConfirmDelete.addEventListener('click', () => {
                if (this.personToDeleteId && this.cardToDeleteElement) {
                    this.deletePerson(this.personToDeleteId, this.cardToDeleteElement);

                    // Cerrar modal
                    const modal = document.getElementById('modalConfirmDelete');
                    modal.classList.remove('active');
                    setTimeout(() => {
                        modal.style.display = 'none';
                        document.body.style.overflow = '';
                    }, 300);

                    this.personToDeleteId = null;
                    this.cardToDeleteElement = null;
                }
            });
        }
    }

    toggleCard(card) {
        // Colapsar otras tarjetas expandidas (comportamiento acordeón opcional)
        // document.querySelectorAll('.person-card.expanded').forEach(c => {
        //     if (c !== card) c.classList.remove('expanded');
        // });

        console.log('Toggle card class. Current classes:', card.className);
        card.classList.toggle('expanded');
        console.log('New classes:', card.className);

        // Si se expande, resaltar en el mapa
        if (card.classList.contains('expanded')) {
            if (typeof window.highlightMapMarker === 'function') {
                window.highlightMapMarker(card.dataset.id);
            }
        }
    }

    initListEditing() {
        // Listener para botones de editar lista
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-edit-list');
            if (btn) {
                this.handleEditList(btn);
            }
        });

        // Listener para guardar cambios de lista
        const formEdit = document.getElementById('formEditarLista');
        if (formEdit) {
            formEdit.addEventListener('submit', (e) => this.handleSaveList(e));
        }

        // Listener para botón eliminar en el modal de edición
        const btnDelete = document.getElementById('btnEliminarLista');
        if (btnDelete) {
            btnDelete.addEventListener('click', () => {
                // Cerrar modal de edición
                const editModal = document.getElementById('modalEditarLista');
                editModal.classList.remove('active');
                editModal.style.display = 'none';

                // Abrir modal de confirmación
                const confirmModal = document.getElementById('modalConfirmarEliminarLista');
                if (confirmModal) {
                    confirmModal.style.display = 'flex';
                    void confirmModal.offsetWidth;
                    confirmModal.classList.add('active');
                }
            });
        }

        // Listener para confirmar eliminación definitiva
        const btnConfirmDeleteList = document.getElementById('btnConfirmDeleteList');
        if (btnConfirmDeleteList) {
            btnConfirmDeleteList.addEventListener('click', () => this.handleConfirmDeleteList());
        }
    }

    handleEditList(btn) {
        const listId = btn.dataset.listId;
        const listName = btn.dataset.listName;
        const listColor = btn.dataset.listColor;

        // Poblar el modal
        document.getElementById('editListaId').value = listId;
        document.getElementById('editListaNombre').value = listName;

        // Seleccionar el color correcto
        const colorInputs = document.querySelectorAll('input[name="color"]');
        colorInputs.forEach(input => {
            if (input.value === listColor) {
                input.checked = true;
            }
        });

        // Abrir modal
        const modal = document.getElementById('modalEditarLista');
        if (modal) {
            modal.style.display = 'flex';
            void modal.offsetWidth;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    async handleSaveList(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(`/tableros/${this.tableroId}/lista/editar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                window.location.reload();
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al guardar los cambios');
        }
    }

    async handleConfirmDeleteList() {
        const listId = document.getElementById('editListaId').value;
        if (!listId) return;

        try {
            const response = await fetch(`/tableros/${this.tableroId}/lista/eliminar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ lista_id: listId })
            });

            const result = await response.json();
            if (result.success) {
                window.location.reload();
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al eliminar la lista');
        }
    }

    async deletePerson(personId, cardElement) {
        try {
            const response = await fetch(`/tableros/eliminar_tarjeta/${personId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                cardElement.remove();

                // Actualizar mapa si está cargado
                if (window.app && window.app.mapManager) {
                    console.log('Refreshing map markers after delete...');
                    window.app.mapManager.loadMarkers();
                }
                // Actualizar contadores
                // this.updateCounters();
            } else {
                alert('Error al eliminar');
            }
        } catch (error) {
            console.error(error);
            alert('Error de conexión');
        }
    }
    initSearch() {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.person-card');

            cards.forEach(card => {
                const name = card.querySelector('.person-name').textContent.toLowerCase();
                const phone = card.dataset.phone ? card.dataset.phone.toLowerCase() : '';
                const spouse = card.dataset.conyuge ? card.dataset.conyuge.toLowerCase() : '';

                // Búsqueda extendida: nombre, teléfono y cónyuge
                if (name.includes(searchTerm) ||
                    phone.includes(searchTerm) ||
                    spouse.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}
