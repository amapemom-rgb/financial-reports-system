# 🐛 Исправление Interactive Demo Script

**Дата:** 2025-10-17  
**Проблема:** Health checks в `interactive_demo.sh` показывали "connection error"  
**Статус:** ✅ Исправлено

## 🔍 Описание проблемы

### Симптомы:
При запуске `./scripts/interactive_demo.sh` опция "1. Проверить здоровье всех сервисов" показывала:
```
frontend-service: ❌ connection error
orchestrator-agent: ❌ connection error
...
```

При этом curl команды вручную работали отлично:
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" https://frontend-service-38390150695.us-central1.run.app/health
# Возвращает: {"status":"healthy"}
```

### Причины:

1. **Проблема с токеном в subshell**
   ```bash
   # Старый код (строка 67):
   response=$(curl -s -m 10 -H "Authorization: Bearer $TOKEN" "$url/health" 2>/dev/null || echo "error")
   ```
   - Переменная `$TOKEN` экспортировалась только один раз в начале
   - В subshell `$()` токен мог быть пустым или недоступным
   - Токен мог истекать во время долгой сессии

2. **Отсутствие проверки HTTP статус кода**
   - Скрипт проверял только наличие слова "healthy" в ответе
   - Не проверял HTTP код ответа (200, 401, 403, 500 и т.д.)
   - Невозможно было понять причину ошибки

3. **Слабая обработка ошибок**
   - Нет информации о том, что именно пошло не так
   - Нет способа получить детальную информацию для отладки

## ✅ Решение

### 1. Функция получения свежего токена

```bash
# Новая функция
get_token() {
    gcloud auth print-identity-token 2>/dev/null
}
```

Теперь токен можно обновлять перед каждым запросом.

### 2. Улучшенная функция проверки здоровья

```bash
check_service_health() {
    local name=$1
    local url=$2
    
    # Получаем свежий токен для этого запроса
    local token=$(get_token)
    
    echo -n "  $name: "
    
    # Захватываем и HTTP код, и ответ
    local temp_file=$(mktemp)
    local http_code=$(curl -s -w "%{http_code}" -m 10 \
        -H "Authorization: Bearer $token" \
        -o "$temp_file" \
        "$url/health" 2>/dev/null)
    
    local response=$(cat "$temp_file")
    rm -f "$temp_file"
    
    # Проверяем HTTP код
    if [ "$http_code" = "200" ]; then
        if echo "$response" | grep -q "healthy"; then
            echo -e "${GREEN}✅ healthy${NC} (HTTP $http_code)"
        else
            echo -e "${YELLOW}⚠️  responded but status unclear${NC} (HTTP $http_code)"
        fi
    elif [ -z "$http_code" ]; then
        echo -e "${RED}❌ connection error${NC} (timeout or network issue)"
    else
        echo -e "${RED}❌ unhealthy${NC} (HTTP $http_code)"
    fi
}
```

**Улучшения:**
- Свежий токен для каждого запроса
- Проверка HTTP статус кода с помощью `-w "%{http_code}"`
- Временный файл для сохранения тела ответа
- Детальный вывод с указанием HTTP кода
- Различение ошибок подключения и HTTP ошибок

### 3. Обновление токена в других операциях

Во всех остальных операциях (загрузка файла, создание задачи и т.д.) добавлено обновление токена:

```bash
# Перед каждым запросом
TOKEN=$(get_token)
curl -H "Authorization: Bearer $TOKEN" ...
```

### 4. Verbose режим для отладки

Добавлена новая опция "v" в меню:

```bash
v|V)
    if [ -z "$VERBOSE" ]; then
        export VERBOSE=1
        echo -e "${GREEN}✅ Verbose режим включен${NC}"
    else
        unset VERBOSE
        echo -e "${YELLOW}⚠️  Verbose режим выключен${NC}"
    fi
    ;;
```

В verbose режиме показываются полные ответы сервисов при ошибках.

## 🆕 Новый скрипт: test_health.sh

Создан дополнительный быстрый скрипт для проверки здоровья:

```bash
./scripts/test_health.sh         # обычный режим
./scripts/test_health.sh -v      # verbose режим
```

**Особенности:**
- Быстрая проверка всех 5 сервисов
- Exit code 0 если все healthy, 1 если есть проблемы
- Подходит для использования в CI/CD
- Поддержка verbose режима

## 📊 Результаты тестирования

### До исправления:
```
🏥 Проверка здоровья сервисов...

  frontend-service: ❌ connection error
  orchestrator-agent: ❌ connection error
  report-reader-agent: ❌ connection error
  logic-understanding-agent: ❌ connection error
  visualization-agent: ❌ connection error
```

### После исправления:
```
🏥 Проверка здоровья сервисов...

  frontend-service: ✅ healthy (HTTP 200)
  orchestrator-agent: ✅ healthy (HTTP 200)
  report-reader-agent: ✅ healthy (HTTP 200)
  logic-understanding-agent: ✅ healthy (HTTP 200)
  visualization-agent: ✅ healthy (HTTP 200)
```

## 🎯 Что было изменено

### Файлы:

1. **scripts/interactive_demo.sh** ✏️
   - Добавлена функция `get_token()`
   - Добавлена функция `check_service_health()`
   - Токен обновляется перед каждым API запросом
   - Добавлен verbose режим
   - Улучшена обработка ошибок

2. **scripts/test_health.sh** 🆕
   - Новый скрипт для быстрой проверки
   - Подходит для CI/CD

3. **docs/BUGFIX_INTERACTIVE_SCRIPT.md** 📝
   - Этот документ с описанием проблемы и решения

## 💡 Уроки

### Что узнали:

1. **Bash subshells и переменные окружения**
   - Переменные в `$()` могут не видеть export из родительского shell
   - Лучше передавать в функции или обновлять перед использованием

2. **GCP Identity Tokens**
   - Токены могут истекать
   - Для долгих interactive сессий нужно обновлять токен
   - `gcloud auth print-identity-token` быстрая операция (~0.1s)

3. **Отладка bash скриптов**
   - Всегда проверяйте HTTP статус коды
   - Используйте временные файлы для сохранения тела ответа
   - Добавляйте verbose режимы для детальной информации

4. **curl best practices**
   - Используйте `-w "%{http_code}"` для получения статус кода
   - Используйте `-o` для разделения тела ответа и статус кода
   - Обрабатывайте timeouts отдельно от HTTP ошибок

## 🚀 Как использовать исправленный скрипт

### Основное использование:

```bash
cd /Users/sergejbykov/financial-reports-system

# Запустить интерактивное меню
./scripts/interactive_demo.sh

# Или быстро проверить здоровье
./scripts/test_health.sh
```

### С verbose для отладки:

```bash
# Запустить interactive demo
./scripts/interactive_demo.sh

# В меню выбрать: v (включить verbose)
# Затем выбрать: 1 (проверить здоровье)

# Или с test_health.sh
./scripts/test_health.sh -v
```

## ✅ Проверочный чек-лист

- [x] Скрипт успешно запускается
- [x] Health checks показывают "healthy" для всех сервисов
- [x] Токен обновляется корректно
- [x] HTTP статус коды показываются
- [x] Verbose режим работает
- [x] test_health.sh создан и работает
- [x] Документация обновлена

## 🔗 Связанные файлы

- `scripts/interactive_demo.sh` - основной интерактивный скрипт
- `scripts/test_health.sh` - быстрая проверка здоровья
- `STATUS.md` - обновлён со статусом исправления
- `USER_GUIDE.md` - руководство пользователя

## 📝 Коммиты

1. `05ae514` - Fix: Исправлен health check в interactive_demo.sh
2. `73f1705` - Add: Быстрый скрипт проверки здоровья сервисов
3. (текущий) - Docs: Документация исправления interactive script

---

**Проблема полностью решена! Система готова к использованию.** ✅
