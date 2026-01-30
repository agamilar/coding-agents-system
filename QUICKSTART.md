# 🚀 Quick Start - Coding Agents System

## За 5 минут до работающей системы!

### Шаг 1: Скачайте проект

```bash
# Если у вас есть архив
tar -xzf coding-agents-system.tar.gz
cd coding-agents-system

# Или клонируйте из репозитория
git clone <your-repo-url>
cd coding-agents-system
```

### Шаг 2: Создайте GitHub App

1. Перейдите: https://github.com/settings/apps/new
2. Заполните:
   - **Name**: `coding-agents-yourname` (уникальное имя)
   - **Homepage URL**: `http://localhost:3000` (временно)
   - **Webhook URL**: `http://localhost:3000/webhook` (обновите позже)
   - **Webhook secret**: (сгенерируйте: `openssl rand -hex 32`)

3. **Permissions**:
   - Contents: Read & Write
   - Issues: Read & Write
   - Pull requests: Read & Write
   - Workflows: Read & Write

4. **Events**:
   - ✅ Issues
   - ✅ Pull request
   - ✅ Pull request review

5. Нажмите "Create GitHub App"
6. Скачайте приватный ключ (.pem файл)
7. Скопируйте App ID

### Шаг 3: Настройте проект

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env:
nano .env  # или используйте ваш редактор
```

Минимальная конфигурация `.env`:
```env
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=/app/keys/private-key.pem
GITHUB_WEBHOOK_SECRET=your_secret_from_step2

OPENAI_API_KEY=sk-...  # или другой LLM провайдер

USE_NGROK=true
NGROK_AUTH_TOKEN=your_ngrok_token  # получите на ngrok.com
```

### Шаг 4: Разместите приватный ключ

```bash
mkdir -p keys
cp ~/Downloads/your-private-key.pem keys/private-key.pem
chmod 600 keys/private-key.pem
```

### Шаг 5: Запустите систему

```bash
./start.sh
```

Или вручную:
```bash
docker-compose --profile ngrok up -d
```

### Шаг 6: Получите публичный URL

После запуска проверьте ngrok dashboard:
```
http://localhost:4040
```

Скопируйте публичный URL (например: `https://abc123.ngrok.io`)

### Шаг 7: Обновите GitHub App

1. Вернитесь в настройки GitHub App
2. Обновите Webhook URL на: `https://abc123.ngrok.io/webhook`
3. Сохраните

### Шаг 8: Установите App на репозиторий

1. В настройках GitHub App нажмите "Install App"
2. Выберите репозиторий для тестирования
3. Нажмите "Install"

### Шаг 9: Создайте тестовый Issue

В вашем репозитории создайте Issue:

```markdown
**Title:** Add hello world function

**Description:**
Create a file `hello.py` with a function `hello_world()` that returns "Hello, World!"

Add unit tests for this function.
```

### Шаг 10: Наблюдайте магию! ✨

1. Система автоматически создаст PR
2. GitHub Actions запустит проверки
3. Review Agent проверит код
4. Если нужно - Code Agent исправит

Следите за процессом:
```bash
# Логи
docker-compose logs -f app

# Статус
curl http://localhost:3000/health
```

## Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Проверка здоровья
curl http://localhost:3000/health

# Информация о настройке
curl http://localhost:3000/setup
```

## Troubleshooting

**Проблема:** Ngrok не работает
```bash
# Проверьте токен
echo $NGROK_AUTH_TOKEN

# Перезапустите с ngrok
docker-compose --profile ngrok restart
```

**Проблема:** Webhook не получает события
- Проверьте URL в настройках GitHub App
- Проверьте логи: `docker-compose logs app`
- Проверьте webhook secret

**Проблема:** LLM не отвечает
- Проверьте API ключ
- Проверьте баланс
- Проверьте логи

## Что дальше?

- 📖 Полная документация: [README.md](README.md)
- 🚢 Развертывание в облаке: [DEPLOYMENT.md](DEPLOYMENT.md)
- 📊 Отчет о системе: [REPORT.md](REPORT.md)
- 💡 Примеры Issues: [examples/EXAMPLE_ISSUES.md](examples/EXAMPLE_ISSUES.md)

## Нужна помощь?

Создайте Issue в репозитории или проверьте документацию!

---

**Приятного использования! 🎉**
