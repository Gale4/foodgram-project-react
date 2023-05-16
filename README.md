
# Продуктовый помощник Foodgtam
![example workflow](https://github.com/Gale4/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Пользователи могут публиковать рецепты, подписываться на публикации друг друга, добавлять рецепты в список и скачивать список продуктов перед походом в магазин. Проект развернут на удаленном сервере в связке Docker контейнеров обеспечивающих работу базы данных (PostgreSQL), сервера nginx и приложения Django + gunicorn.

### Для просмотра проекта

* Адрес: [158.160.1.232](http://158.160.1.232/)<br>
* Логин (Для сайта): <code>test@ya.ru</code><br>
* Логин (Для админки): <code>review</code><br>
* Пароль: <code>reviewpass</code>

## Запуск прокета на удаленном сервере
Выполните вход на удаленный сервер:
```
ssh <username>@<адрес_сервера>
```
Установите Docker:
```
sudo apt install docker.io
```
Установите docker-compose на удаленный сервер
[в соответсвии с установленнной системой.](https://docs.docker.com/compose/install/)

Скопируйте проет:
```
git clone git@github.com:Gale4/foodgram-project-react.git
```
Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra
```
scp docker-compose.yml nginx.conf username@IP:/home/username/

```
**Запустите Docker контейнеры выполнив команду в папке foodgram-project-react/infra**
```
sudo docker-compose up -d
```
Войдите в контейнер:
```
sudo docker container ls # узнать id контейнера приложения
sudo docker exec -it <id_контейнера> bash
```
Установите зависимости:
```
pip install -r requirements.txt
```
Выполните миграции, ипортируйте тестовые данные, собирите статику:
```
python manage.py makemigrations
python manage.py migrate
python manage.py import
python manage.py collectstatic --no-input
```
**После этого проект будет доступен по адресу вашего сервера.**

## Запуск на локальном компьютере

* Клонируйте проект

* Поменяйте настроки DATABASES в фаиле /backend/foodgram/settings.py на слудующие:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Установите и активирйте локальное окружение. Установите зависимости и выполните миграции:
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py import
python manage.py collectstatic --no-input
```
**Запустите проект:**
```
python manage.py runserver
```
Теперь проект доступен для обращения через API запросы по адресу:
[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

#### Примеры запросов:
```
POST http://127.0.0.1:8000/api/auth/token/login/ # Получить токен авторизации
GET http://127.0.0.1:8000/api/recipes/ # Получить список рецептов
GET http://127.0.0.1:8000/api/recipes/1/ # Получить данные рецепта с id1
POST GET http://127.0.0.1:8000/api/recipes/1/shopping_cart/ # Добавить рецепт в список покупок
GET http://127.0.0.1:8000/api/recipes/download_shopping_cart/ #скачать список покупок
```

##### Проект сделан в рамках учебного процесса по специализации Python-разработчик (backend) Яндекс.Практикум.
