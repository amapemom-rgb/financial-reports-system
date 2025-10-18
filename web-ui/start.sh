#!/bin/bash
# Quick start script for Web UI

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Financial Reports Analysis System - Web UI           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "web-ui/index.html" ]; then
    echo -e "${YELLOW}Переходим в директорию проекта...${NC}"
    cd "$(dirname "$0")/.."
fi

# Make serve.py executable
chmod +x web-ui/serve.py

echo -e "${GREEN}🚀 Запуск веб-интерфейса...${NC}"
echo ""
echo -e "${YELLOW}📝 Инструкция:${NC}"
echo "1. Сейчас откроется браузер с интерфейсом"
echo "2. В другом терминале выполни: gcloud auth print-identity-token"
echo "3. Скопируй токен и вставь в интерфейс"
echo "4. Начни работу!"
echo ""
echo -e "${BLUE}🌐 URL: http://localhost:8000${NC}"
echo ""

# Start server
cd web-ui
python3 serve.py &
SERVER_PID=$!

# Wait a bit for server to start
sleep 2

# Open browser
if command -v open &> /dev/null; then
    open http://localhost:8000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
fi

echo ""
echo -e "${GREEN}✅ Сервер запущен!${NC}"
echo -e "${YELLOW}🛑 Для остановки нажми Ctrl+C${NC}"
echo ""

# Wait for Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo -e '${GREEN}✅ Сервер остановлен${NC}'; exit 0" INT

wait $SERVER_PID
