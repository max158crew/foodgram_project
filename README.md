
Cайт [Foodgram](https://yandexmax.ddns.net), Продуктовый помощник с возможностью размещать рецепты пользователей, подписываться на других авторов, добавлять список ингредиентов выбранного рецепта в корзину, скачивать список ингредиентов из корзины. 
## Использованные технологии

![Python](https://img.shields.io/badge/Python-3.7-3776AB?logo=Python&style=flat-square)

[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)

[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)

[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

[![Docker Compose](https://img.shields.io/badge/Docker_Compose-464646?style=flat-square)](https://docs.docker.com/compose/)

[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

## ip: 158.160.68.205, https://yandexmax.ddns.net/recipes
Admin login: test@mail.com
pass: Asd1asd2asd3

## Запуск
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:max158crew/foodgram_project.git
```
```
cd infra
```

Для функционирования - создать файл .env и прописать переменные окружения в нём.

```bash
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<ваш_secret_key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,158.160.68.205,<ip_вашего_сервера>
```

Выполнить команду из директории infra, где находится файл docker-compose.yaml
```bash
docker compose up
```
Выполнить миграции, создать суперпользователя и собрать статику. 
```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic 
```
Заполнить базу данными
```
docker compose exec backend python manage.py importcsv
```
База данных заполнится ингредиентами. 

Создать суперпользователя (введите логин, почту, имя, фамилию пароль):
```
docker compose exec backend python manage.py createsuperuser
```
Залогиниться в админ панель, используя данные суперпользователя.
Через админ панель создать 2-3 тэга для проведения тестов.
## Примеры запросов:

### Регистрация нового пользователя:

```bash
POST - '/api/users/'
```
```yaml
{
  "username": "username.",
  "email": "username@mail.ru",
  "password": "password.",
  "first_name": "first_name",
  "last_name": "last_name"
}
```

#### Ответ
```yaml
{
  "id": 2,
  "username": "username.",
  "email": "username@mail.ru",
  "first_name": "irst_name",
  "last_name": "last_name"
}
```

### Получение токена:
#### Запрос
```bash
POST - '/api/auth/token/login/'
```
```yaml
{
  "password": "password.",
  "email": "username@mail.ru"
}
```

#### Ответ
```yaml
{ "auth_token": "token_value" }
```

### Информация о своей учетной записи:
#### Запрос
```bash
GET - '/api/users/me/'
header 'Authorization: Token "token_value"'
```

#### Ответ
```yaml
{
  "id": 2,
  "username": "username.",
  "email": "username@mail.ru",
  "first_name": "first_name",
  "last_name": "last_name",
  "is_subscribed": false
}
```

### Добавление нового рецепта:
#### Запрос
```bash
POST - '/api/recipes/'
header 'Authorization: Token "token_value"'
```
```yaml
{
  "ingredients": [
    {
      "id": 1,
      "amount": 10
    },
    {
      "id": 8,
      "amount": 25
    },
    {
      "id": 7,
      "amount": 30
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 5
}
```

#### Ответ
```yaml
{
    "id": 1,
    "tags": [
        {
            "id": 2,
            "name": "обед",
            "color": "#FFD81B",
            "slug": "llunch"
        },
        {
            "id": 1,
            "name": "Завтрак",
            "color": "#FFFFFF",
            "slug": "breakfast"
        }
    ],
    "author": {
        "email": "username@mail.ru",
        "id": 2,
        "username": "username.",
        "first_name": "first_name",
        "last_name": "last_name",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 2,
            "name": "абрикосовый джем",
            "measurement_unit": "г",
            "amount": 10.0
        },
        {
            "id": 8,
            "name": "агар-агар",
            "measurement_unit": "г",
            "amount": 25.0
        },
        {
            "id": 7,
            "name": "агава сироп",
            "measurement_unit": "г",
            "amount": 30.0
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "Название рецепта",
    "image": "http://127.0.0.1:8000/media/recipes/images/temp_5LHaOzn.png",
    "text": "Описание рецепта",
    "cooking_time": 5
}
```