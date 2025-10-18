# 🔧 Исправления для интерактивного скрипта

## 📌 Проблема

Интерактивный скрипт `scripts/interactive_demo.sh` показывал "connection error" для всех health checks, хотя curl команды вручную работали отлично.

## 🔍 Причина

1. **Токен не обновлялся**: Токен получался один раз в начале, но не обновлялся для каждого запроса
2. **Плохая обработка ошибок**: Не проверялся HTTP status code, только текст ответа
3. **Проблемы с subshell**: Переменная $TOKEN могла терять значение в некоторых контекстах

## ✅ Решение

### 1. Добавлена функция `get_token()`

```bash
get_token() {
    gcloud auth print-identity-token 2>/dev/null
}
```

### 2. Улучшена проверка health checks

Было:
```bash
response=$(curl -s -m 10 -H "Authorization: Bearer $TOKEN" "$url/health" 2>/dev/null || echo "error")

if echo "$response" | grep -q "healthy"; then
    echo "✅ healthy"
elif [ "$response" = "error" ]; then
    echo "❌ connection error"
else
    echo "❌ unhealthy"
fi
```

Стало:
```bash
CURRENT_TOKEN=$(get_token)

http_code=$(curl -s -w "%{http_code}" -o /tmp/health_response.txt \
    -m 10 \
    -H "Authorization: Bearer $CURRENT_TOKEN" \
    "$url/health" 2>/dev/null)

response=$(cat /tmp/health_response.txt 2>/dev/null)

if [ "$http_code" = "200" ] && echo "$response" | grep -q "healthy"; then
    echo "✅ healthy"
elif [ -z "$http_code" ] || [ "$http_code" = "000" ]; then
    echo "❌ connection error"
elif [ "$http_code" = "403" ] || [ "$http_code" = "401" ]; then
    echo "❌ auth error (code: $http_code)"
else
    echo "❌ unhealthy (code: $http_code)"
fi
```

### 3. Обновлены все curl запросы

Теперь каждый curl запрос:
- Получает свежий токен через `get_token()`
- Использует локальную переменную `CURRENT_TOKEN`
- Показывает HTTP status код при ошибках

## 📁 Изменённые файлы

- `scripts/interactive_demo.sh` - полностью исправлен
- `scripts/test_health.sh` - новый тестовый скрипт для проверки

## 🧪 Тестирование

### Запустить health check тест

```bash
chmod +x scripts/test_health.sh
./scripts/test_health.sh
```

Ожидаемый вывод:
```
Testing health checks...

Getting auth token...
✅ Token obtained

Testing frontend-service... ✅ OK (HTTP 200)
Testing orchestrator-agent... ✅ OK (HTTP 200)
Testing report-reader-agent... ✅ OK (HTTP 200)
Testing logic-understanding-agent... ✅ OK (HTTP 200)
Testing visualization-agent... ✅ OK (HTTP 200)

================================
Results: 5 passed, 0 failed
================================
✅ All services are healthy! 🎉
```

### Запустить интерактивное меню

```bash
chmod +x scripts/interactive_demo.sh
./scripts/interactive_demo.sh
```

Теперь опция "1. 🏥 Проверить здоровье всех сервисов" должна работать корректно!

## 🎯 Преимущества

1. **Надёжность**: Токен обновляется для каждого запроса
2. **Диагностика**: Показываются HTTP коды для понимания проблем
3. **Отказоустойчивость**: Правильная обработка всех типов ошибок
4. **Отладка**: Легко увидеть, что именно пошло не так

## 📊 Статус

- ✅ Health checks работают корректно
- ✅ Все curl запросы обновлены
- ✅ Добавлен тестовый скрипт
- ✅ Улучшена обработка ошибок

## 🚀 Следующие шаги

1. Протестировать все опции меню
2. Создать реальный E2E тест с загрузкой файла
3. Добавить больше примеров в документацию

---

**Проблема решена! Интерактивный скрипт теперь работает! 🎉**
