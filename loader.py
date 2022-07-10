import multiprocessing as mp
import random
from client import *
from classes.book import *
from classes.user import *
import asyncio
from typing import List
from hashlib import sha256
import string
import json
import time
import datetime


allowed_commands = ["del", "add"]                                   # разрешенные команды
existing_books: List[Book] = []                                             # книги, которые есть в БД
is_timeout = mp.Manager().Value('i', False)                                 # булево значения общее для всех процессов, отображающее, не пора ли заканчивать работать


async def make_task(login, passwd):                                         # создание запроса к серверу
    global existing_books
    current_client = await RpcClient().connect(login, passwd)               # клиент процесса

    while not is_timeout.value:
        msg = {}
        msg["command"] = random.choice(allowed_commands)                    # команда выбирается случайно

        if msg["command"] == "del" and len(existing_books) == 0:            # если нету книг, то и удалить не можем
            continue

        if msg["command"] == "add":
            new_book = gen_book()
            msg["object"] = new_book                                        # генерируем книгу, которую будем создавать

        if msg["command"] == "del":
            del_book = random.choice(existing_books)                        # выбираем случайную книгу
            msg["object"] = del_book.id

        response = await current_client.call(msg)                           # отправляем запрос серверу

        upd_command = {"command": "read"}                                   # сразу после "основного" запроса отправляем запрос на обновленеие списка книг
        upd_response = await current_client.call(upd_command)

        try:
            content = json.loads(response)
            updated_books = json.loads(upd_response)                        # вместе с ответом на "основную" команду подгружаем список книг
            existing_books = BookJson.from_json(updated_books)
        except Exception as error:
            print("Ошибка получения данных от сервера: ", error)
            print("Клиент выключается...")
            await current_client.disconn_alert()                            # если не получается обработать ответ
            break

        out_info = login + ' - ' + datetime.datetime.now().strftime("%H:%M:%S") + ' - ' + content       # выводим ответ и доп. информацию
        print(out_info)

    await current_client.disconn_alert()                                # когда закончилось время работы (вышли из цикла), отправляем сообщение, об отключении


def gen_book():                                                             # генерируем книгу со случайными данными
    name = ''.join(random.choices(string.ascii_uppercase, k=5))
    author = ''.join(random.choices(string.ascii_uppercase, k=5))
    pages = random.randint(1, 30)
    book = Book(name, author, pages)
    return book


def spawn():                                                                # создание процессов
    processes = []
    for c in range(1, client_count + 1):
        login = f"test_user{c}"
        passwd = sha256(f"pass{c}".encode()).hexdigest()
        processes.append(mp.Process(target=task_starter, args=(login, passwd)))     # создаем процесс и кидаем логин и пароль для аутиентификации

    processes.append(mp.Process(target=timer))                                      # в конце добавляем процесс, который будет следить за временем работы

    for p in processes:                                                             # запускам все процессы
        p.start()
    for p in processes:
        p.join()


def task_starter(login, passwd):
    asyncio.run(make_task(login, passwd))                                           # т.к. не можем закинуть в target asnyc функцию, обойдем это таким образом


def timer():
    time.sleep(runtime_secs)                                                        # по истечению установленного времени работы ставим флаг завершения работы
    is_timeout.value = True


def load_settings():
    with open("config_files/load_settings.json") as f:                              # читаем json
        cfg = json.load(f)
    client_count = cfg["clients_count"]
    runtime_secs = cfg["runtime"]

    if not str(client_count).isdigit() or not str(runtime_secs).isdigit():          # проверям данные
        print("Кол-во клиентов и время работы должны быть числом")
        exit()
    if client_count > 49 or client_count < 3:
        print("Кол-во клиентов не может быть больше 49 или меньше 3")
        exit()
    if runtime_secs > 180 or runtime_secs < 3:
        print("Время работы не может быть больше 180 или меньше 3")
        exit()

    return (client_count, runtime_secs)


if __name__ == '__main__':
    client_count, runtime_secs = load_settings()                                    # получаем кол-во процессов-клиентов и время работы
    spawn()                                                                         # вызываем метод создания процессов
