#!/bin/bash
# Post-deployment script to compile translations
echo "Compiling translations..."
pybabel compile -d app/translations || echo "Warning: pybabel not found, translations may not work"
echo "Translations compiled successfully!"
