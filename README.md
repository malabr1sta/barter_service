# 📦 Приложение по обмену товаров

**Barter Service** — это веб-приложение, позволяющее пользователям обмениваться товарами напрямую между собой. Система поддерживает создание объявлений, поиск и фильтрацию товаров, а также безопасный обмен между участниками.


## 🚀 Возможности

- Регистрация и авторизация пользователей
- Создание и управление объявлениями
- Поиск и фильтрация товаров
- Система обмена между пользователями
- REST API для взаимодействия с внешними приложениями

## 🛠️ Используемые технологии

- Django / Django REST Framework
- PostgreSQL
- Nginx
- Docker
- Docker-compose

## ⚙️ Установка и запуск вручную

```bash
# 1. Клонируйте репозиторий
git clone git@github.com:malabr1sta/barter_service.git
cd barter_service/

# 2. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Соберите статику
python ./barter/manage.py collectstatic

# 5. Скопируйте файл окружения
cp env_template .env
```

## 🧪 Тестирование

Для запуска тестов используйте команду:

```bash
python ./barter/manage.py test ads
```

## 🔧 После тестирования

Чтобы включить рабочий режим, замените переменную окружения DJANGO_TEST на False:

```bash
sed -i 's/DJANGO_TEST=True/DJANGO_TEST=False/' .env
# Для macOS используйте:
# sed -i '' 's/DJANGO_TEST=True/DJANGO_TEST=False/' .env
```

## 🐳 Запуск через Docker Compose

```bash
docker-compose up --build
```

После успешного запуска сервиса выполните следующие команды в новом терминале для применения миграций и создания суперпользователя:

```bash
docker exec -it barter_web_server python manage.py migrate
docker exec -it barter_web_server python manage.py createsuperuser
```

---

## 🌐 Доступ к сервису

- **Главная страница объявлений:** [http://127.0.0.1/ads/](http://127.0.0.1/ads/)
- **Админка:** [http://127.0.0.1/admin/](http://127.0.0.1/admin/)
- **Документация API:** [http://127.0.0.1/api/docs/](http://127.0.0.1/api/docs/)

---

## 📄 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).


## 👤 Автор

[malabr1sta](https://github.com/malabr1sta)

---
