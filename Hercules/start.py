#!/usr/bin/env python3
import subprocess
import os
import sys
import signal
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    venv_bin = os.path.join(root_dir, ".venv", "bin")

    print("🚀 Starting Pentest Agent Suite...")

    # Set up environment for the backend
    env = os.environ.copy()
    env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    
    # Check if .venv exists
    if not os.path.exists(venv_bin):
        print("❌ Error: Virtual environment not found. Please run 'uv sync' or set up the venv first.")
        sys.exit(1)

    print("Starting FastAPI Backend...")
    backend_process = subprocess.Popen(
        [os.path.join(venv_bin, "uvicorn"), "backend.app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=root_dir,
        env=env
    )

    print("Starting Vite Frontend...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )

    def signal_handler(sig, frame):
        print("\n🛑 Shutting down Pentest Agent Suite...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✅ Both processes terminated cleanly.")
        sys.exit(0)

    # Register signal handlers for graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n=======================================================")
    print("✅ PentestAI is running!")
    print("🌐 Frontend URL: http://localhost:5173")
    print("🔌 Backend API:  http://localhost:8000")
    print("Press Ctrl+C to stop both servers.")
    print("=======================================================\n")

    try:
        # Keep the main process alive and monitor children
        while True:
            time.sleep(1)
            
            # Check if either process died unexpectedly
            if backend_process.poll() is not None:
                print("❌ Backend process died unexpectedly. Shutting down...")
                frontend_process.terminate()
                sys.exit(1)
                
            if frontend_process.poll() is not None:
                print("❌ Frontend process died unexpectedly. Shutting down...")
                backend_process.terminate()
                sys.exit(1)
                
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
