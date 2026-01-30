# Coding Agents System - GitHub App для автоматизации SDLC

Полностью автоматизированная система для разработки, ревью и итеративного улучшения кода на основе GitHub Issues.

## 🎯 Возможности

- ✅ **GitHub App** - устанавливается на любой репозиторий одним кликом
- 🤖 **Code Agent** - автоматически пишет код по описанию из Issue
- 👀 **Review Agent** - проводит автоматический code review
- 🔄 **Итеративный процесс** - исправляет код до полного соответствия требованиям
- 🧪 **Генерация тестов** - создает и дополняет тесты для лучшего покрытия
- 🚀 **CI/CD интеграция** - не ломает существующие проверки
- ☁️ **Облачное развертывание** - Cloud.ru / Yandex.Cloud / Docker + ngrok

## 🏗️ Архитектура

```
┌─────────────┐
│   GitHub    │
│   Issue     │
└──────┬──────┘
       │
       │ Webhook
       ▼
┌─────────────────┐
│  GitHub App     │
│   (Flask)       │
└──────┬──────────┘
       │
       │ Triggers
       ▼
┌─────────────────┐     ┌──────────────────┐
│   Code Agent    │────▶│  GitHub API      │
│   (Writes Code) │     │  (Create PR)     │
└─────────────────┘     └──────────────────┘
       │
       │ Creates PR
       ▼
┌─────────────────┐
│  GitHub Actions │
│    Workflow     │
└──────┬──────────┘
       │
       │ Runs
       ▼
┌─────────────────┐     ┌──────────────────┐
│  Review Agent   │────▶│  Post Review     │
│  (Analyzes)     │     │  Comment         │
└─────────────────┘     └──────────────────┘
       │
       │ If needs fixes
       ▼
┌─────────────────┐
│  Code Agent     │
│  (Iteration)    │
└─────────────────┘
```

## 🚀 Быстрый старт

### Локальное развертывание с Docker

```bash
# 1. Клонируйте репозиторий
git clone <your-repo>
cd coding-agents-system

# 2. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваши токены

# 3. Запустите систему
docker-compose up -d

# 4. Настройте туннелирование (в отдельном терминале)
docker-compose exec app python -m utils.tunnel
```

### Развертывание в облаке

#### Cloud.ru

```bash
# 1. Создайте виртуальную машину в Cloud.ru
# 2. Подключитесь по SSH
# 3. Установите Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Клонируйте и запустите
git clone <your-repo>
cd coding-agents-system
docker-compose up -d
```

#### Yandex.Cloud

```bash
# 1. Создайте виртуальную машину в Yandex.Cloud
# 2. Используйте образ с предустановленным Docker
# 3. Настройте группу безопасности для портов 3000, 80, 443
# 4. Запустите приложение
docker-compose up -d
```

## 🔧 Настройка GitHub App

### Шаг 1: Создание GitHub App

1. Перейдите в Settings → Developer settings → GitHub Apps → New GitHub App
2. Заполните форму:
   - **GitHub App name**: Coding Agents System
   - **Homepage URL**: `https://your-domain.com` или `https://your-ngrok-url.ngrok.io`
   - **Webhook URL**: `https://your-domain.com/webhook`
   - **Webhook secret**: Сгенерируйте секретный ключ
   
3. Настройте права доступа:
   - **Repository permissions**:
     - Contents: Read & Write
     - Issues: Read & Write
     - Pull requests: Read & Write
     - Workflows: Read & Write
     - Metadata: Read-only
   - **Subscribe to events**:
     - Issues
     - Pull request
     - Pull request review
     - Push

4. Создайте и скачайте приватный ключ (.pem файл)

### Шаг 2: Конфигурация

Создайте `.env` файл:

```env
# GitHub App Configuration
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY_PATH=/app/keys/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# LLM Configuration (выберите один)
OPENAI_API_KEY=your_openai_key
# или
YANDEX_API_KEY=your_yandex_key
YANDEX_FOLDER_ID=your_folder_id

# Tunnel (для локальной разработки)
USE_NGROK=true
NGROK_AUTH_TOKEN=your_ngrok_token

# Optional
MAX_ITERATIONS=5
LOG_LEVEL=INFO
```

### Шаг 3: Установка в репозиторий

1. Перейдите на страницу вашего GitHub App
2. Нажмите "Install App"
3. Выберите репозитории для установки
4. Готово! 🎉

## 📝 Использование

### Создание задачи

Создайте Issue в вашем репозитории с описанием задачи:

```markdown
Название: Добавить функцию расчета факториала

Описание:
Необходимо реализовать функцию `factorial(n)` которая:
- Принимает целое число n >= 0
- Возвращает факториал числа
- Обрабатывает ошибки для отрицательных чисел
- Покрыта unit-тестами
```

### Автоматический процесс

1. **Code Agent** получает Issue и создает PR с кодом
2. **GitHub Actions** запускает CI/CD и Review Agent
3. **Review Agent** анализирует код и пишет review
4. Если есть замечания, **Code Agent** делает новую итерацию
5. Процесс повторяется до успешного прохождения всех проверок
6. PR готов к слиянию ✅

## 🧪 Тестирование

```bash
# Запуск всех тестов
docker-compose exec app pytest

# Запуск с покрытием
docker-compose exec app pytest --cov=app --cov-report=html

# Проверка кода
docker-compose exec app ruff check .
docker-compose exec app black --check .
docker-compose exec app mypy .
```

## 🛠️ Структура проекта

```
coding-agents-system/
├── app/
│   ├── __init__.py
│   └── main.py              # Flask приложение (GitHub App)
├── agents/
│   ├── __init__.py
│   ├── code_agent.py        # Агент для написания кода
│   ├── review_agent.py      # Агент для ревью кода
│   └── prompts.py           # Промпты для LLM
├── github_app/
│   ├── __init__.py
│   ├── auth.py              # Аутентификация GitHub App
│   ├── webhook.py           # Обработка webhook
│   └── api.py               # Работа с GitHub API
├── utils/
│   ├── __init__.py
│   ├── llm.py               # Интеграция с LLM
│   ├── git_helper.py        # Работа с Git
│   └── tunnel.py            # Настройка ngrok
├── tests/
│   ├── test_code_agent.py
│   ├── test_review_agent.py
│   └── test_integration.py
├── .github/
│   └── workflows/
│       └── review.yml       # Workflow для Review Agent
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Безопасность

- ✅ Все секретные ключи хранятся в переменных окружения
- ✅ Webhook подписи проверяются
- ✅ GitHub App использует временные токены
- ✅ Приватный ключ монтируется как volume (не в образе)

## 📊 Мониторинг

Логи доступны через Docker:

```bash
# Все логи
docker-compose logs -f

# Только app
docker-compose logs -f app

# Последние 100 строк
docker-compose logs --tail=100 app
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License

## 🙋 Поддержка

Если возникли вопросы или проблемы, создайте Issue в этом репозитории.

## 🎓 Примеры использования

См. директорию `examples/` с примерами Issues и соответствующих Pull Requests.
