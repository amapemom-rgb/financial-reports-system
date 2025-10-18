#!/bin/bash
# Quick Start Script - Interactive menu for testing the system

# Don't exit on errors in interactive mode
set +e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# URLs
FRONTEND_URL="https://frontend-service-38390150695.us-central1.run.app"
ORCHESTRATOR_URL="https://orchestrator-agent-38390150695.us-central1.run.app"
REPORT_READER_URL="https://report-reader-agent-38390150695.us-central1.run.app"
LOGIC_AGENT_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"
VISUALIZATION_URL="https://visualization-agent-38390150695.us-central1.run.app"

echo -e "${GREEN}🚀 Financial Reports System - Quick Start${NC}"
echo "=========================================="
echo ""

# Function to get fresh token
get_token() {
    gcloud auth print-identity-token 2>/dev/null
}

# Initial token check
echo -e "${YELLOW}🔐 Getting auth token...${NC}"
TOKEN=$(get_token)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get auth token. Make sure you're logged in with gcloud.${NC}"
    echo ""
    echo "Try running:"
    echo "  gcloud auth login"
    exit 1
fi

echo -e "${GREEN}✅ Token obtained${NC}"
echo ""

# Function to check service health
check_service_health() {
    local name=$1
    local url=$2
    
    # Get fresh token for this request
    local token=$(get_token)
    
    echo -n "  $name: "
    
    # Make request and capture both response and HTTP code
    local temp_file=$(mktemp)
    local http_code=$(curl -s -w "%{http_code}" -m 10 \
        -H "Authorization: Bearer $token" \
        -o "$temp_file" \
        "$url/health" 2>/dev/null)
    
    local response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    # Check HTTP code first
    if [ "$http_code" = "200" ]; then
        # Check if response contains "healthy"
        if echo "$response" | grep -q "healthy"; then
            echo -e "${GREEN}✅ healthy${NC} (HTTP $http_code)"
        else
            echo -e "${YELLOW}⚠️  responded but status unclear${NC} (HTTP $http_code)"
            if [ -n "$VERBOSE" ]; then
                echo "     Response: $response"
            fi
        fi
    elif [ -z "$http_code" ]; then
        echo -e "${RED}❌ connection error${NC} (timeout or network issue)"
    else
        echo -e "${RED}❌ unhealthy${NC} (HTTP $http_code)"
        if [ -n "$VERBOSE" ]; then
            echo "     Response: $response"
        fi
    fi
}

# Menu
while true; do
    echo -e "${BLUE}═══════════════════════════════════${NC}"
    echo -e "${BLUE}    Выберите действие:${NC}"
    echo -e "${BLUE}═══════════════════════════════════${NC}"
    echo ""
    echo "  1. 🏥 Проверить здоровье всех сервисов"
    echo "  2. 📊 Создать тестовый CSV файл"
    echo "  3. 📤 Загрузить файл и запустить анализ"
    echo "  4. 📈 Создать визуализацию"
    echo "  5. 📋 Посмотреть все задачи"
    echo "  6. 🔍 Проверить статус задачи"
    echo "  7. 🎤 Голосовой анализ (demo)"
    echo "  8. 🤖 Информация об AI агенте"
    echo "  9. 📚 Открыть руководство"
    echo "  v. 🔧 Включить/выключить verbose режим"
    echo "  0. ❌ Выход"
    echo ""
    read -p "Введите номер (0-9, v): " choice
    echo ""

    case $choice in
        1)
            echo -e "${YELLOW}🏥 Проверка здоровья сервисов...${NC}"
            echo ""
            
            # Check each service
            check_service_health "frontend-service" "$FRONTEND_URL"
            check_service_health "orchestrator-agent" "$ORCHESTRATOR_URL"
            check_service_health "report-reader-agent" "$REPORT_READER_URL"
            check_service_health "logic-understanding-agent" "$LOGIC_AGENT_URL"
            check_service_health "visualization-agent" "$VISUALIZATION_URL"
            
            echo ""
            ;;
            
        2)
            echo -e "${YELLOW}📊 Создание тестового CSV файла...${NC}"
            
            cat > /tmp/financial_report_test.csv << 'EOF'
Месяц,Доход,Расходы,Прибыль
Январь,100000,75000,25000
Февраль,120000,80000,40000
Март,110000,78000,32000
Апрель,130000,85000,45000
Май,125000,82000,43000
Июнь,140000,90000,50000
EOF
            
            echo -e "${GREEN}✅ Файл создан: /tmp/financial_report_test.csv${NC}"
            echo ""
            echo "Содержимое:"
            cat /tmp/financial_report_test.csv
            echo ""
            ;;
            
        3)
            if [ ! -f /tmp/financial_report_test.csv ]; then
                echo -e "${YELLOW}⚠️  Сначала создайте тестовый файл (опция 2)${NC}"
                echo ""
                continue
            fi
            
            # Get fresh token
            TOKEN=$(get_token)
            
            echo -e "${YELLOW}📤 Загрузка файла...${NC}"
            
            upload_response=$(curl -s -X POST \
                -H "Authorization: Bearer $TOKEN" \
                -F "file=@/tmp/financial_report_test.csv" \
                "$FRONTEND_URL/upload")
            
            echo "$upload_response" | jq
            
            file_id=$(echo "$upload_response" | jq -r '.file_id')
            
            if [ "$file_id" != "null" ] && [ -n "$file_id" ]; then
                echo ""
                echo -e "${YELLOW}🤖 Создание задачи на анализ...${NC}"
                
                task_response=$(curl -s -X POST \
                    -H "Authorization: Bearer $TOKEN" \
                    -H "Content-Type: application/json" \
                    -d '{
                        "workflow_type": "analyze_report",
                        "input_data": {
                            "file_path": "'$file_id'",
                            "query": "Проанализируй финансовый отчёт. Какая динамика доходов и расходов? Есть ли тренды?"
                        }
                    }' \
                    "$ORCHESTRATOR_URL/tasks")
                
                echo "$task_response" | jq
                
                task_id=$(echo "$task_response" | jq -r '.task_id')
                
                if [ "$task_id" != "null" ] && [ -n "$task_id" ]; then
                    echo ""
                    echo -e "${GREEN}✅ Задача создана: $task_id${NC}"
                    echo ""
                    echo -e "${YELLOW}⏳ Ожидание выполнения (10 секунд)...${NC}"
                    sleep 10
                    
                    echo ""
                    echo -e "${YELLOW}📊 Проверка статуса...${NC}"
                    
                    # Get fresh token for status check
                    TOKEN=$(get_token)
                    curl -s -H "Authorization: Bearer $TOKEN" \
                        "$ORCHESTRATOR_URL/tasks/$task_id" | jq
                fi
            else
                echo -e "${RED}❌ Не удалось получить file_id из ответа${NC}"
            fi
            echo ""
            ;;
            
        4)
            echo -e "${YELLOW}📈 Создание визуализации...${NC}"
            echo ""
            
            # Get fresh token
            TOKEN=$(get_token)
            
            viz_response=$(curl -s -X POST \
                -H "Authorization: Bearer $TOKEN" \
                -H "Content-Type: application/json" \
                -d '{
                    "chart_type": "line",
                    "data": {
                        "x": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь"],
                        "y": [25000, 40000, 32000, 45000, 43000, 50000]
                    },
                    "title": "Динамика прибыли",
                    "x_label": "Месяц",
                    "y_label": "Прибыль (руб)"
                }' \
                "$VISUALIZATION_URL/create")
            
            echo "$viz_response" | jq
            
            chart_url=$(echo "$viz_response" | jq -r '.chart_url')
            
            if [ "$chart_url" != "null" ] && [ -n "$chart_url" ]; then
                echo ""
                echo -e "${GREEN}✅ График создан!${NC}"
                echo -e "${BLUE}URL: $chart_url${NC}"
                echo ""
                read -p "Открыть график в браузере? (y/n): " open_chart
                
                if [ "$open_chart" == "y" ]; then
                    open "$chart_url" 2>/dev/null || xdg-open "$chart_url" 2>/dev/null
                fi
            fi
            echo ""
            ;;
            
        5)
            echo -e "${YELLOW}📋 Все задачи:${NC}"
            echo ""
            
            # Get fresh token
            TOKEN=$(get_token)
            
            curl -s -H "Authorization: Bearer $TOKEN" \
                "$ORCHESTRATOR_URL/tasks?limit=10" | jq
            echo ""
            ;;
            
        6)
            echo -e "${YELLOW}🔍 Проверка статуса задачи${NC}"
            echo ""
            read -p "Введите task_id: " task_id
            
            if [ -n "$task_id" ]; then
                echo ""
                
                # Get fresh token
                TOKEN=$(get_token)
                
                curl -s -H "Authorization: Bearer $TOKEN" \
                    "$ORCHESTRATOR_URL/tasks/$task_id" | jq
            fi
            echo ""
            ;;
            
        7)
            echo -e "${YELLOW}🎤 Голосовой анализ (demo)${NC}"
            echo ""
            echo -e "${BLUE}Для голосового анализа нужен аудио файл.${NC}"
            echo ""
            echo "Пример команды:"
            echo ""
            echo 'TOKEN=$(gcloud auth print-identity-token)'
            echo 'curl -X POST \'
            echo '  -H "Authorization: Bearer $TOKEN" \'
            echo '  -F "audio=@/path/to/audio.wav" \'
            echo '  -F "report_id=reports/filename.csv" \'
            echo '  "'$FRONTEND_URL'/voice/analyze"'
            echo ""
            echo "📝 Инструкция:"
            echo "1. Запиши аудио вопрос (WAV, MP3, FLAC)"
            echo "2. Загрузи файл отчёта (опция 3)"
            echo "3. Используй команду выше с правильными путями"
            echo ""
            ;;
            
        8)
            echo -e "${YELLOW}🤖 Информация об AI агенте${NC}"
            echo ""
            
            # Get fresh token
            TOKEN=$(get_token)
            
            curl -s -H "Authorization: Bearer $TOKEN" \
                "$LOGIC_AGENT_URL/agent/info" | jq
            echo ""
            ;;
            
        9)
            echo -e "${YELLOW}📚 Открытие руководства...${NC}"
            
            if [ -f USER_GUIDE.md ]; then
                open USER_GUIDE.md 2>/dev/null || xdg-open USER_GUIDE.md 2>/dev/null
                echo -e "${GREEN}✅ Руководство открыто${NC}"
            else
                echo -e "${RED}❌ Файл USER_GUIDE.md не найден в текущей директории${NC}"
                echo ""
                echo "Документация доступна онлайн:"
                echo "https://github.com/amapemom-rgb/financial-reports-system"
            fi
            echo ""
            ;;
            
        v|V)
            if [ -z "$VERBOSE" ]; then
                export VERBOSE=1
                echo -e "${GREEN}✅ Verbose режим включен${NC}"
            else
                unset VERBOSE
                echo -e "${YELLOW}⚠️  Verbose режим выключен${NC}"
            fi
            echo ""
            ;;
            
        0)
            echo -e "${GREEN}👋 До свидания!${NC}"
            exit 0
            ;;
            
        *)
            echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
            echo ""
            ;;
    esac
done
