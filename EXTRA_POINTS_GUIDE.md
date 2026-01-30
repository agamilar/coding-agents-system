# 🎓 Как получить дополнительные баллы с Yandex Cloud

## ✨ Что нужно для доп баллов

Согласно ТЗ, для получения дополнительных баллов необходимо:

> Доп-баллы за разворачивание решения в облаке:
> - Вариант через бесплатный период на https://cloud.ru
> - **Вариант через бесплатный период на https://console.yandex.cloud** ✅

## 🚀 План действий (30-60 минут)

### 1️⃣ Активируйте грант Yandex Cloud (5 минут)

**Вариант А: Студенческий грант (рекомендуется)**
- Перейдите: https://cloud.yandex.ru/students
- Получите 4000₽ на 1 год
- Требуется: email учебного заведения

**Вариант Б: Стартовый грант**
- Перейдите: https://console.cloud.yandex.ru
- Получите 1000₽ на 60 дней
- Требуется: регистрация

### 2️⃣ Создайте виртуальную машину (10 минут)

1. Войдите в консоль: https://console.cloud.yandex.ru
2. Compute Cloud → Создать ВМ
3. Конфигурация:
   - **Образ:** Ubuntu 22.04 LTS ✅ Docker
   - **vCPU:** 2
   - **RAM:** 2 ГБ
   - **Диск:** 15 ГБ SSD
   - **Публичный IP:** ✅ Да
   - **SSH ключ:** добавьте ваш публичный ключ

4. Скопируйте публичный IP адрес!

📸 **Скриншот 1:** Консоль Yandex Cloud со списком VM

### 3️⃣ Подключитесь к VM (2 минуты)

```bash
# Замените YOUR_VM_IP на ваш IP
ssh ubuntu@YOUR_VM_IP
```

### 4️⃣ Загрузите проект на VM (5 минут)

**Способ 1: Через Git (рекомендуется)**
```bash
# На VM
git clone https://github.com/your-username/coding-agents-system.git
cd coding-agents-system
```

**Способ 2: Через SCP**
```bash
# На вашем компьютере
scp coding-agents-system.tar.gz ubuntu@YOUR_VM_IP:~
ssh ubuntu@YOUR_VM_IP
tar -xzf coding-agents-system.tar.gz
cd coding-agents-system
```

### 5️⃣ Запустите автоматическое развертывание (5-10 минут)

```bash
# На VM
./deploy-yandex.sh
```

Скрипт автоматически:
- ✅ Установит все зависимости
- ✅ Настроит Docker
- ✅ Настроит Nginx
- ✅ Настроит автозапуск
- ✅ Запустит приложение

Следуйте инструкциям скрипта.

📸 **Скриншот 2:** Вывод команды `docker-compose ps` (показывает работающие контейнеры)

### 6️⃣ Настройте переменные окружения (5 минут)

Когда скрипт попросит, отредактируйте `.env`:

```bash
nano .env
```

**Минимальная конфигурация:**
```env
# GitHub App
GITHUB_APP_ID=123456
GITHUB_WEBHOOK_SECRET=your_secret

# Yandex GPT (для максимальных баллов!)
YANDEX_API_KEY=ваш_api_ключ
YANDEX_FOLDER_ID=ваш_folder_id

# Отключить ngrok на сервере
USE_NGROK=false
```

**Как получить Yandex API:**
1. Консоль → IAM → Сервисные аккаунты
2. Создать сервисный аккаунт с ролью `ai.languageModels.user`
3. Создать API ключ
4. Скопировать ключ и ID каталога

### 7️⃣ Добавьте GitHub App ключ (3 минуты)

```bash
nano keys/private-key.pem
# Вставьте содержимое вашего GitHub App private key
# Ctrl+X, Y, Enter
```

### 8️⃣ Настройте GitHub App Webhook (2 минуты)

1. Перейдите в настройки вашего GitHub App
2. Обновите **Webhook URL**:
   ```
   http://YOUR_VM_IP/webhook
   ```
3. Сохраните

📸 **Скриншот 3:** Настройки GitHub App с webhook URL

### 9️⃣ Проверьте работоспособность (5 минут)

```bash
# На VM или с вашего компьютера
curl http://YOUR_VM_IP/health
```

Должен вернуть:
```json
{
  "status": "healthy",
  "github_app_configured": true,
  "llm_configured": true
}
```

📸 **Скриншот 4:** Вывод health check

### 🔟 Создайте тестовый Issue (5 минут)

1. Установите GitHub App на репозиторий
2. Создайте Issue:

```markdown
**Title:** Test Yandex Cloud Deployment

**Description:**
Создать функцию `factorial(n: int) -> int` которая:
- Вычисляет факториал числа
- Обрабатывает ошибки для n < 0
- Покрыта unit-тестами

Пример:
- factorial(5) → 120
- factorial(0) → 1
```

3. Дождитесь автоматического создания PR

📸 **Скриншот 5:** Созданный автоматически PR
📸 **Скриншот 6:** Комментарий от Review Agent

### 1️⃣1️⃣ Проверьте мониторинг (опционально)

В консоли Yandex Cloud:
- Перейдите в вашу VM
- Вкладка "Мониторинг"
- Посмотрите графики CPU, RAM, Network

📸 **Скриншот 7:** Графики мониторинга VM

## 📸 Обязательные скриншоты для отчета

1. ✅ Консоль Yandex Cloud с вашей VM (показан IP, статус)
2. ✅ Вывод `docker-compose ps` (контейнеры работают)
3. ✅ GitHub App настройки (webhook URL)
4. ✅ Health check endpoint (возвращает healthy)
5. ✅ Автоматически созданный PR
6. ✅ Комментарий Review Agent в PR
7. ✅ (опционально) Мониторинг VM

## 📝 Что написать в отчете

### Раздел "Развертывание в облаке"

```markdown
## Развертывание в Yandex Cloud

Система развернута на виртуальной машине в Yandex Cloud.

### Конфигурация VM:
- **Платформа:** Yandex Cloud
- **ОС:** Ubuntu 22.04 LTS
- **Ресурсы:** 2 vCPU, 2 GB RAM, 15 GB SSD
- **Публичный IP:** XX.XX.XX.XX
- **Регион:** ru-central1-a

### Компоненты:
- Docker & Docker Compose
- Nginx (reverse proxy)
- Systemd (автозапуск)
- Coding Agents System

### LLM провайдер:
Используется **Yandex GPT** для генерации кода и review.
- Model: yandexgpt-lite
- Интеграция через Yandex Cloud API

### Доступность:
Система доступна 24/7 по адресу: http://XX.XX.XX.XX

### Webhook:
GitHub App настроен с webhook URL: http://XX.XX.XX.XX/webhook

### Автозапуск:
Настроен systemd service для автоматического запуска при перезагрузке VM.

[Скриншоты прилагаются]
```

## ✅ Чеклист готовности

- [ ] VM создана в Yandex Cloud
- [ ] Публичный IP получен
- [ ] Проект загружен на VM
- [ ] Скрипт `deploy-yandex.sh` выполнен
- [ ] `.env` настроен с Yandex GPT
- [ ] GitHub App private key размещен
- [ ] Docker containers запущены
- [ ] Health check возвращает "healthy"
- [ ] GitHub App webhook настроен
- [ ] Тестовый Issue создан → PR автоматически создан
- [ ] Review Agent проверил код
- [ ] Сделаны все обязательные скриншоты
- [ ] Написан раздел в отчете

## 🎯 Дополнительные плюсы

### Использование Yandex GPT (вместо OpenAI)
- ✅ Показывает знание отечественных технологий
- ✅ Дешевле для экспериментов
- ✅ Поддержка русского языка

### Nginx + потенциально SSL
- ✅ Production-ready setup
- ✅ Готово к получению SSL сертификата
- ✅ Профессиональный подход

### Systemd autostart
- ✅ Система переживет перезагрузку
- ✅ Показывает понимание Linux

## 💰 Стоимость

На студенческом гранте (4000₽):
- ~1500₽/месяц
- **Хватит на 2.5+ месяца**
- Для демонстрации и тестирования более чем достаточно

## 🆘 Если что-то пошло не так

### Быстрая диагностика:

```bash
# Проверка контейнеров
docker-compose ps

# Логи приложения
docker-compose logs app

# Статус systemd
sudo systemctl status coding-agents

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
```

### Перезапуск всего:

```bash
sudo systemctl restart coding-agents
sudo systemctl restart nginx
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker-compose logs app`
2. Проверьте документацию: `YANDEX_CLOUD_DEPLOYMENT.md`
3. Проверьте `.env` конфигурацию
4. Убедитесь, что все порты открыты в Security Groups

---

**Удачи с получением дополнительных баллов! 🚀**
