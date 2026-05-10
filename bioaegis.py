#!/usr/bin/env python3
"""
BioAEGIS — Setup en una línea.
Descarga el proyecto, instala dependencias y arranca todo.
Autor: Fernando Fondillo — VIHOLABS
"""
import subprocess, sys, os

VERSION = "1.0"
COMMANDS = {
    "start":        "Iniciar BioAEGIS",
    "stop":         "Detener servidores",
    "status":       "Ver estado",
    "install":      "Instalar dependencias",
    "dashboard":    "Abrir dashboard en navegador",
    "docs":         "Abrir documentación API",
    "logs":         "Ver logs del servidor",
    "help":         "Mostrar esta ayuda",
}

BACKEND_PORT  = 8000
DASHBOARD_PORT = 3001
PROJECT_DIR = os.path.expanduser("~/BIOAEGIS")
BACKEND_DIR  = os.path.join(PROJECT_DIR, "backend")
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend", "bioaegis-dashboard")
DB_DIR       = os.path.expanduser("~/BIOAEGIS/backend")

def run(cmd, cwd=None, capture=False):
    r = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR, capture_output=capture, text=True)
    if r.returncode != 0 and capture:
        print(f"  ⚠ {r.stderr.strip()[:100]}")
    return r

def check_env():
    print("🔍 Verificando entorno...")
    checks = [
        ("Python",    ["python3", "--version"]),
        ("Git",       ["git",    "--version"]),
    ]
    for name, cmd in checks:
        r = run(" ".join(cmd), capture=True)
        v = r.stdout.split("\n")[0] if r.returncode == 0 else "❌ no encontrado"
        print(f"  {'✅' if r.returncode == 0 else '❌'} {name}: {v}")

    if not os.path.exists(PROJECT_DIR):
        print(f"\n📥 Descargando BioAEGIS...")
        r = run(f"git clone https://github.com/fernandofondillo/BIOAEGIS.git {PROJECT_DIR}")
        if r.returncode != 0:
            print(f"  ❌ Error: {r.stderr}")
            return False
        print(f"  ✅ Proyecto descargado en ~/BIOAEGIS")
    return True

def install():
    print("\n📦 Instalando dependencias Python...")
    deps = "fastapi uvicorn[standard] loguru pydantic httpx"
    r = run(f'python3 -m pip install --user {deps}')
    if r.returncode != 0:
        r = run(f'pip3 install {deps}')
    if r.returncode != 0:
        r = run(f'python3 -m pip install --break-system-packages {deps}')
    print(f"  ✅ Dependencias Python instaladas")

    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("\n📦 Instalando frontend...")
        run(f"cd {FRONTEND_DIR} && npm install")
        run(f"cd {FRONTEND_DIR} && npm run build")
        print(f"  ✅ Frontend construido")
    return True

def start():
    print(f"\n🚀 Arrancando BioAEGIS...")
    os.makedirs(DB_DIR, exist_ok=True)

    # Backend
    print(f"  🧠 Backend → http://localhost:{BACKEND_PORT}")
    run(f'cd {BACKEND_DIR} && python3 -m uvicorn app.main:app --host 127.0.0.1 --port {BACKEND_PORT} &')
    
    # Dashboard
    dist = os.path.join(FRONTEND_DIR, "dist")
    if os.path.exists(dist):
        os.chdir(dist)
        print(f"  🌐 Dashboard → http://localhost:{DASHBOARD_PORT}")
        run(f'cd {dist} && python3 -m http.server {DASHBOARD_PORT} &')
    else:
        print(f"  ⚠ Frontend no construido. Ejecuta: python3 bioaegis.py install")

    print(f"\n✅ ¡Listo! Abre http://localhost:{DASHBOARD_PORT} en tu navegador")

def stop():
    print("🛑 Deteniendo servidores...")
    run("pkill -f 'uvicorn app.main:app'")
    run("pkill -f 'http.server 3001'")
    print("  ✅ Servidores detenidos")

def status():
    r_backend = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{BACKEND_PORT}/health", capture=True)
    r_dashboard = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{DASHBOARD_PORT}/", capture=True)
    be = "✅ Online" if r_backend.stdout.strip() == "200" else "❌ Offline"
    da = "✅ Online" if r_dashboard.stdout.strip() == "200" else "❌ Offline"
    print(f"  🧠 Backend  ({BACKEND_PORT}):  {be}")
    print(f"  🌐 Dashboard ({DASHBOARD_PORT}): {da}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description=f"BioAEGIS {VERSION} — Sistema de Gemelo Digital Biológico")
    parser.add_argument("command", nargs="?", default="help", choices=list(COMMANDS.keys()))
    parser.add_argument("--api-key", dest="api_key", help="Establecer API key de Groq o MiniMax")
    parser.add_argument("--provider", default="groq", choices=["groq","minimax"], help="Provider LLM (groq o minimax)")
    args = parser.parse_args()

    if args.command == "help":
        print(f"\n🐟 BioAEGIS {VERSION} — Sistema de Gemelo Digital Biológico\n")
        print("  COMANDOS:")
        for cmd, desc in COMMANDS.items():
            print(f"    python3 bioaegis.py {cmd:<12} — {desc}")
        print("\n  EJEMPLO RÁPIDO:")
        print("    1. python3 bioaegis.py install")
        print("    2. python3 bioaegis.py start")
        print("    3. Abrir http://localhost:3001")
        print("\n  CONFIGURAR API KEY:")
        print("    python3 bioaegis.py --api-key TU_KEY --provider groq")
        print("\n  La primera ejecución descarga el proyecto automáticamente.")
        print()
    elif args.command == "install":
        if not check_env(): return
        install()
    elif args.command == "start":
        if not os.path.exists(PROJECT_DIR):
            check_env()
        install()
        start()
    elif args.command == "stop":
        stop()
    elif args.command == "status":
        status()
    elif args.command == "dashboard":
        import webbrowser
        webbrowser.open(f"http://localhost:{DASHBOARD_PORT}")
        print(f"  🌐 Abriendo http://localhost:{DASHBOARD_PORT}")
    elif args.command == "docs":
        import webbrowser
        webbrowser.open(f"http://localhost:{BACKEND_PORT}/docs")
        print(f"  📖 Abriendo http://localhost:{BACKEND_PORT}/docs")

if __name__ == "__main__":
    main()
