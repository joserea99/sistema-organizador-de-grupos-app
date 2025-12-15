#!/bin/bash
echo "Compiling translations..."
pybabel compile -d app/translations 2>/dev/null || echo "Note: pybabel not found, translations will be compiled in production"
