"""
Development server runner for the Legal Case Analyzer API
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting Legal Case Analyzer API Development Server...")
    print("📍 Backend directory:", backend_dir.absolute())
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Use the current Python executable
    python_exe = sys.executable
    
    # Run uvicorn using subprocess to avoid import issues
    cmd = [
        python_exe, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload", 
        "--log-level", "info"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running server: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Please install requirements first:")
        print("   pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
