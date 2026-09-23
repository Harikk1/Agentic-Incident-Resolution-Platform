"""
SmartOps AI - Local Development Multi-Process Launcher
Starts User Service, Order Service, Payment Service, Backend, MCP Server, and Frontend in one command.
"""
import sys
import os
import subprocess
import time
import signal

PYTHON_EXE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe"))
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

PROCESSES = []

def start_service(name, cmd, cwd=ROOT_DIR):
    print(f"[SmartOps] Launching {name}...")
    p = subprocess.Popen(cmd, cwd=cwd, shell=False)
    PROCESSES.append((name, p))
    time.sleep(1)

def shutdown(sig, frame):
    print("\n[SmartOps] Shutting down all services...")
    for name, p in reversed(PROCESSES):
        print(f"Stopping {name} (PID: {p.pid})...")
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            else:
                p.terminate()
                p.wait(timeout=2)
        except Exception:
            p.kill()
    print("[SmartOps] All services stopped.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 65)
    print("  🚀 Starting SmartOps AI Incident Response Platform")
    print("=" * 65)

    # 1. Microservices
    start_service("User Service (:8001)", [PYTHON_EXE, "-m", "uvicorn", "main:app", "--app-dir", "services/user-service", "--port", "8001"])
    start_service("Order Service (:8002)", [PYTHON_EXE, "-m", "uvicorn", "main:app", "--app-dir", "services/order-service", "--port", "8002"])
    start_service("Payment Service (:8003)", [PYTHON_EXE, "-m", "uvicorn", "main:app", "--app-dir", "services/payment-service", "--port", "8003"])

    # 2. SmartOps Core Backend
    start_service("Backend Gateway (:8000)", [PYTHON_EXE, "-m", "uvicorn", "backend.app.main:app", "--port", "8000"])

    # 3. FastMCP Server
    start_service("FastMCP Server (:8005)", [PYTHON_EXE, "-m", "mcp_server.server"])

    # 4. React Frontend (via npm run dev in frontend/)
    frontend_dir = os.path.join(ROOT_DIR, "frontend")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    start_service("React Frontend (:3000)", [npm_cmd, "run", "dev"], cwd=frontend_dir)

    print("\n" + "=" * 65)
    print("  ✅ All Services are Running!")
    print("=" * 65)
    print("  👉 React Dashboard:     http://localhost:3000")
    print("  👉 Backend API Docs:    http://localhost:8000/docs")
    print("  👉 User Service:        http://localhost:8001/health")
    print("  👉 Order Service:       http://localhost:8002/health")
    print("  👉 Payment Service:     http://localhost:8003/health")
    print("  👉 MCP Server:          http://localhost:8005")
    print("\n  Demo Login Credentials:")
    print("    - Admin:    admin@smartops.ai / adminpassword")
    print("    - Engineer: engineer@smartops.ai / engineerpassword")
    print("    - Viewer:   viewer@smartops.ai / viewerpassword")
    print("\n  Press Ctrl+C at any time to gracefully terminate all services.")
    print("=" * 65 + "\n")

    # Keep main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
