#!/bin/bash
# BioAEGIS — Instalador en una línea
# Uso: curl -fsSL https://raw.githubusercontent.com/fernandofondillo/BIOAEGIS/main/install.sh | bash
set -e
BOLD='\033[1m'; CYAN='\033[96m'; GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; RESET='\033[0m'
echo ""; echo -e "${BOLD}🐟 BioAEGIS 1.0 — Instalador automático${RESET}"; echo ""
OS=$(uname -s)
[[ "$OS" == "Darwin" ]] && echoc() { echo -e "$1$2${RESET}"; } || echoc() { echo "$2"; }
BIOAEGIS="$HOME/BIOAEGIS"
if [[ ! -d "$BIOAEGIS/.git" ]]; then
  echoc "${CYAN}  ℹ  Descargando BioAEGIS desde GitHub...${RESET}"
  git clone --quiet https://github.com/fernandofondillo/BIOAEGIS.git "$BIOAEGIS"
  echoc "${GREEN}  ✅ Proyecto descargado en ~/BIOAEGIS${RESET}"
else
  echoc "${YELLOW}  ℹ  Proyecto ya existe — actualizando...${RESET}"
  git -C "$BIOAEGIS" pull --quiet 2>/dev/null || true
fi
cd "$BIOAEGIS"
echoc "${CYAN}  ℹ  Instalando dependencias Python...${RESET}"
pip3 install --break-system-packages -q fastapi "uvicorn[standard]" loguru pydantic httpx 2>/dev/null || \
pip3 install -q fastapi "uvicorn[standard]" loguru pydantic httpx 2>/dev/null || \
python3 -m pip install --user -q fastapi "uvicorn[standard]" loguru pydantic httpx 2>/dev/null || true
echoc "${GREEN}  ✅ Dependencias Python listas${RESET}"
if [[ ! -d "$BIOAEGIS/frontend/bioaegis-dashboard/dist" ]]; then
  echoc "${CYAN}  ℹ  Construyendo dashboard...${RESET}"
  cd "$BIOAEGIS/frontend/bioaegis-dashboard"
  npm install --silent 2>/dev/null
  npm run build 2>/dev/null
  cd "$BIOAEGIS"
  echoc "${GREEN}  ✅ Dashboard construido${RESET}"
fi
mkdir -p "$HOME/.fenix"
if [[ ! -f "$HOME/.fenix/providers.toml" ]]; then
  cat > "$HOME/.fenix/providers.toml" << 'EOF'
# BioAEGIS — Configura tu API key aquí
# Groq:      GROQ_API_KEY=tu_key_de_groq
# MiniMax:   MINIMAX_API_KEY=tu_key_de_minimax
GROQ_API_KEY=PEGA_TU_KEY_AQUI
EOF
  echoc "${GREEN}  ✅ Archivo ~/.fenix/providers.toml creado${RESET}"
fi
mkdir -p "$HOME/BIOAEGIS/backend"
cd "$BIOAEGIS/backend"
nohup python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/bioaegis_backend.log 2>&1 &
sleep 3
cd "$BIOAEGIS/frontend/bioaegis-dashboard/dist"
nohup python3 -m http.server 3001 > /tmp/bioaegis_dashboard.log 2>&1 &
sleep 1
echo ""; echo -e "${BOLD}🐟 BioAEGIS — ¡Arrancado!${RESET}"; echo ""
echoc "${CYAN}  🌐 Dashboard:  http://localhost:3001${RESET}"
echoc "${CYAN}  📖 API Docs:   http://localhost:8000/docs${RESET}"
echo ""
echoc "${YELLOW}  ⚠  Para configurar tu API key: nano ~/.fenix/providers.toml${RESET}"
echoc "${YELLOW}  ⚠  Después reinicia: pkill -f uvicorn && cd ~/BIOAEGIS/backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &${RESET}"
echo ""
