#!/bin/bash
set -e

echo "========================================="
echo "Starting Railway Deployment"
echo "========================================="

echo "Step 1: Running database migrations..."
import os
import sys
os.environ.setdefault('FLASK_APP', 'run.py')

from app import create_app
from flask_migrate import upgrade

app = create_app()
with app.app_context():
    print("Applying database migrations...")
    upgrade()
    print("✓ Migrations completed successfully")
PYTHON_SCRIPT

echo ""
echo "Step 2: Compiling translations..."
python -c "
try:
    from babel.messages import frontend as babel
    import subprocess
    subprocess.run(['pybabel', 'compile', '-d', 'app/translations'], check=False)
    print('✓ Translations compiled')
except:
    print('Note: Babel not available for compilation')
" || echo "Skipping translation compilation"

echo ""
echo "Step 3: Starting application..."
echo "========================================="
exec gunicorn --bind 0.0.0.0:$PORT run:app
