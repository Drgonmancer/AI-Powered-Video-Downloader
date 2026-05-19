import os
import shutil
import subprocess
import sys
import time
import webbrowser
import signal

BACKEND_PORT = 8976
FRONTEND_PORT = 5173

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

processes = []


def log(tag, msg):
    print(f"  [{tag}] {msg}")


def check_python():
    ver = sys.version_info
    if ver < (3, 10):
        log("FAIL", f"Python {ver.major}.{ver.minor} too low, need 3.10+")
        sys.exit(1)
    log("OK", f"Python {ver.major}.{ver.minor}.{ver.micro}")


def check_node():
    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node or not npm:
        log("WARN", "Node.js/npm not found, frontend disabled")
        return False
    result = subprocess.run([node, "--version"], capture_output=True, text=True)
    log("OK", f"Node.js {result.stdout.strip()}")
    return True


def install_backend_deps():
    req = os.path.join(BACKEND_DIR, "requirements.txt")
    if not os.path.exists(req):
        return
    log("..", "Installing Python dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install",
             "-r", req, "-q"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        log("OK", "Backend dependencies installed")
    except Exception as e:
        log("FAIL", f"pip install failed: {e}")
        sys.exit(1)


def install_frontend_deps():
    pkg = os.path.join(FRONTEND_DIR, "package.json")
    if not os.path.exists(pkg):
        log("WARN", "No package.json, skip frontend deps")
        return False
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if os.path.isdir(node_modules) and os.listdir(node_modules):
        log("OK", "Frontend dependencies already installed")
        return True
    log("..", "Installing Node.js dependencies (npm install)...")
    try:
        npm = shutil.which("npm") or "npm"
        subprocess.check_call(
            [npm, "install"],
            cwd=FRONTEND_DIR,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        log("OK", "Frontend dependencies installed")
        return True
    except Exception as e:
        log("WARN", f"npm install failed: {e}, frontend may not work")
        return False


def check_yt_dlp():
    try:
        import yt_dlp
        log("OK", "yt-dlp ready")
    except ImportError:
        log("..", "Installing yt-dlp...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install",
                 "yt-dlp", "-q"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            log("OK", "yt-dlp installed")
        except Exception:
            log("FAIL", "yt-dlp install failed")
            sys.exit(1)


def check_browser_cookie3():
    try:
        import browser_cookie3
        log("OK", "browser-cookie3 ready (Edge support)")
    except ImportError:
        log("..", "Installing browser-cookie3 for Edge...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install",
                 "browser-cookie3>=0.19.0", "-q"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            log("OK", "browser-cookie3 installed")
        except Exception:
            log("WARN", "browser-cookie3 install failed, Edge auto-cookie disabled")


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        log("OK", "ffmpeg ready")
        return True
    log("WARN", "ffmpeg not found - format conversion disabled")
    return False


def ensure_dirs():
    os.makedirs(os.path.join(BASE_DIR, "downloads"), exist_ok=True)


def start_backend():
    log("..", f"Starting backend server (port {BACKEND_PORT})...")
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND_DIR
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn",
         "main:app", "--host", "127.0.0.1", "--port",
         str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes.append(("backend", proc))
    return proc


def start_frontend():
    node = shutil.which("node") or "node"
    npx = shutil.which("npx") or "npx"
    pkg = os.path.join(FRONTEND_DIR, "package.json")
    if not os.path.exists(pkg):
        log("WARN", "No frontend to start")
        return None
    log("..", f"Starting frontend dev server (port {FRONTEND_PORT})...")
    proc = subprocess.Popen(
        [npx, "vite", "--port", str(FRONTEND_PORT), "--host"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        if sys.platform == "win32" else 0,
    )
    processes.append(("frontend", proc))
    return proc


def wait_for_backend(timeout=15):
    import urllib.request
    for i in range(timeout * 10):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{BACKEND_PORT}/api/health", timeout=1)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def wait_for_frontend(timeout=20):
    import urllib.request
    for i in range(timeout * 10):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{FRONTEND_PORT}/", timeout=1)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def cleanup(signum=None, frame=None):
    print("\n\n  Shutting down...")
    for name, proc in processes:
        try:
            if sys.platform == "win32":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    log("DONE", "All services stopped")


def main():
    print("")
    print("=" * 54)
    print("   VideoForge Pro - AI Universal Video Downloader")
    print("=" * 54)
    print("")

    log("CHECK", "Environment validation")
    print("-" * 40)

    has_node = check_python() and check_node()

    print("")
    log("INSTALL", "Dependencies")
    print("-" * 40)

    install_backend_deps()
    has_frontend = has_node and install_frontend_deps()

    print("")
    log("TOOLS", "Runtime tools")
    print("-" * 40)

    check_yt_dlp()
    check_browser_cookie3()
    check_ffmpeg()
    ensure_dirs()

    print("")
    log("LAUNCH", "Starting all services")
    print("-" * 40)

    backend_proc = start_backend()
    frontend_proc = start_frontend() if has_frontend else None

    print("")
    log("WAIT", "Waiting for services to be ready...")

    backend_ready = wait_for_backend()
    if backend_ready:
        log("OK", f"Backend online: http://localhost:{BACKEND_PORT}")
    else:
        log("FAIL", "Backend failed to start")

    frontend_ready = False
    if frontend_proc:
        frontend_ready = wait_for_frontend()
        if frontend_ready:
            log("OK", f"Frontend online: http://localhost:{FRONTEND_PORT}")
        else:
            log("WARN", "Frontend may still be starting...")

    print("")
    print("=" * 54)
    print("   ALL SYSTEMS READY")
    print("=" * 54)
    print("")
    print(f"  Frontend:  http://localhost:{FRONTEND_PORT}/")
    print(f"  Backend:   http://localhost:{BACKEND_PORT}/")
    print(f"  API Docs:  http://localhost:{BACKEND_PORT}/docs")
    print("")

    url = f"http://localhost:{FRONTEND_PORT}/" if frontend_ready else f"http://localhost:{BACKEND_PORT}/docs"
    try:
        webbrowser.open(url)
    except Exception:
        pass

    print("  Press Ctrl+C to stop all services\n")

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    for name, proc in processes:
        try:
            for line in iter(proc.stdout.readline, ""):
                if line.strip():
                    print(f"  [{name.upper()}] {line.rstrip()}")
        except Exception:
            pass

    for name, proc in processes:
        proc.wait()

    cleanup()


if __name__ == "__main__":
    main()
