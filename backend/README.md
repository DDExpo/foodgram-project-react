## Проект Foodgram

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

<!-- Проект доступен по [адресу](https://.ru)

Документация к API доступна [здесь](https://.ru/api/docs/) -->

В документации описаны возможные запросы к API и структура ожидаемых ответов. Для каждого запроса указаны уровни прав доступа.

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL,

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
https://github.com/DDExpo/foodgram-project-react.git
```

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:

- Создать и запустить контейнеры Docker, выполнить команду на сервере
```
sudo docker compose up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```

- Наполнить базу данных заготовленными данными:
```
sudo docker compose exec backend python manage.py load_data
```

### Запуск проекта на локальной машине:

- Клонировать репозиторий:
```
https://github.com/DDExpo/foodgram-project-react.git
```

- В директории infra создать файл .env и заполнить своими данными по аналогии с .env.example:
```

- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```

```
docker-compose -f docker-compose-local.yml up -d
```

### Автор backend'а:

Михаил Солдаткин (c) 2022

 #### All Api request can be found in greenelephant/static/redoc2.yaml or after starting project at 
``` 
http://localhost/api/redoc/
```

## Readme was made with help 
``` 
https://github.com/joemccann/dillinger
``` 
``` 
https://github.com/octokatherine/readme.so
``` 


## License

[MIT](https://choosealicense.com/licenses/mit/)

