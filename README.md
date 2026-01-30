# Coding Agents System - Автоматизированная разработка на GitHub

> **Рабочая система** для автоматического написания кода, code review и итерационного улучшения на основе GitHub Issues. Развёрнута в Yandex Cloud.

## 🎯 Что система умеет

- ✅ **Автоматическое написание кода** - создаёт реализацию по описанию из Issue
- ✅ **Создание Pull Request** - автоматически коммитит и создаёт PR
- ✅ **Автоматический Code Review** - анализирует код через GitHub Actions
- ✅ **CI/CD проверки** - запускает ruff, black, mypy, pytest
- ✅ **GitHub App** - работает через webhook, устанавливается на любой репозиторий
- ✅ **Облачное развёртывание** - работает 24/7 в Yandex Cloud

## 🚀 Демонстрация работы

### Пример работающей системы

**Issue → Code Agent → Pull Request → Review Agent**

**Репозиторий для демонстрации:** https://github.com/agamilar/ai-test

### Живой пример

1. **Создаём Issue:**
   ```markdown
   Title: Create a simple Python script that prints "Hello World"
   Body: Create test7.py with hello world functionality
   ```

2. **Code Agent автоматически создаёт PR** с кодом:
   ```python
   print('Hello World')
   ```

3. **Review Agent запускается через GitHub Actions** и проверяет:
   - Качество кода (ruff, black, mypy)
   - Тесты и покрытие
   - Соответствие требованиям Issue

4. **Результат:** PR с рабочим кодом готов к мёржу ✅

## 🏗️ Архитектура

```
┌─────────────────┐
│  GitHub Issue   │
│  "Create X"     │
└────────┬────────┘
         │
         │ Webhook (POST /webhook)
         ▼
┌─────────────────────────────┐
│    GitHub App (Yandex VM)   │
│  Flask/Gunicorn на :3000    │
│  ├─ Code Agent              │
│  ├─ Webhook Handler         │
│  └─ GitHub API Integration  │
└────────┬────────────────────┘
         │
         │ 1. Анализирует Issue
         │ 2. Генерирует код (YandexGPT)
         │ 3. Создаёт branch
         │ 4. Коммитит файлы
         │ 5. Создаёт Pull Request
         ▼
┌─────────────────────────────┐
│       Pull Request          │
│  branch: issue-39-timestamp │
│  files: test7.py            │
└────────┬────────────────────┘
         │
         │ Trigger: pull_request [opened, synchronize]
         ▼
┌──────────────────────────────┐
│    GitHub Actions Workflow   │
│  (.github/workflows/review)  │
│  ├─ Code quality (ruff, etc) │
│  ├─ Tests (pytest)           │
│  └─ Review Agent             │
└────────┬─────────────────────┘
         │
         │ 1. Проверяет код
         │ 2. Анализирует через LLM
         │ 3. Пишет комментарий
         ▼
┌─────────────────────────────┐
│    Review Comment in PR     │
│  ✅ Approved / ❌ Changes   │
└─────────────────────────────┘
```

## 📋 Технический стек

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.11 |
| **LLM** | YandexGPT (yandexgpt-lite) |
| **Web Framework** | Flask + Gunicorn |
| **GitHub Integration** | PyGithub, GitHub App |
| **CI/CD** | GitHub Actions |
| **Code Quality** | ruff, black, mypy |
| **Testing** | pytest, pytest-cov |
| **Deploy** | Docker + Docker Compose |
| **Cloud** | Yandex Cloud (VM) |

## 🚀 Развёртывание

### Требования

- Python 3.11+
- Docker + Docker Compose
- GitHub App credentials
- YandexGPT API key

### Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/coding-agents-system
cd coding-agents-system

# 2. Создайте .env файл
cp .env.example .env

# 3. Отредактируйте .env (добавьте токены)
nano .env

# 4. Создайте директорию для ключей
mkdir -p keys

# 5. Скопируйте приватный ключ GitHub App
cp /path/to/your/private-key.pem keys/private-key.pem

# 6. Запустите систему
docker-compose up -d

# 7. Проверьте логи
docker-compose logs -f app
```

### Переменные окружения

```env
# GitHub App Configuration
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=/app/keys/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_INSTALLATION_ID=your_installation_id

# YandexGPT Configuration
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id
YANDEX_MODEL=yandexgpt-lite

# Optional: OpenAI или Anthropic
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Agent Configuration
CODE_AGENT_TEMPERATURE=0.3
REVIEW_AGENT_TEMPERATURE=0.2
MAX_ITERATIONS=5
MIN_TEST_COVERAGE=80

# Server Configuration
FLASK_PORT=3000
FLASK_HOST=0.0.0.0
LOG_LEVEL=INFO
```

## 🔧 Настройка GitHub App

### Шаг 1: Создание GitHub App

1. Перейдите: Settings → Developer settings → GitHub Apps → **New GitHub App**

2. Заполните форму:
   - **Name**: Coding Agents System
   - **Homepage URL**: `http://your-vm-ip:3000`
   - **Webhook URL**: `http://your-vm-ip:3000/webhook`
   - **Webhook secret**: Сгенерируйте случайную строку

3. **Repository permissions:**
   - Contents: **Read & Write**
   - Issues: **Read & Write**
   - Pull requests: **Read & Write**
   - Metadata: **Read-only**

4. **Subscribe to events:**
   - ✅ Issues
   - ✅ Pull request
   - ✅ Pull request review

5. Создайте и скачайте **Private key** (.pem файл)

### Шаг 2: Установка App в репозиторий

1. После создания App нажмите **Install App**
2. Выберите репозиторий для установки
3. Скопируйте **Installation ID** из URL

### Шаг 3: Добавьте секреты в GitHub Actions

В настройках репозитория добавьте secrets:
- `YANDEX_API_KEY`
- `YANDEX_FOLDER_ID`
- `OPENAI_API_KEY` (опционально)
- `ANTHROPIC_API_KEY` (опционально)

## 📝 Использование

### Создание Issue

Создайте Issue с описанием задачи:

```markdown
Title: Create calculator module

Body:
Create a Python module `calculator.py` with the following functions:
- add(a, b) - returns sum of a and b
- subtract(a, b) - returns difference
- multiply(a, b) - returns product
- divide(a, b) - returns quotient (handle division by zero)

Include unit tests for all functions.
```

### Что происходит дальше

1. ✅ **Code Agent получает webhook** от GitHub
2. ✅ **Анализирует Issue** через YandexGPT
3. ✅ **Генерирует код** (`calculator.py` и `test_calculator.py`)
4. ✅ **Создаёт branch** (`issue-42-20260130-120000`)
5. ✅ **Коммитит файлы** в новый branch
6. ✅ **Создаёт Pull Request**
7. ✅ **GitHub Actions запускает Review Agent**
8. ✅ **Review Agent проверяет** код и тесты
9. ✅ **Пишет review комментарий** в PR

## 🛠️ Структура проекта

```
coding-agents-system/
├── agents/
│   ├── code_agent.py       # ✅ Генерирует код по Issue
│   ├── review_agent.py     # ✅ Проводит code review
│   └── prompts.py          # ✅ Промпты для LLM
├── app/
│   └── main.py             # ✅ Flask app + webhook handler
├── github_app/
│   ├── auth.py             # ✅ GitHub App authentication
│   ├── api.py              # ✅ GitHub API helpers
│   └── webhook.py          # ✅ Webhook processing
├── utils/
│   ├── llm.py              # ✅ YandexGPT/OpenAI/Anthropic client
│   ├── git_helper.py       # Git operations
│   └── tunnel.py           # ngrok tunnel (dev)
├── .github/workflows/
│   └── review.yml          # ✅ GitHub Actions workflow
├── docker-compose.yml      # ✅ Docker setup
├── Dockerfile              # ✅ Container image
├── requirements.txt        # ✅ Python dependencies
└── .env.example            # Environment template
```

## 🧪 Тестирование

```bash
# Запуск тестов
docker-compose exec app pytest

# С покрытием
docker-compose exec app pytest --cov=. --cov-report=html

# Проверка качества кода
docker-compose exec app ruff check .
docker-compose exec app black --check .
docker-compose exec app mypy . --ignore-missing-imports
```

## 📊 Мониторинг и логи

```bash
# Просмотр логов в реальном времени
docker-compose logs -f app

# Последние 100 строк
docker-compose logs --tail=100 app

# Проверка статуса
docker-compose ps

# Перезапуск
docker-compose restart app
```

## 🎯 Что реализовано (чеклист)

### Core функциональность
- ✅ GitHub App с webhook обработкой
- ✅ Code Agent (генерирует код по Issue)
- ✅ Review Agent (анализирует PR)
- ✅ Создание Pull Request автоматически
- ✅ GitHub Actions workflow для CI/CD
- ✅ Интеграция с YandexGPT

### CI/CD
- ✅ Автоматический запуск проверок на PR
- ✅ Code quality checks (ruff, black, mypy)
- ✅ Автоматический запуск тестов (pytest)
- ✅ Coverage reporting
- ✅ AI-powered code review

### Deployment
- ✅ Docker + Docker Compose
- ✅ Развёртывание в Yandex Cloud
- ✅ Production-ready setup (Gunicorn)
- ✅ Health check endpoint

### Известные ограничения
- ⚠️ Итерационный цикл (Code Agent реагирует на Review) - частично реализован
- ⚠️ Автоматическая генерация тестов - базовая реализация
- ⚠️ Адаптация существующих тестов - требует доработки

## 🔒 Безопасность

- ✅ Приватный ключ монтируется через volume (не в образе)
- ✅ Секреты хранятся в переменных окружения
- ✅ Webhook подписи проверяются
- ✅ GitHub App токены временные (срок действия 1 час)

## 🚀 Развёртывание в Yandex Cloud

### Пошаговая инструкция

```bash
# 1. Создайте VM в Yandex Cloud
#    - OS: Ubuntu 22.04 LTS
#    - vCPU: 2, RAM: 4GB, Disk: 20GB
#    - Публичный IP: Да

# 2. Подключитесь по SSH
ssh ubuntu@<your-vm-ip>

# 3. Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 4. Установите Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 5. Клонируйте проект
git clone https://github.com/your-username/coding-agents-system
cd coding-agents-system

# 6. Настройте .env и ключи
nano .env
mkdir keys
nano keys/private-key.pem  # Вставьте содержимое .pem файла

# 7. Запустите
docker-compose up -d

# 8. Проверьте
docker-compose logs -f app
curl http://localhost:3000/health
```

### Настройка firewall в Yandex Cloud

В настройках Security Group разрешите:
- Port 3000 (webhook)
- Port 22 (SSH)

## 📖 Примеры использования

См. примеры реальной работы системы:
- Репозиторий: https://github.com/agamilar/ai-test
- Issues: https://github.com/agamilar/ai-test/issues
- Pull Requests: https://github.com/agamilar/ai-test/pulls


## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📧 Контакты

- GitHub: [@agamilar](https://github.com/agamilar)
- Issues: [Создать Issue](https://github.com/agamilar/coding-agents-system/issues)

---

**Made with ❤️ for Мегашкола Coding Agents track**

*Система полностью работает и готова к использованию. Развёрнута в production в Yandex Cloud.*
