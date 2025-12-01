/**
 * Módulo Principal
 * Inicializa la aplicación y coordina los módulos
 */

import { ThemeManager } from './themes.js';
import { ModalManager } from './modals.js';
import { FilterManager } from './filters.js';

console.log('app.js module loading...');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');

    // Inicializar Gestor de Temas
    const themeManager = new ThemeManager();
    themeManager.init();

    // Inicializar Gestor de Modales
    const modalManager = new ModalManager();
    // modalManager.init() is called in constructor

    // Inicializar Gestor de Filtros (Buscador)
    const filterManager = new FilterManager();

    // Exponer instancias globalmente para depuración si es necesario
    window.app = {
        themeManager
    };

    console.log('App inicializada con tema:', themeManager.currentTheme);

    // Inicializar otros componentes si existen en la página
    if (document.querySelector('.kanban-board')) {
        console.log('Kanban board detected, loading module...');
        // Cargar módulo Kanban dinámicamente
        import('./kanban.js').then(module => {
            console.log('Kanban module loaded successfully');
            window.app.kanban = new module.KanbanBoard();
        }).catch(err => {
            console.error('Error loading Kanban module:', err);
        });
    } else {
        console.log('No kanban board found on this page');
    }

    if (document.querySelector('.maps-section')) {
        console.log('Maps section detected, loading module...');
        // Cargar módulo Mapas dinámicamente
        import('./maps.js').then(module => {
            console.log('Maps module loaded successfully');
            console.log('Maps module loaded successfully');
            window.mapManager = new module.MapManager();
            window.app.mapManager = window.mapManager; // Keep reference in app just in case
        }).catch(err => {
            console.error('Error loading Maps module:', err);
        });
    } else {
        console.log('No maps section found on this page');
    }
});

console.log('app.js module loaded');
