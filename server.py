import sys
from os import getenv
from aio_pika import *
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from classes.book import *
from classes.user import *
import asyncio
import psutil
import dotenv
from pathlib import Path


dotenv.load_dotenv()
db_login = getenv("db_login")
db_passwd = getenv("db_passwd")
engine = create_engine(f'postgresql+psycopg2://{db_login}:{db_passwd}@db:5432/books', pool_size=51, max_overflow=0)


try:
    test_conn = engine.connect()                                                                            # проверям подключение к БД
    test_conn.close()
except Exception as error:
    print("Не удалось подключится к базе данных")
    raise Exception('Ошибка подключения к базе данных')


session_fab = sessionmaker(bind=engine)
exchange: AbstractExchange
clients_connections: List[User] = []                                                                         # список, в котором хварнятся все активные пользователи


async def start_server():                                                                                   # Основная функция, запускающая сервер
    connection = await connect(host="rabbit")
    channel = await connection.channel()

    global exchange
    exchange = channel.default_exchange

    queue = await channel.declare_queue("rpc_queue", durable=False)                                         # очередь, в которую клиенту отправляют запросы

    connections_queue = await channel.declare_queue("connections_queue", exclusive=False, durable=False)    # очередь, в которую клиенты сообщают о подключении к серверу и отключении

    await connections_queue.consume(connection_handler, no_ack=True)

    print("Сервер запущен")

    async with queue.iterator() as qiterator:
        message: AbstractIncomingMessage

        async for message in qiterator:                                                                     # перебираем все сообщения, приходящие в очередь команд серверу
            async with message.process(requeue=False):
                assert message.reply_to is not None

                in_data = message.body.decode()                                                             # получаем пришедшие данные
                data = json.loads(in_data)                                                                  # загружаем их в словарь
                current_client = get_client_by_queue(message.reply_to)                                      # клиент, чье сообщение сейчас обрабатываем
                answer = None                                                                               # будующий ответ клиенту

                if current_client == None:
                    print("Не удалось индентифицировать отправителя...")
                    await exchange.publish(
                        Message(
                            body="Серверу не удалось Вас индентифицировать...".encode(),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )
                    continue

                print(f"Обработка запроса клиента - {current_client.login}")

                if data["command"] == 'bye':                                                                # Получена команда отключение клиента
                    print(f"Клиент {current_client.login} отключается по собственному желанию")             # Клиент позже сам отправит сообщение об отключение, которое обработывает connection_handler()

                if data["command"] == 'stop':                                                               # Получена команда остановки сервера
                    if current_client.is_admin:                                                             # Дополнительная проверка, есть ли права
                        print("Отключаем сервер")
                        for client in clients_connections:                                                  # Отправляем всем клиент сигнал об отключении
                            await exchange.publish(
                                Message(
                                    body="Сервер был отключен...".encode(),
                                    correlation_id=client.discon_id,
                                ),
                                routing_key=client.queue,
                            )
                        return
                    else:
                        answer = "Эта операция доступна только админам"

                if data["command"] == 'add':
                    print("Добавляем книгу")
                    answer = add_book(data["object"])                                                       # Передаем объект из полученного словаря в функцию добавления книги

                if data["command"] == 'del':
                    print("Удаляем книгу")
                    answer = del_book(data["object"])                                                       # Передает id из полученного словаря в функцию удаления книги

                if data["command"] == 'read':
                    print("Считываем список книг")
                    answer = read_books()                                                                   # Вызывается функция чтения книг, данные из функции записываются в переменную answer

                if data["command"] == 'clients':
                    print("Получаю список активных клиентов...")
                    answer = get_active_logins()                                                            #  Вызываем функцию получения клиентов и записываем результат

                if data["command"] == 'disconnect':
                    if current_client.is_admin:                                                             # Дополнительная проверка, есть ли права
                        client_to_discon = get_client_by_login(data["object"])                              # получаем объект клиента, которого надо отключить

                        if client_to_discon is not None:                                                    # Если такого клиента не нашлось, то он не подключен

                            await exchange.publish(                                                         # отправляем нужному клиенту сообщение, задав discon_id, чтоб знать, что это именно сообщение-отключение
                                Message(
                                    body=f"Отключение по команде пользователя {current_client.login}".encode(),
                                    correlation_id=client_to_discon.discon_id,
                                ),
                                routing_key=client_to_discon.queue,

                            )
                            answer = "Клиент отключен"
                            clients_connections.remove(client_to_discon)                                    # после этого удаляем клиента из списка с подключенными клиентами
                            print(f"Клиент {client_to_discon.login} отключен....")
                        else:
                            answer = "Данный клиент не подключен"
                    else:
                        answer = "Эта операция доступна только админам"

                await exchange.publish(                                                                     # отправка ответ клиенту, который прислал запрос
                        Message(
                            body=json.dumps(answer, cls=BookJson).encode(),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=current_client.queue,
                    )


async def connection_handler(message: AbstractIncomingMessage):                                             # обработака подключений клиентов
    data = json.loads(message.body.decode())                                                                # подгружаем данные
    global clients_connections

    if data["connect"]:                                                                                     # если запрос на подключение
        if get_client_by_login(data["login"]) in clients_connections:                                       # проверяем, не подключен ли уже клиент
            answer = {"info": "Этот пользователь в данный момент уже авторизирован", "success": False}
            await exchange.publish(
                Message(body=json.dumps(answer).encode(),
                        correlation_id=data["connect_corid"]),
                routing_key=data["queue"]
            )
            return

        success, user = check_login(data["login"], data["passwd"])                                          # аутентификация и авторизация

        if not success:                                                                                     # если логин и пароль не подходят
            answer = {"info": "Пользователь с таким логином и паролем не найден", "success": False}
            await exchange.publish(
                Message(body=json.dumps(answer).encode(),
                        correlation_id=data["connect_corid"]),
                routing_key=data["queue"]
            )
            return

        if success:                                                                                         # если успшено зашли
            print(f"Клиент {user.login} подключился")
            user.set_conn_info(data["queue"], data["disconnect_corid"])                                     # подгружаем данные о подключение из сообщения
            clients_connections.append(user)                                                                # добавляем клиента в список подключенных
            answer = {"info": "Авторизация пройдена", "success": True, "is_admin": user.is_admin}
            await exchange.publish(
                Message(body=json.dumps(answer).encode(),
                        correlation_id=data["connect_corid"]),
                routing_key=data["queue"]
            )
            return
    else:                                                                                                   # иначе пришел запрос на отключение
        client = get_client_by_queue(data["queue"])
        if client is not None:                                                                              # проверяем, точно ли пользователь подключен
            print(f"Клиент {client.login} отключен...")
            clients_connections.remove(client)                                                              # убираем клиента из списка подключенных


def get_client_by_login(login: str):                                                                        # полученние подключенного клиента по логину
    for client in clients_connections:
        if client.login == login:
            return client


def get_client_by_queue(queue: str):                                                                        # полученние подключенного клиента по его персональной очереди ответов на запросы
    for client in clients_connections:
        if client.queue == queue:
            return client


def check_login(login: str, passwd: str) -> (bool, User):                                                   # аутентификация
    session = session_fab()                                                                                 # пароль приходит уже захэшированный
    user = session.query(User).filter_by(login=login, passwd=passwd).first()
    return (user is not None, user)


def get_active_logins():                                                                                    # получение логинов активных клиентов
    answer = []
    for client in clients_connections:
        answer.append(client.login)
    return answer


def del_book(id):                                                                                           # Функция удаления книги, она получает номер удаляемой книги
    session = session_fab()
    book = session.query(Book).get(id)
    if book:
        session.delete(book)
        session.commit()
        return "Книга удалена"
    return "Такой книги не существует"                                                                      # Если такого номера в словаре не было - возвращаем текст об этом


def add_book(book):                                                                                         # Добавление книги, получаем объект книги в виде словаря
    msg=check_book(book)                                                                                    # Проверка, правильная ли книга
    if msg:                                                                                                 # Если есть текст по результатам проверки, значит, книга проверку не прошла
        return msg                                                                                          # Возвращаем сообщение
    book = Book(book["name"], book["author"], book["pages"])
    session = session_fab()
    session.add(book)                                                                                       # Добавляем книгу
    session.commit()
    return "Книга добавлена"


def check_book(book):                                                                                       # Проверка, правильная ли книга
    if book['author'].isdigit():                                                                            # Проверяем, содержит ли имя автора цифры
        return "Имя автора содержит цифры!"                                                                 # Возвращаем об этом сообщение
    return ""                                                                                               # Возвращаем пустое сообщение, если ошибок нет


def read_books():                                                                                           # Считываем список книг
    session = session_fab()
    return session.query(Book).all()


if __name__ == "__main__":
    procs = [p for p in psutil.process_iter() if 'python' in p.name() and Path(__file__).name in p.cmdline()[1]]         # проверяем (по активным процессам), чтоб был запущен только один экземпляр сервера
    if len(procs) > 1:
        print('Экземпляр сервера уже запущен')
        sys.exit(1)
    asyncio.run(start_server())
