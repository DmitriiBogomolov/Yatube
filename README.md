# Коллективный блог

Функционал приложения:
- профили пользователей;
- система подписок;
- система постов и комментариев;
- разграничение прав доступа.

## Установка

1. Собрать приложение

        docker build -t yatube .

2. Запустить

        docker run -p 8000:8000 --name yatube_app yatube

3. Остановка:

        docker stop yatube_app

4. Сервис будет доступен по адресу http://localhost:8000

## Приложение

![1](https://github.com/DmitriiBogomolov/yatube/blob/master/static/refs/1.png)
![2](https://github.com/DmitriiBogomolov/yatube/blob/master/static/refs/2.png)
![3](https://github.com/DmitriiBogomolov/yatube/blob/master/static/refs/3.png)

## Лицензия
[MIT](https://choosealicense.com/licenses/mit/)
