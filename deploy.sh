#!/bin/bash
set -e

echo "========================================="
echo "Starting Railway Deployment (DEBUG VERSION V2)"
echo "========================================="

echo "Step 1: Running database migrations..."
# python perform_migrations.py
echo "Skipping migrations for debugging..."

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
