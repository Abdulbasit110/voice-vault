"""
Vercel serverless function wrapper for FastAPI backend
"""
import sys
import os

# Add parent directory to path to import backend modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Change to backend directory for relative imports
os.chdir(backend_dir)

try:
    from mangum import Mangum
    from main import app
    
    # Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Fallback if mangum not available - use direct ASGI handler
    from main import app
    handler = app

