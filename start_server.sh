#!/bin/bash
./venv/bin/python run.py > server.log 2>&1 &
echo $! > server.pid
