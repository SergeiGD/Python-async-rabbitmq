# Python-async-rabbitmq

## В данном репозитории содержится проект с взаимодействием программ-клиентов с программой-сервером с помощью aio_pika (асинхронная обработка клиентских запросов с помощью очередей RabbitMQ)

## Инструкция по запуску:

1) Создайте базу данных postgresql 
```
create books
```

2) Импортируйте данные в базу данных
```bash
psql books < ./db_dump.sql
```

3) В папке с проектом создайте файл .env
```bash
touch .env
```

4) В нем задайте в нем ваш логин и пароль postgresql (под которым вы создали БД)
```bash
db_login=YOUR_DB_LOGIN
db_passwd=YOUR_DB_PASSWORD
```

5) Создайте вирутальную среду
```bash
python3 -m venv venv
```

6) Активируйте среду
```bash
source venv/bin/activate
```

7) Установите необходимые пакеты
```bash
pip install -r requirements.txt
```

8) Запустите программы
```bash
python3 server.py
python3 client.py
```

**Логины и пароли пользователей:**
* admin - 123
* user1 - mypass123
* user2 - qwerty