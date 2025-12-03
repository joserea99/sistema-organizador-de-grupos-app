import subprocess
import time

with open('server_launcher.log', 'w') as f:
    f.write("Launching server...\n")
    try:
        proc = subprocess.Popen(['./venv/bin/python', 'run.py'], stdout=f, stderr=f)
        f.write(f"Server launched with PID {proc.pid}\n")
    except Exception as e:
        f.write(f"Failed to launch: {e}\n")
