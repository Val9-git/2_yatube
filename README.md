# Социальная сеть Yatube для публикации личных дневников

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

### Описание проекта
Социальная сеть для авторов и подписчиков. Пользователи могут подписываться на избранных авторов, оставлять и удалять комментари к постам, оставлять новые посты на главной странице и в тематических группах, прикреплять изображения к публикуемым постам.

### Запуск сервера
> Для MacOs и Linux вместо python использовать python3

Клонировать репозиторий.

```
git@github.com:Val9-git/2_yatube.git
```

Cоздать и активировать виртуальное окружение:

```
  $ cd yatube
  $ python -m venv venv
```

Для Windows:

```
  $ source venv/Scripts/activate
```

Для MacOs/Linux:

```
  $ source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
(venv) $ python -m pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

Создать и запустить миграции:

```
cd yatube/
python manage.py makemigrations
python manage.py migrate
```

Запустить сервер:

```
python manage.py runserver
```

После выполнения вышеперечисленных инструкций проект доступен по адресу http://127.0.0.1:8000/

### Автор:
Valeriy Lozitskiy
