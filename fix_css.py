import re
import os

filepath = 'app/static/css/themes/variables.css'

with open(filepath, 'r') as f:
    text = f.read()

# We need to restructure variables.css. 
# Right now, it has 4 sections. Each section defines `[data-theme="X"] { ... }` and then immediately defines global classes `.header { ... }`.
# We want to extract ALL global classes and put them at the end or beginning exactly ONCE.
# Wait, what if the global classes defined in 'oscuro' are different from 'clasico'?
# Yes, they ARE different. For example, 'moderno' adds `backdrop-filter: var(--glass-blur)` to `.header`.
# So those differences MUST be scoped to `[data-theme="moderno"] .header`.

# Strategy:
# Parse the CSS into blocks.
# A block is either a selector { rules } or a comment.

# Let's do it with some manual logic or we can just download a clean version. Wait, instead of a complex parser, I can just write out the desired optimized variables.css since I can see what they are trying to achieve.

# Actually, the user has identical structures for most components. The base bindings:
base_bindings = """
/* === APLICACIÓN DE VARIABLES A COMPONENTES (GLOBAL) === */
body {
    background: var(--bg-body) !important;
    color: var(--text-primary) !important;
}

.header {
    background: var(--bg-primary) !important;
    box-shadow: var(--shadow-sm);
    border-bottom: 1px solid var(--border-color);
}

.header-title {
    color: var(--text-primary) !important;
}

.btn-primary {
    background: var(--color-primary);
    color: var(--text-on-primary) !important;
}
.btn-primary:hover {
    background: var(--color-primary-dark);
    transform: translateY(-1px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color);
}

.btn-success {
    background: var(--color-success);
    color: var(--text-on-primary) !important;
}

.btn-danger {
    background: var(--color-error);
    color: var(--text-on-primary) !important;
}

.card, .kanban-list, .controls-section, .import-export-section, .maps-section, .dropdown-menu, .modal-content {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

.person-card {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-sm);
}

.person-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    background: var(--bg-tertiary) !important;
}

.person-card.expanded {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
    border-color: var(--color-primary);
    background: var(--bg-primary) !important;
}

.list-header {
    background: var(--bg-secondary) !important;
    border-bottom-color: var(--border-color);
}

.list-title, .person-name, .modal-title, .controls-title {
    color: var(--text-primary) !important;
}

.list-count, .tag {
    background: var(--bg-tertiary);
    color: var(--text-primary) !important;
}

.person-info, .form-label, .modal-close {
    color: var(--text-secondary) !important;
}

.form-input, .form-select, .form-textarea {
    background: var(--bg-body) !important;
    border-color: var(--border-color);
    color: var(--text-primary) !important;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
    border-color: var(--color-primary);
}

.toast {
    background: var(--bg-secondary) !important;
    box-shadow: var(--shadow-xl);
    border-left: 4px solid var(--color-success);
    color: var(--text-primary) !important;
}

.map-filter-btn {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color);
    color: var(--text-secondary) !important;
}
.map-filter-btn.active {
    background: var(--color-primary) !important;
    color: var(--text-on-primary) !important;
    border-color: var(--color-primary);
}

/* === OVERRIDES ESPECÍFICOS DE TEMAS === */
[data-theme="moderno"] body {
    background-attachment: fixed;
}
[data-theme="moderno"] .header {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-bottom: 1px solid var(--glass-border);
}
[data-theme="moderno"] .btn-primary {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    box-shadow: var(--glow-primary);
}

[data-theme="minimalista"] .card, 
[data-theme="minimalista"] .kanban-list, 
[data-theme="minimalista"] .person-card,
[data-theme="minimalista"] .modal-content,
[data-theme="minimalista"] .controls-section {
    box-shadow: none !important;
    border-radius: 4px !important;
}
[data-theme="minimalista"] .header {
    box-shadow: none !important;
}
[data-theme="minimalista"] body {
    font-family: 'Inter', sans-serif !important;
}
"""

with open(filepath, 'r') as f:
    original = f.read()

# I will find all `/* === THEME:` markers and keep ONLY the `:root` or `[data-theme="X"]` variable definitions.
# I will strip out all other rules!

# Regular expression to extract the `[data-theme="X"] { ... }` blocks:
theme_blocks = re.findall(r'(\[data-theme="[^"]+"\]\s*\{[^}]+\})', original)

# Let's concatenate those clean blocks, and then append base_bindings!
new_css = "/* Unified Theme Variables */\n\n"
for block in theme_blocks:
    if "--color-primary:" in block or "--bg-body:" in block:
        new_css += block + "\n\n"

new_css += base_bindings

with open(filepath, 'w') as f:
    f.write(new_css)

print("Variables CSS Successfully rewritten!")
