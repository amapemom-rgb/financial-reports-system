# 🧪 Testing Guide

## 📋 Overview

Проект использует **pytest** для тестирования с покрытием **>70%**.

### Типы тестов:

1. **Unit Tests** - тестируют отдельные функции
2. **Integration Tests** - тестируют взаимодействие между агентами
3. **E2E Tests** - тестируют полные workflows

---

## 🚀 Быстрый старт

### Установка зависимостей:
```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов:
```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

### Только unit тесты (быстро):
```bash
chmod +x scripts/quick_test.sh
./scripts/quick_test.sh
```

---

## 📊 Запуск тестов

### Все тесты:
```bash
pytest tests/ -v
```

### Только unit тесты:
```bash
pytest tests/unit/ -v -m unit
```

### Только integration тесты:
```bash
pytest tests/integration/ -v -m integration
```

### Только E2E тесты:
```bash
# Требует запущенные Docker сервисы
docker-compose up -d
pytest tests/e2e/ -v -m e2e
```

### С coverage:
```bash
pytest tests/ --cov=agents --cov-report=html
```

### Конкретный файл:
```bash
pytest tests/unit/test_logic_agent.py -v
```

### Конкретный тест:
```bash
pytest tests/unit/test_logic_agent.py::TestFinancialMetrics::test_calculate_roi -v
```

---

## 📈 Coverage

### Генерация отчёта:
```bash
pytest tests/ --cov=agents --cov-report=html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

### Минимальное покрытие:
Проект требует **минимум 70% coverage**. Тесты упадут, если покрытие ниже.

---

## 🎯 Структура тестов

```
tests/
├── __init__.py
├── unit/                      # Unit tests
│   ├── test_logic_agent.py
│   ├── test_visualization_agent.py
│   ├── test_report_reader.py
│   └── test_orchestrator.py
├── integration/               # Integration tests
│   └── test_agent_communication.py
└── e2e/                       # End-to-end tests
    └── test_workflows.py
```

---

## 📝 Что тестируем

### Logic Understanding Agent:
- ✅ Расчёт финансовых метрик (ROI, margin, growth)
- ✅ Анализ трендов
- ✅ API endpoints
- ✅ Error handling

### Visualization Agent:
- ✅ Создание графиков (5 типов)
- ✅ Cloud Storage integration
- ✅ Chart management
- ✅ API endpoints

### Report Reader Agent:
- ✅ Excel чтение
- ✅ Google Sheets API
- ✅ Data cleaning
- ✅ Metadata extraction

### Orchestrator Agent:
- ✅ State Machine
- ✅ Database operations
- ✅ Workflow execution
- ✅ Agent coordination

### Integration:
- ✅ Agent-to-agent communication
- ✅ Health checks

### E2E:
- ✅ Full analyze workflow
- ✅ Voice analysis workflow
- ✅ Visualization workflow

---

## 🔧 Настройка

### pytest.ini
Конфигурация pytest находится в корне проекта.

### Markers:
```python
@pytest.mark.unit        # Unit test
@pytest.mark.integration # Integration test
@pytest.mark.e2e         # E2E test
@pytest.mark.slow        # Slow test
```

### Fixtures:
```python
@pytest.fixture
def sample_data():
    return {"test": "data"}
```

---

## 🐛 Debugging

### Запуск с pdb:
```bash
pytest tests/unit/test_logic_agent.py --pdb
```

### Показать print():
```bash
pytest tests/ -s
```

### Verbose output:
```bash
pytest tests/ -vv
```

### Показать все warnings:
```bash
pytest tests/ -W all
```

---

## ⚡ CI/CD Integration

Тесты автоматически запускаются в GitHub Actions:

```yaml
- name: Run tests
  run: pytest tests/ --cov=agents --cov-fail-under=70
```

---

## 📊 Coverage Target

| Component | Target | Current |
|-----------|--------|---------|
| Logic Agent | 70% | TBD |
| Visualization | 70% | TBD |
| Report Reader | 70% | TBD |
| Orchestrator | 70% | TBD |
| **Overall** | **70%** | **TBD** |

---

## 🎯 Best Practices

1. **Один тест - одна проверка**
2. **Используй fixtures для общих данных**
3. **Mock внешние сервисы (Google APIs)**
4. **Тестируй edge cases**
5. **Пиши читаемые тесты**

### Хороший тест:
```python
def test_calculate_roi_positive_return():
    """Test ROI calculation with positive return"""
    result = calculate_roi(revenue=150, investment=100)
    assert result == 50.0
```

### Плохой тест:
```python
def test_stuff():
    x = do_thing()
    assert x
```

---

## 🚨 Common Issues

### Issue: ImportError
```bash
# Solution: Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Issue: Google API credentials
```bash
# Solution: Mock Google APIs in tests
with patch('google.cloud.storage.Client'):
    # your test
```

### Issue: Database errors
```bash
# Solution: Use in-memory SQLite for tests
engine = create_engine("sqlite:///:memory:")
```

---

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)

---

**Happy Testing! 🎉**
