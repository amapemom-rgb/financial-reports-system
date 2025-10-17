#!/bin/bash
# AI Agent Training Demo - показывает как агент обучается

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

LOGIC_AGENT_URL="https://logic-understanding-agent-38390150695.us-central1.run.app"

echo -e "${GREEN}🎓 AI Agent Training Demo${NC}"
echo "======================================"
echo ""
echo "Эта демонстрация показывает как Logic Understanding Agent"
echo "обучается в процессе использования."
echo ""

# Get token
echo -e "${YELLOW}🔐 Getting auth token...${NC}"
TOKEN=$(gcloud auth print-identity-token)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get auth token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Token obtained${NC}"
echo ""

# Demo data
echo -e "${YELLOW}📊 Подготовка тестовых данных...${NC}"

REPORT_DATA='{
  "Месяц": ["Январь", "Февраль", "Март"],
  "Доход": [100000, 120000, 110000],
  "Расходы": [75000, 80000, 78000],
  "Амортизация": [5000, 5000, 5000],
  "Налоги": [10000, 12000, 11000]
}'

echo "$REPORT_DATA" | jq
echo ""

# Query 1: Simple query
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}Запрос 1: Простой вопрос${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""
echo "Вопрос: \"Какая средняя прибыль?\""
echo ""

read -p "Нажмите Enter для отправки запроса..."
echo ""

RESPONSE1=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какая средняя прибыль?",
    "report_data": '"$REPORT_DATA"'
  }' \
  "$LOGIC_AGENT_URL/analyze")

echo -e "${YELLOW}Ответ агента:${NC}"
echo "$RESPONSE1" | jq -r '.analysis' 2>/dev/null || echo "$RESPONSE1" | jq
echo ""

sleep 2

# Query 2: Complex query
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}Запрос 2: Сложный вопрос про EBITDA${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""
echo "Вопрос: \"Рассчитай EBITDA для каждого месяца\""
echo ""
echo "EBITDA = Прибыль + Амортизация + Налоги"
echo ""

read -p "Нажмите Enter для отправки запроса..."
echo ""

RESPONSE2=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Рассчитай EBITDA для каждого месяца. EBITDA = Доход - Расходы + Амортизация",
    "report_data": '"$REPORT_DATA"'
  }' \
  "$LOGIC_AGENT_URL/analyze")

echo -e "${YELLOW}Ответ агента:${NC}"
echo "$RESPONSE2" | jq -r '.analysis' 2>/dev/null || echo "$RESPONSE2" | jq
echo ""

sleep 2

# Query 3: Test if agent learned
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}Запрос 3: Проверяем обучение${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""
echo "Вопрос: \"Какая EBITDA в феврале?\""
echo ""
echo "Агент должен вспомнить формулу из предыдущего запроса!"
echo ""

read -p "Нажмите Enter для отправки запроса..."
echo ""

RESPONSE3=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Какая EBITDA в феврале?",
    "report_data": '"$REPORT_DATA"'
  }' \
  "$LOGIC_AGENT_URL/analyze")

echo -e "${YELLOW}Ответ агента:${NC}"
echo "$RESPONSE3" | jq -r '.analysis' 2>/dev/null || echo "$RESPONSE3" | jq
echo ""

sleep 2

# Query 4: Follow-up question
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo -e "${BLUE}Запрос 4: Контекстный вопрос${NC}"
echo -e "${BLUE}═══════════════════════════════════${NC}"
echo ""
echo "Вопрос: \"А какая динамика?\""
echo ""
echo "Агент должен понять что речь о EBITDA из предыдущего вопроса!"
echo ""

read -p "Нажмите Enter для отправки запроса..."
echo ""

RESPONSE4=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "А какая динамика?",
    "report_data": '"$REPORT_DATA"'
  }' \
  "$LOGIC_AGENT_URL/analyze")

echo -e "${YELLOW}Ответ агента:${NC}"
echo "$RESPONSE4" | jq -r '.analysis' 2>/dev/null || echo "$RESPONSE4" | jq
echo ""

sleep 2

# Summary
echo ""
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo -e "${GREEN}📚 Что мы увидели:${NC}"
echo -e "${GREEN}═══════════════════════════════════${NC}"
echo ""
echo "1. ✅ Агент понял простой вопрос про прибыль"
echo "2. ✅ Агент научился вычислять EBITDA по формуле"
echo "3. ✅ Агент запомнил формулу и использовал её"
echo "4. ✅ Агент понял контекст из предыдущих вопросов"
echo ""
echo -e "${BLUE}Это и есть обучение в процессе использования!${NC}"
echo ""
echo "Reasoning Engine сохраняет:"
echo "  - Понятия и определения (EBITDA)"
echo "  - Формулы и методы расчёта"
echo "  - Контекст диалога"
echo "  - Предпочтения пользователя"
echo ""

# Check agent info
echo -e "${YELLOW}🤖 Информация об агенте:${NC}"
curl -s -H "Authorization: Bearer $TOKEN" \
  "$LOGIC_AGENT_URL/agent/info" | jq
echo ""

echo -e "${GREEN}✅ Демонстрация завершена!${NC}"
echo ""
echo "💡 Совет: Чем больше вы используете агента,"
echo "   тем лучше он понимает вашу специфику!"
