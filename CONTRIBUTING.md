# Contributing to Coding Agents System

Спасибо за интерес к улучшению Coding Agents System! 🎉

## Как внести вклад

### Сообщение об ошибках

Если вы нашли баг:

1. Проверьте, нет ли уже такого Issue
2. Создайте новый Issue с описанием:
   - Шаги для воспроизведения
   - Ожидаемое поведение
   - Фактическое поведение
   - Версия системы
   - Логи (если есть)

### Предложение улучшений

1. Создайте Issue с описанием улучшения
2. Опишите use case
3. Предложите возможное решение

### Pull Requests

1. Fork репозиторий
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Внесите изменения
4. Добавьте тесты
5. Убедитесь, что тесты проходят: `pytest`
6. Проверьте code style: `ruff check . && black --check .`
7. Закоммитьте: `git commit -m 'Add amazing feature'`
8. Запушьте: `git push origin feature/amazing-feature`
9. Откройте Pull Request

## Стандарты кода

### Python

- Следуйте PEP 8
- Используйте type hints
- Пишите docstrings (Google style)
- Покрывайте код тестами (coverage >= 80%)

### Git

Формат commit messages:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: Новая функциональность
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование кода
- `refactor`: Рефакторинг
- `test`: Добавление тестов
- `chore`: Обновление зависимостей, конфигов

Пример:
```
feat: Add support for Claude API

Add Anthropic Claude as LLM provider option.
Users can now use Claude API by setting ANTHROPIC_API_KEY.

Closes #123
```

## Code Review Process

1. Автоматические проверки должны пройти
2. Минимум один approve от мейнтейнеров
3. Все комментарии должны быть разрешены

## Вопросы?

Создайте Issue с меткой `question` или напишите в Discussions.

Спасибо за ваш вклад! 🚀
