# Руководство по развертыванию Coding Agents System

Это подробное руководство поможет вам развернуть систему локально, в облаке или через Docker.

## Оглавление

1. [Предварительные требования](#предварительные-требования)
2. [Настройка GitHub App](#настройка-github-app)
3. [Локальное развертывание](#локальное-развертывание)
4. [Развертывание в Docker](#развертывание-в-docker)
5. [Развертывание в Cloud.ru](#развертывание-в-cloudru)
6. [Развертывание в Yandex Cloud](#развертывание-в-yandex-cloud)
7. [Настройка туннеля](#настройка-туннеля)
8. [Проверка работоспособности](#проверка-работоспособности)

## Предварительные требования

### Для локального развертывания:
- Python 3.11 или выше
- Git
- Аккаунт GitHub
- API ключ для LLM (OpenAI, Anthropic или Yandex)

### Для Docker:
- Docker и Docker Compose
- 2GB+ свободного места на диске

### Для облачного развертывания:
- Виртуальная машина с Ubuntu 20.04+
- 2GB+ RAM
- Доступ по SSH

## Настройка GitHub App

### Шаг 1: Создание GitHub App

1. Перейдите в настройки вашего аккаунта/организации GitHub:
   ```
   https://github.com/settings/apps
   ```

2. Нажмите "New GitHub App"

3. Заполните форму:
   - **GitHub App name**: `coding-agents-[ваше-имя]` (должно быть уникальным)
   - **Homepage URL**: `https://your-domain.com` (или временно `http://localhost:3000`)
   - **Webhook URL**: `https://your-domain.com/webhook` (обновите позже)
   - **Webhook secret**: Сгенерируйте случайную строку:
     ```bash
     openssl rand -hex 32
     ```

### Шаг 2: Настройка разрешений

Установите следующие **Repository permissions**:

| Permission | Access |
|------------|--------|
| Contents | Read & Write |
| Issues | Read & Write |
| Pull requests | Read & Write |
| Workflows | Read & Write |
| Metadata | Read-only |

### Шаг 3: Подписка на события

Включите следующие события:

- ✅ Issues
- ✅ Pull request
- ✅ Pull request review

### Шаг 4: Создание и сохранение ключа

1. После создания приложения, прокрутите вниз до раздела "Private keys"
2. Нажмите "Generate a private key"
3. Сохраните скачанный `.pem` файл в безопасном месте
4. Скопируйте **App ID** (отображается вверху страницы)

## Локальное развертывание

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/your-username/coding-agents-system.git
cd coding-agents-system
```

### Шаг 2: Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
# GitHub App
GITHUB_APP_ID=123456  # Ваш App ID
GITHUB_APP_PRIVATE_KEY_PATH=./keys/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# LLM (выберите один)
OPENAI_API_KEY=sk-...

# Tunnel для локальной разработки
USE_NGROK=true
NGROK_AUTH_TOKEN=your_ngrok_token
```

### Шаг 5: Размещение приватного ключа

```bash
mkdir -p keys
cp /path/to/downloaded/private-key.pem keys/private-key.pem
chmod 600 keys/private-key.pem
```

### Шаг 6: Запуск приложения

```bash
python app/main.py
```

Приложение запустится на `http://localhost:3000`

### Шаг 7: Настройка туннеля (для локальной разработки)

Если `USE_NGROK=true`, туннель запустится автоматически. Скопируйте публичный URL из логов:

```
INFO - Ngrok tunnel active at: https://abc123.ngrok.io
```

Обновите Webhook URL в настройках GitHub App на этот URL + `/webhook`

## Развертывание в Docker

### Шаг 1: Подготовка

```bash
# Создайте директорию для ключа
mkdir -p keys

# Скопируйте приватный ключ
cp /path/to/private-key.pem keys/private-key.pem

# Создайте .env файл
cp .env.example .env
# Отредактируйте .env
```

### Шаг 2: Сборка и запуск

```bash
docker-compose up -d
```

### Шаг 3: Проверка логов

```bash
docker-compose logs -f app
```

### Шаг 4: С ngrok (опционально)

Для запуска с ngrok туннелем:

```bash
docker-compose --profile ngrok up -d
```

Ngrok dashboard будет доступен на `http://localhost:4040`

### Управление контейнерами

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр статуса
docker-compose ps
```

## Развертывание в Cloud.ru

### Шаг 1: Создание виртуальной машины

1. Зарегистрируйтесь на https://cloud.ru
2. Активируйте бесплатный период
3. Создайте виртуальную машину:
   - OS: Ubuntu 22.04
   - RAM: 2GB+
   - Disk: 10GB+
   - Откройте порты: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3000

### Шаг 2: Подключение по SSH

```bash
ssh root@your-vm-ip
```

### Шаг 3: Установка Docker

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
apt install docker-compose -y
```

### Шаг 4: Клонирование проекта

```bash
git clone https://github.com/your-username/coding-agents-system.git
cd coding-agents-system
```

### Шаг 5: Настройка

```bash
# Создайте .env
nano .env
# Вставьте конфигурацию

# Создайте директорию для ключа
mkdir -p keys

# Скопируйте приватный ключ
# Можно использовать scp с локальной машины:
# scp private-key.pem root@your-vm-ip:/root/coding-agents-system/keys/
```

### Шаг 6: Запуск

```bash
docker-compose up -d
```

### Шаг 7: Настройка домена (опционально)

Если у вас есть домен:

1. Добавьте A-запись, указывающую на IP вашей VM
2. Установите Nginx и SSL сертификат:

```bash
apt install nginx certbot python3-certbot-nginx -y

# Настройте Nginx для проксирования на порт 3000
nano /etc/nginx/sites-available/coding-agents

# Получите SSL сертификат
certbot --nginx -d your-domain.com
```

## Развертывание в Yandex Cloud

### Шаг 1: Создание VM

1. Перейдите на https://console.yandex.cloud
2. Активируйте грант для студентов/стартапов
3. Создайте виртуальную машину:
   - Образ: Ubuntu 22.04 LTS
   - vCPU: 2
   - RAM: 2GB
   - Disk: 10GB
   - Публичный IP: да

### Шаг 2: Настройка Security Group

Добавьте правила для входящего трафика:
- TCP 22 (SSH)
- TCP 80 (HTTP)
- TCP 443 (HTTPS)
- TCP 3000 (App)

### Шаг 3-7: Аналогично Cloud.ru

Следуйте шагам 2-6 из раздела Cloud.ru

## Настройка туннеля

### Ngrok

1. Зарегистрируйтесь на https://ngrok.com
2. Получите auth token
3. Добавьте в `.env`:
   ```env
   USE_NGROK=true
   NGROK_AUTH_TOKEN=your_token
   ```

### Альтернатива: localtunnel

```bash
npm install -g localtunnel
lt --port 3000
```

### Публичный IP (рекомендуется для продакшена)

Если у вас есть виртуальная машина с публичным IP:

1. Настройте брандмауэр
2. Настройте reverse proxy (Nginx)
3. Получите SSL сертификат (Let's Encrypt)

## Проверка работоспособности

### 1. Health Check

```bash
curl http://localhost:3000/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "github_app_configured": true,
  "llm_configured": true
}
```

### 2. Webhook

Создайте тестовый Issue в репозитории с установленным приложением.

Проверьте логи:
```bash
# Локально
tail -f app.log

# Docker
docker-compose logs -f app
```

### 3. Интеграционный тест

1. Создайте Issue с простой задачей:
   ```
   Название: Add hello world function
   
   Описание:
   Create a function `hello_world()` that returns "Hello, World!"
   Add unit tests for this function.
   ```

2. Дождитесь создания PR
3. Проверьте автоматический review
4. Убедитесь, что CI проходит

## Troubleshooting

### Проблема: Webhook не работает

**Решение:**
1. Проверьте логи: `docker-compose logs app`
2. Проверьте webhook secret
3. Проверьте, что URL доступен извне
4. Проверьте логи GitHub App (Settings → Developer settings → GitHub Apps → Advanced)

### Проблема: LLM не отвечает

**Решение:**
1. Проверьте API ключ
2. Проверьте баланс аккаунта
3. Проверьте rate limits
4. Тестируйте соединение: `python -c "from utils.llm import LLMClient; LLMClient().test_connection()"`

### Проблема: Приватный ключ не найден

**Решение:**
1. Проверьте путь в `.env`
2. Проверьте права доступа: `chmod 600 keys/private-key.pem`
3. В Docker убедитесь, что volume примонтирован

## Следующие шаги

- Настройте CI/CD для самого проекта
- Добавьте мониторинг (Prometheus, Grafana)
- Настройте логирование в внешний сервис
- Добавьте rate limiting
- Настройте автоматическое резервное копирование

## Поддержка

Если у вас возникли проблемы:

1. Проверьте [FAQ](FAQ.md)
2. Посмотрите [Examples](examples/)
3. Создайте Issue в репозитории
