/**
 * Módulo de Modales
 * Gestiona la apertura y cierre de modales
 */

export class ModalManager {
    constructor() {
        this.modals = document.querySelectorAll('.modal');
        this.init();
    }

    init() {
        console.log('ModalManager initialized');
        // Cerrar al hacer click fuera o en botón cerrar
        this.modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.closest('.modal-close') || e.target.closest('[data-dismiss="modal"]')) {
                    this.closeModal(modal);
                }
            });
        });

        // Listeners para abrir modales
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-toggle="modal"]');
            if (trigger) {
                const targetId = trigger.dataset.target;
                console.log('Modal trigger clicked for:', targetId);
                const modal = document.querySelector(targetId);
                if (modal) {
                    this.openModal(modal);
                } else {
                    console.error(`Modal ${targetId} not found`);
                }
            }
        });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.active');
                if (activeModal) {
                    this.closeModal(activeModal);
                }
            }
        });
    }

    openModal(modal) {
        console.log('Opening modal:', modal.id);
        modal.style.display = 'flex';
        // Forzar reflow para animación
        modal.offsetHeight;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevenir scroll del body
        console.log('Modal opened, overflow hidden');
    }

    closeModal(modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }, 300); // Esperar a que termine la transición CSS
    }
}
