# 🚀 Быстрая установка Coding Agents System

## 📋 Требования

- Docker 20.10+
- Docker Compose 2.0+
- GitHub App credentials
- YandexGPT API key (или OpenAI/Anthropic)

---

## ⚡ Установка за 5 минут

### Шаг 1: Клонирование

```bash
git clone https://github.com/agamilar/coding-agents-system.git
cd coding-agents-system
```

### Шаг 2: Создание `.env` файла

```bash
cp .env.example .env
nano .env  # или используйте любой редактор
```

### Шаг 3: Заполнение `.env`

Замените все `<paste_...>` на ваши реальные значения:

```env
# GitHub App
GITHUB_APP_ID=<paste_your_github_app_id>
GITHUB_APP_PRIVATE_KEY_PATH=/app/keys/private-key.pem
GITHUB_WEBHOOK_SECRET=<paste_your_webhook_secret>
GITHUB_INSTALLATION_ID=<paste_your_installation_id>

# YandexGPT
YANDEX_API_KEY=<paste_your_yandex_api_key>
YANDEX_FOLDER_ID=<paste_your_yandex_folder_id>
YANDEX_MODEL=yandexgpt-lite

# Settings (можно не менять)
CODE_AGENT_TEMPERATURE=0.3
REVIEW_AGENT_TEMPERATURE=0.2
MAX_ITERATIONS=5
FLASK_PORT=3000
LOG_LEVEL=INFO
```

### Шаг 4: Добавление приватного ключа

```bash
mkdir -p keys
cp /path/to/your/downloaded-key.pem keys/private-key.pem
```

### Шаг 5: Запуск

```bash
docker-compose up -d
```

### Шаг 6: Проверка

```bash
# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f app

# Проверить health endpoint
curl http://localhost:3000/health
```

---

## 📝 Где взять credentials?

### GitHub App ID и ключи:

1. Создайте GitHub App: https://github.com/settings/apps/new
2. **App ID** - в разделе "About"
3. **Private Key** - нажмите "Generate a private key"
4. **Webhook Secret** - придумайте или сгенерируйте:
   ```bash
   openssl rand -hex 32
   ```
5. **Installation ID** - установите App в репо, ID будет в URL

**Permissions нужны:**
- Contents: Read & Write
- Issues: Read & Write
- Pull requests: Read & Write

**Events:**
- Issues
- Pull request
- Pull request review

### YandexGPT API:

1. Зайдите: https://console.cloud.yandex.ru
2. Создайте/выберите проект (Folder)
3. **Folder ID** - в настройках проекта
4. **API Key** - создайте в разделе "API ключи"

---

## 🔧 Управление

```bash
# Перезапуск
docker-compose restart app

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs --tail=100 app

# Пересборка (после изменений)
docker-compose build --no-cache
docker-compose up -d
```

---

## ✅ Проверка работы

1. Создайте тестовый Issue в GitHub:
   ```
   Title: Create hello.py
   Body: Create a Python script that prints "Hello, World!"
   ```

2. Через 5-10 секунд должен появиться PR!

3. Проверьте GitHub Actions в PR - должен запуститься Review Agent

---

## 🐛 Решение проблем

### "Private key not found"
```bash
# Проверьте что ключ на месте
ls -la keys/private-key.pem

# Проверьте права
chmod 600 keys/private-key.pem
```

### "Failed to authenticate"
- Проверьте GITHUB_APP_ID
- Проверьте что ключ правильный
- Проверьте GITHUB_WEBHOOK_SECRET

### "YandexGPT API error"
- Проверьте YANDEX_API_KEY (начинается с AQVN)
- Проверьте YANDEX_FOLDER_ID
- Проверьте квоты в Yandex Cloud

### Webhook не работает
```bash
# Проверьте что порт доступен
curl http://localhost:3000/health

# Если на сервере, проверьте firewall
sudo ufw allow 3000
```

---

## 📚 Полная документация

- **Подробная установка:** См. README.md
- **Архитектура:** См. REPORT.md
- **Примеры Issues:** См. examples/

---

## 🔐 Безопасность

**⚠️ НИКОГДА не коммитьте в Git:**
- `.env` - реальные ключи
- `keys/*.pem` - приватные ключи
- Любые файлы с секретами

**✅ Можно коммитить:**
- `.env.example` - с заглушками `<paste_...>`
- README и документацию
- Исходный код

---

## 🎯 Что дальше?

После успешного запуска:

1. ✅ Протестируйте на простых Issues
2. ✅ Настройте GitHub Secrets для CI/CD
3. ✅ Добавьте мониторинг (опционально)
4. ✅ Настройте backup (для production)

---

**Готово! Система работает! 🎉**

Если возникли проблемы - создайте Issue в репозитории.