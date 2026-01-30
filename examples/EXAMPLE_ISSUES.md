# Примеры Issues для тестирования Coding Agents System

## Пример 1: Простая функция

**Название:** Add factorial function

**Описание:**
```markdown
Необходимо реализовать функцию для вычисления факториала числа.

## Требования:
- Создать файл `math_utils.py` в директории `src/`
- Функция `factorial(n: int) -> int`
- Принимает неотрицательное целое число
- Возвращает факториал числа
- Обрабатывает ошибки для отрицательных чисел (raise ValueError)
- Покрыта unit-тестами с coverage >= 90%

## Примеры:
- factorial(0) → 1
- factorial(5) → 120
- factorial(-1) → ValueError
```

## Пример 2: CRUD API

**Название:** Implement User CRUD endpoints

**Описание:**
```markdown
Реализовать REST API для управления пользователями.

## Требования:

### Модель
- Создать файл `models/user.py`
- Класс `User` с полями:
  - id: int
  - username: str (уникальный, не пустой)
  - email: str (валидный email)
  - created_at: datetime

### API Endpoints
- Создать файл `api/users.py`
- GET /api/users - список всех пользователей
- GET /api/users/{id} - получить пользователя по ID
- POST /api/users - создать пользователя
- PUT /api/users/{id} - обновить пользователя
- DELETE /api/users/{id} - удалить пользователя

### Валидация
- Email должен быть валидным
- Username должен быть уникальным
- Все поля обязательны при создании

### Тесты
- Unit-тесты для модели
- Integration-тесты для API endpoints
- Coverage >= 85%

### Технологии
- FastAPI
- Pydantic для валидации
- SQLite для хранения (in-memory для тестов)
```

## Пример 3: Утилиты для работы с файлами

**Название:** Create file processing utilities

**Описание:**
```markdown
Создать набор утилит для работы с файлами.

## Требования:

### Файл: `utils/file_utils.py`

Функции:
1. `read_json(filepath: str) -> dict`
   - Читает JSON файл
   - Обрабатывает ошибки (FileNotFoundError, JSONDecodeError)

2. `write_json(filepath: str, data: dict) -> bool`
   - Записывает данные в JSON файл
   - Создает директории если нужно
   - Возвращает True при успехе

3. `read_csv(filepath: str) -> List[dict]`
   - Читает CSV файл
   - Возвращает список словарей
   - Первая строка - заголовки

4. `write_csv(filepath: str, data: List[dict]) -> bool`
   - Записывает список словарей в CSV
   - Автоматически определяет заголовки

### Требования к коду:
- Использовать type hints
- Docstrings для всех функций
- Обработка всех возможных ошибок
- Логирование операций

### Тесты:
- Тесты для каждой функции
- Тесты для edge cases
- Тесты для обработки ошибок
- Coverage >= 95%
```

## Пример 4: Исправление бага

**Название:** Fix division by zero in calculator

**Описание:**
```markdown
В файле `calculator.py` есть баг - отсутствует проверка деления на ноль.

## Текущий код:
```python
def divide(a: float, b: float) -> float:
    return a / b
```

## Требования:
1. Добавить проверку деления на ноль
2. Выбрасывать `ValueError` с понятным сообщением
3. Добавить тесты для проверки:
   - Нормальное деление
   - Деление на ноль
   - Деление отрицательных чисел
   - Деление float чисел

## Ожидаемое поведение:
```python
divide(10, 2)  # → 5.0
divide(10, 0)  # → ValueError: Division by zero
```
```

## Пример 5: Рефакторинг

**Название:** Refactor authentication module

**Описание:**
```markdown
Провести рефакторинг модуля аутентификации для улучшения читаемости и тестируемости.

## Текущие проблемы:
- Один большой класс `AuthManager` с 500+ строками
- Отсутствуют type hints
- Нет docstrings
- Дублирование кода
- Низкая тестируемость

## Требования:

### Архитектура:
Разделить `auth/manager.py` на:
- `auth/password.py` - работа с паролями (hashing, validation)
- `auth/token.py` - генерация и валидация токенов
- `auth/user.py` - управление пользователями
- `auth/session.py` - управление сессиями

### Улучшения:
- Добавить type hints везде
- Добавить docstrings (Google style)
- Использовать dependency injection
- Выделить интерфейсы
- Применить паттерн Strategy для разных методов аутентификации

### Тесты:
- Покрыть тестами весь новый код
- Mock внешние зависимости
- Coverage >= 90%

### Совместимость:
- Сохранить обратную совместимость API
- Добавить deprecation warnings для старых методов
```

## Пример 6: Документация

**Название:** Add comprehensive documentation

**Описание:**
```markdown
Добавить документацию для проекта.

## Требования:

### README.md
- Описание проекта
- Quick start guide
- Installation instructions
- Basic usage examples
- Link to full documentation

### docs/
Создать структуру документации:
- docs/getting-started.md
- docs/api-reference.md
- docs/examples.md
- docs/contributing.md
- docs/changelog.md

### Code documentation
- Docstrings для всех публичных функций/классов
- Примеры использования в docstrings
- Type hints везде

### API docs
- Использовать Sphinx для генерации HTML документации
- Настроить autodoc для автоматической генерации из docstrings
```

## Как использовать эти примеры

1. Скопируйте название и описание Issue
2. Создайте новый Issue в вашем репозитории
3. Дождитесь, пока Code Agent создаст PR
4. Review Agent автоматически проверит код
5. Если нужны правки, Code Agent сделает новую итерацию

## Советы по написанию Issues

### ✅ Хорошие практики:
- Четкие и конкретные требования
- Примеры входных/выходных данных
- Указание требований к тестам
- Упоминание edge cases
- Указание технологий/библиотек

### ❌ Чего избегать:
- Расплывчатых формулировок ("сделать лучше")
- Отсутствия критериев приемки
- Слишком больших задач (разбивайте на части)
- Противоречивых требований
