# 🚀 Развертывание в Yandex Cloud - Пошаговая инструкция

Эта инструкция поможет развернуть Coding Agents System в Yandex Cloud и получить дополнительные баллы!

## 📋 Что вы получите

- ✅ Работающее приложение в облаке 24/7
- ✅ Публичный IP адрес (белый IP)
- ✅ SSL сертификат (HTTPS)
- ✅ Автоматический запуск при перезагрузке
- ✅ Бесплатно на грант для студентов/стартапов

## 🎓 Активация гранта Yandex Cloud

### Вариант 1: Грант для студентов (4000₽)

1. Перейдите: https://cloud.yandex.ru/students
2. Зарегистрируйтесь с email вашего учебного заведения
3. Подтвердите статус студента
4. Получите 4000₽ на 1 год

### Вариант 2: Стартовый грант (1000₽)

1. Перейдите: https://console.cloud.yandex.ru
2. Зарегистрируйтесь
3. Активируйте пробный период
4. Получите 1000₽ на 60 дней

### Вариант 3: Грант для стартапов

1. Перейдите: https://cloud.yandex.ru/startup
2. Заполните анкету
3. Получите до 500,000₽

## 🖥️ Создание виртуальной машины

### Шаг 1: Создание облака и каталога

1. Войдите в консоль: https://console.cloud.yandex.ru
2. Создайте облако (если еще нет)
3. Создайте каталог "coding-agents"

### Шаг 2: Создание VM

1. В меню выберите **Compute Cloud** → **Виртуальные машины**
2. Нажмите **Создать ВМ**

### Шаг 3: Конфигурация VM

#### Базовые параметры:
- **Имя:** coding-agents-vm
- **Зона доступности:** ru-central1-a
- **Платформа:** Intel Ice Lake

#### Вычислительные ресурсы:
- **vCPU:** 2
- **RAM:** 2 ГБ
- **Уровень производительности:** 100%

#### Образ:
- **Семейство:** Ubuntu
- **Версия:** Ubuntu 22.04 LTS
- ✅ Установите галочку "Docker"

#### Диск:
- **Тип:** SSD
- **Размер:** 15 ГБ

#### Сеть:
- **Подсеть:** default-ru-central1-a
- ✅ **Публичный IP:** Установите галочку
- **Защита от DDoS:** Не требуется

#### Доступ:
- **Логин:** ubuntu
- **SSH-ключ:** 
  ```bash
  # Создайте ключ на вашем компьютере (если нет)
  ssh-keygen -t rsa -b 4096
  
  # Скопируйте содержимое
  cat ~/.ssh/id_rsa.pub
  
  # Вставьте в форму Yandex Cloud
  ```

#### Дополнительно:
- **Прерываемая:** НЕТ (важно!)
- **Автоматическое создание резервных копий:** По желанию

3. Нажмите **Создать ВМ**
4. Дождитесь создания (2-3 минуты)
5. **Скопируйте публичный IP адрес!**

## 🔒 Настройка группы безопасности

1. В меню VM выберите вкладку **Сеть**
2. Нажмите на имя подсети
3. Перейдите в **Группы безопасности**
4. Создайте новую группу или отредактируйте существующую

### Правила входящего трафика:

Добавьте следующие правила:

| Протокол | Порт | CIDR | Описание |
|----------|------|------|----------|
| TCP | 22 | 0.0.0.0/0 | SSH |
| TCP | 80 | 0.0.0.0/0 | HTTP |
| TCP | 443 | 0.0.0.0/0 | HTTPS |
| TCP | 3000 | 0.0.0.0/0 | App (временно) |

## 🔧 Подключение к VM и настройка

### Подключение по SSH

```bash
# Замените YOUR_VM_IP на ваш публичный IP
ssh ubuntu@YOUR_VM_IP
```

### Обновление системы

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка необходимых утилит
sudo apt install -y git curl wget nano htop
```

### Проверка Docker

```bash
# Docker должен быть предустановлен
docker --version
docker-compose --version

# Если нет, установите:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y

# Добавьте пользователя в группу docker
sudo usermod -aG docker ubuntu
newgrp docker
```

## 📦 Развертывание приложения

### Шаг 1: Загрузка проекта

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/coding-agents-system.git
cd coding-agents-system

# Или загрузите архив
wget https://your-storage.com/coding-agents-system.tar.gz
tar -xzf coding-agents-system.tar.gz
cd coding-agents-system
```

### Шаг 2: Настройка окружения

```bash
# Создайте .env файл
cp .env.example .env
nano .env
```

Конфигурация для Yandex Cloud:

```env
# GitHub App Configuration
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY_PATH=/app/keys/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Yandex GPT Configuration (для доп баллов!)
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id
YANDEX_MODEL=yandexgpt-lite

# Application Settings
USE_NGROK=false
MAX_ITERATIONS=5
LOG_LEVEL=INFO
FLASK_PORT=3000
FLASK_HOST=0.0.0.0
```

### Шаг 3: Получение Yandex GPT API ключа

1. Перейдите: https://console.cloud.yandex.ru/folders
2. Выберите ваш каталог
3. Скопируйте **ID каталога** → это ваш `YANDEX_FOLDER_ID`

4. Создайте API ключ:
   ```bash
   # В терминале Yandex Cloud CLI
   yc iam api-key create --service-account-id <YOUR_SERVICE_ACCOUNT_ID>
   ```
   
   Или через веб-интерфейс:
   - Перейдите в **IAM** → **Сервисные аккаунты**
   - Создайте сервисный аккаунт с ролью `ai.languageModels.user`
   - Создайте API ключ
   - Скопируйте ключ → это ваш `YANDEX_API_KEY`

### Шаг 4: Размещение приватного ключа GitHub

```bash
# Создайте директорию
mkdir -p keys

# Создайте файл ключа
nano keys/private-key.pem

# Вставьте содержимое вашего GitHub App private key
# Ctrl+X, Y, Enter для сохранения

# Установите права
chmod 600 keys/private-key.pem
```

### Шаг 5: Запуск приложения

```bash
# Запустите Docker Compose
docker-compose up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

## 🌐 Настройка Nginx и SSL

### Установка Nginx

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Настройка Nginx

```bash
# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/coding-agents
```

Вставьте конфигурацию:

```nginx
server {
    listen 80;
    server_name YOUR_VM_IP;  # Замените на ваш IP или домен

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте конфигурацию:

```bash
# Создайте символическую ссылку
sudo ln -s /etc/nginx/sites-available/coding-agents /etc/nginx/sites-enabled/

# Проверьте конфигурацию
sudo nginx -t

# Перезапустите Nginx
sudo systemctl restart nginx
```

### SSL сертификат (опционально, если есть домен)

Если у вас есть домен:

```bash
# Получите SSL сертификат
sudo certbot --nginx -d your-domain.com

# Certbot автоматически настроит HTTPS
```

## 🔄 Автозапуск при перезагрузке

```bash
# Создайте systemd service
sudo nano /etc/systemd/system/coding-agents.service
```

Содержимое:

```ini
[Unit]
Description=Coding Agents System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/coding-agents-system
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Активируйте:

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable coding-agents

# Запустите сервис
sudo systemctl start coding-agents

# Проверьте статус
sudo systemctl status coding-agents
```

## 🔗 Настройка GitHub App

1. Перейдите в настройки вашего GitHub App
2. Обновите **Webhook URL** на:
   ```
   http://YOUR_VM_IP/webhook
   ```
   Или если настроили домен и SSL:
   ```
   https://your-domain.com/webhook
   ```

3. Сохраните изменения

## ✅ Проверка работоспособности

### Тест 1: Health Check

```bash
# На VM
curl http://localhost:3000/health

# Или с вашего компьютера
curl http://YOUR_VM_IP/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "github_app_configured": true,
  "llm_configured": true
}
```

### Тест 2: Создайте Issue

1. Установите GitHub App на тестовый репозиторий
2. Создайте Issue:
   ```markdown
   **Title:** Test Yandex Cloud Deployment
   
   **Description:**
   Create a simple function `greet(name: str) -> str` that returns "Hello, {name}!"
   Add unit tests.
   ```

3. Следите за логами:
   ```bash
   docker-compose logs -f app
   ```

4. Проверьте, что PR был создан автоматически

## 📊 Мониторинг

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только приложение
docker-compose logs -f app

# Последние 100 строк
docker-compose logs --tail=100 app
```

### Использование ресурсов

```bash
# Использование Docker
docker stats

# Использование VM
htop
```

### Логи Nginx

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

## 💰 Оптимизация затрат

### Рекомендуемая конфигурация для гранта:

- **vCPU:** 2 (минимум, можно 4 для лучшей производительности)
- **RAM:** 2 ГБ (достаточно для работы)
- **Диск:** 15 ГБ SSD (хватит надолго)
- **Публичный IP:** Да (необходим)

### Ориентировочная стоимость:

- **2 vCPU + 2GB RAM:** ~1200₽/месяц
- **Публичный IP:** ~150₽/месяц
- **Диск 15GB SSD:** ~150₽/месяц
- **Итого:** ~1500₽/месяц

**На грант 4000₽ хватит на 2.5+ месяца работы!**

### Экономия:

1. Используйте прерываемую VM (скидка 50%) для тестирования
2. Останавливайте VM когда не нужна
3. Используйте HDD вместо SSD (если скорость не критична)

## 🎓 Оформление отчета для доп баллов

Для получения дополнительных баллов создайте скриншоты:

1. **Yandex Cloud Console:**
   - Список виртуальных машин (видна ваша VM)
   - Детали VM (IP адрес, конфигурация)
   - Мониторинг (CPU, RAM usage)

2. **Работающее приложение:**
   - Health check endpoint
   - Созданный PR
   - Логи работы

3. **GitHub App:**
   - Настройки webhook
   - История событий
   - Успешные PR

4. **Расходы:**
   - Страница биллинга (показать что в рамках гранта)

## 🔧 Troubleshooting

### Проблема: VM не создается

**Решение:**
- Проверьте наличие квоты на ресурсы
- Попробуйте другую зону доступности
- Уменьшите конфигурацию

### Проблема: Не могу подключиться по SSH

**Решение:**
```bash
# Проверьте, что правильно скопировали публичный ключ
# Проверьте группу безопасности (порт 22 открыт)
# Попробуйте:
ssh -v ubuntu@YOUR_VM_IP
```

### Проблема: Docker не запускается

**Решение:**
```bash
# Переустановите Docker
sudo apt remove docker docker-engine docker.io containerd runc
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Проблема: Yandex GPT не отвечает

**Решение:**
- Проверьте API ключ
- Проверьте FOLDER_ID
- Убедитесь, что сервисный аккаунт имеет нужные права
- Проверьте логи: `docker-compose logs app | grep -i yandex`

### Проблема: Webhook не работает

**Решение:**
- Проверьте, что порт 3000 или 80 открыт
- Проверьте URL в GitHub App настройках
- Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`

## 📝 Чеклист для сдачи

- [ ] VM создана в Yandex Cloud
- [ ] Публичный IP настроен
- [ ] Docker Compose запущен
- [ ] Health check возвращает "healthy"
- [ ] GitHub App настроен с webhook на VM IP
- [ ] Yandex GPT API настроен и работает
- [ ] Создан тестовый Issue → автоматически создан PR
- [ ] PR прошел review от AI
- [ ] Сделаны скриншоты для отчета
- [ ] Nginx настроен (опционально)
- [ ] SSL настроен (опционально)
- [ ] Автозапуск настроен

## 🎉 Готово!

Теперь у вас работающая система в Yandex Cloud!

### Полезные команды для демонстрации:

```bash
# Статус системы
docker-compose ps
systemctl status coding-agents

# Логи
docker-compose logs --tail=50 app

# Мониторинг
docker stats
htop

# Health check
curl http://YOUR_VM_IP/health
```

---

**Удачи с получением дополнительных баллов! 🚀**
