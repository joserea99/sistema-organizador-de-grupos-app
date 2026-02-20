import os
import re

css_dir = 'app/static/css/themes'
files = ['clasico.css', 'minimalista.css', 'moderno.css', 'oscuro.css']

output = "/* Unified Theme Variables */\n\n"

for f in files:
    theme_name = f.replace('.css', '')
    path = os.path.join(css_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Replace :root with [data-theme="theme_name"]
            content = re.sub(r':root\s*\{', f'[data-theme="{theme_name}"] {{', content)
            
            # Replace body { with [data-theme="theme_name"] {
            content = re.sub(r'body\s*\{', f'[data-theme="{theme_name}"] {{', content)
            
            # Replace body.dark { with [data-theme="theme_name"] {
            content = re.sub(r'body\.dark\s*\{', f'[data-theme="{theme_name}"] {{', content)
            
            output += f"/* === THEME: {theme_name.upper()} === */\n"
            output += content + "\n\n"

with open(os.path.join(css_dir, 'variables.css'), 'w', encoding='utf-8') as out_file:
    out_file.write(output)

print("Variables.css created successfully!")
