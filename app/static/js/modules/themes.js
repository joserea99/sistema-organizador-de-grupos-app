/**
 * Sistema de Gestión de Temas
 * Permite cambiar entre diferentes temas visuales manteniendo la funcionalidad
 */

export class ThemeManager {
    constructor() {
        this.currentTheme = this.loadTheme();
        this.themes = {
            moderno: {
                name: 'Moderno',
                description: 'Dark con glassmorphism y colores vibrantes',
                file: 'moderno.css',
                preview: '/static/img/themes/moderno-preview.png'
            },
            clasico: {
                name: 'Clásico',
                description: 'Light profesional y tradicional',
                file: 'clasico.css',
                preview: '/static/img/themes/clasico-preview.png'
            },
            minimalista: {
                name: 'Minimalista',
                description: 'Clean, simple y espacioso',
                file: 'minimalista.css',
                preview: '/static/img/themes/minimalista-preview.png'
            },
            oscuro: {
                name: 'Oscuro',
                description: 'Dark mode moderno y elegante',
                file: 'oscuro.css',
                preview: '/static/img/themes/oscuro-preview.png'
            }
        };

        // Auto-inicializar si no se llama manualmente
        console.log('ThemeManager constructor, tema actual:', this.currentTheme);
    }

    /**
     * Cargar tema guardado desde localStorage
     */
    loadTheme() {
        return localStorage.getItem('selectedTheme') || 'clasico';
    }

    /**
     * Guardar tema seleccionado
     */
    saveTheme(themeName) {
        localStorage.setItem('selectedTheme', themeName);
    }

    /**
     * Aplicar tema al documento
     */
    applyTheme(themeName) {
        if (!this.themes[themeName]) {
            console.warn(`Tema "${themeName}" no existe. Usando tema por defecto.`);
            themeName = 'clasico';
        }

        // Actualizar hoja de estilos
        const themeLink = document.getElementById('theme-style');
        if (themeLink) {
            themeLink.href = `/static/css/themes/${this.themes[themeName].file}`;
        } else {
            const linkElement = document.createElement('link');
            linkElement.id = 'theme-style';
            linkElement.rel = 'stylesheet';
            linkElement.href = `/static/css/themes/${this.themes[themeName].file}`;
            document.head.appendChild(linkElement);
        }

        // Guardar preferencia
        this.currentTheme = themeName;
        this.saveTheme(themeName);

        // Actualizar atributo en body para CSS específico
        document.body.setAttribute('data-theme', themeName);

        // Toggle 'dark' class for Tailwind
        if (['oscuro', 'moderno'].includes(themeName)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }

        // Disparar evento para notificar el cambio
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: themeName }
        }));

        console.log(`✅ Tema "${this.themes[themeName].name}" aplicado`);
    }

    /**
     * Inicializar tema al cargar la página
     */
    init() {
        this.applyTheme(this.currentTheme);
        this.attachThemeSelector();
    }

    /**
     * Adjuntar event listeners al selector de temas
     */
    attachThemeSelector() {
        // Soporte para selectores con data-theme-select
        const themeButtons = document.querySelectorAll('[data-theme-select]');
        themeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const selectedTheme = e.currentTarget.getAttribute('data-theme-select');
                this.applyTheme(selectedTheme);
                this.updateThemeUI(selectedTheme);
            });
        });

        // Soporte para select element con id="theme-selector"
        const themeSelect = document.getElementById('theme-selector');
        if (themeSelect) {
            console.log('Theme selector found, attaching change event');
            themeSelect.addEventListener('change', (e) => {
                const selectedTheme = e.target.value;
                console.log('Theme changed to:', selectedTheme);
                this.applyTheme(selectedTheme);
            });

            // Establecer el tema actual como seleccionado
            themeSelect.value = this.currentTheme;
        }
    }

    /**
     * Actualizar UI del selector de temas
     */
    updateThemeUI(selectedTheme) {
        const themeButtons = document.querySelectorAll('[data-theme-select]');
        themeButtons.forEach(button => {
            if (button.getAttribute('data-theme-select') === selectedTheme) {
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');
            } else {
                button.classList.remove('active');
                button.setAttribute('aria-selected', 'false');
            }
        });
    }

    /**
     * Obtener información del tema actual
     */
    getCurrentThemeInfo() {
        return {
            id: this.currentTheme,
            ...this.themes[this.currentTheme]
        };
    }

    /**
     * Obtener lista de todos los temas disponibles
     */
    getAllThemes() {
        return Object.keys(this.themes).map(key => ({
            id: key,
            ...this.themes[key]
        }));
    }
}

console.log('themes.js module loaded');
