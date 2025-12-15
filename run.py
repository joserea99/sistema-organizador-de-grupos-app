import sys
import traceback

print("Starting application...", file=sys.stderr, flush=True)

try:
    print("Importing create_app...", file=sys.stderr, flush=True)
    from app import create_app
    
    print("Creating Flask app...", file=sys.stderr, flush=True)
    app = create_app()
    
    # Auto-run migrations on startup (because Railway behaves unexpectedly with Procfile)
    with app.app_context():
        print("🔧 Attempting automatic database migration in run.py...", file=sys.stderr, flush=True)
        try:
            from flask_migrate import upgrade
            upgrade()
            print("✅ Automatic migration successful!", file=sys.stderr, flush=True)
            
            # Compile translations
            import subprocess
            print("🌍 Compiling translations...", file=sys.stderr, flush=True)
            subprocess.run(["pybabel", "compile", "-d", "app/translations"], check=False)
            print("✅ Translations compiled!", file=sys.stderr, flush=True)
            
        except Exception as e:
            print(f"❌ Automatic migration failed: {e}", file=sys.stderr, flush=True)
            # We don't exit here, hoping the app might still work or shows the error later
            
    print("App created successfully!", file=sys.stderr, flush=True)
    
except Exception as e:
    print(f"CRITICAL ERROR: {str(e)}", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    
    # Fallback app to show error in browser
    from flask import Flask
    app = Flask(__name__)
    
    error_msg = f"""
    <h1>Application Failed to Start</h1>
    <p>Error: {str(e)}</p>
    <pre>{traceback.format_exc()}</pre>
    """
    
    @app.route('/')
    @app.route('/<path:path>')
    def catch_all(path=''):
        return error_msg, 500

if __name__ == '__main__':
    print("Running in development mode", file=sys.stderr, flush=True)
    app.run()
else:
    print("Running in production mode", file=sys.stderr, flush=True)
