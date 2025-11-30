import sys
import traceback

print("Starting application...", file=sys.stderr, flush=True)

try:
    print("Importing create_app...", file=sys.stderr, flush=True)
    from app import create_app
    
    print("Creating Flask app...", file=sys.stderr, flush=True)
    app = create_app()
    
    print("App created successfully!", file=sys.stderr, flush=True)
    
    if __name__ == '__main__':
        print("Running in development mode", file=sys.stderr, flush=True)
        app.run()
    else:
        print("Running in production mode", file=sys.stderr, flush=True)
        
except Exception as e:
    print(f"ERROR: {str(e)}", file=sys.stderr, flush=True)
    print("Full traceback:", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
# Force rebuild
