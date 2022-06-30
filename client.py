import asyncio
import uuid
from typing import MutableMapping
from classes.book import *
import aioconsole
import signal
from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue,
)
from hashlib import sha256


class RpcClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    stop_server_queue: AbstractQueue
    connections_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self) -> None:
        self.futures: MutableMapping[str, asyncio.Future] = {}
        self.loop = asyncio.get_running_loop()
        self.disconnect_corid = str(uuid.uuid4())                                                                       # используется для опознавания сообщения с указанием отключится
        self.connect_corid = str(uuid.uuid4())                                                                          # используется для опознавания сообщения с ответом на запрос подключения
        self.is_connected = False
        self.is_admin = False

    async def connect(self, login, passwd) -> "RpcClient":
        self.connection = await connect(
            host="127.0.0.1", loop=self.loop,
        )
        self.channel = await self.connection.channel()

        self.callback_queue = await self.channel.declare_queue(exclusive=True)                                          # очередь, в которую приходят сообщения от сервера
        await self.callback_queue.consume(self.on_response)

        self.stop_server_queue = await self.channel.declare_queue("stop_server", exclusive=False, durable=False)        # очередь, в которую приходят сообщения об откобчение сервера
        await self.stop_server_queue.consume(self.on_server_stop, no_ack=True)

        self.connections_queue = await self.channel.declare_queue("connections_queue", exclusive=False, durable=False)  # очередь, в которую клиенты сообщают серверу о подключении и отключении

        await self.conn_alert(login, passwd)                                                                            # отправляем серверу запрос на подключение

        return self

    async def conn_alert(self, login, passwd):
        conn_args = {"login": login, "passwd": passwd, "queue": self.callback_queue.name, "connect_corid": self.connect_corid, "disconnect_corid": self.disconnect_corid, "connect": True}

        await self.channel.default_exchange.publish(                                                                    # отправляем все необходимые для аутентификации данные
            Message(body=json.dumps(conn_args).encode()),
            routing_key=self.connections_queue.name
        )

    async def disconn_alert(self):
        conn_args = {"queue": self.callback_queue.name, "connect": False}

        await self.channel.default_exchange.publish(                                                                    # отправка сообщения серверу об отключении клиента
            Message(body=json.dumps(conn_args).encode()),
            routing_key=self.connections_queue.name
        )

    def on_response(self, message: AbstractIncomingMessage) -> None:                                                    # обрботчик "персональных" сообщений клиенту от сервера
        if message.correlation_id is None:                                                                              # если нету correlation_id, то не можем опознать сообщение
            print(f"Не удалось обработать сообщение...")
            return

        if message.correlation_id == self.disconnect_corid:                                                             # если сообщение с указанием отключится
            print("Принудительное отключение...")
            self.is_connected = False
            self.loop.stop()
            return

        if message.correlation_id == self.connect_corid:                                                                # сообщение с ответом на попытку аутентификации
            data = json.loads(message.body.decode())
            print(data["info"])
            if not data["success"]:
                self.loop.stop()
                return
            else:
                self.is_connected = True
                self.is_admin = data["is_admin"]
                return

        future: asyncio.Future = self.futures.pop(message.correlation_id)                                               # если сообщение не о подключении/отключении, то это просто ответ на какой-то
        future.set_result(message.body)                                                                                 # пользовательский запрос серверу и с помощью correlation_id узнаем на какой именно

    def on_server_stop(self, message: AbstractIncomingMessage):                                                         # обработчки сообщений об отключении сервера
        print(message.body.decode())
        self.is_connected = False
        self.loop.stop()

    async def call(self, msg: json) -> str:                                                                             # отправка запроса сервера
        correlation_id = str(uuid.uuid4())                                                                              # генерируем uuid, для последующей однозначной идентификации ответа
        future = self.loop.create_future()
        self.futures[correlation_id] = future                                                                           # создаем фьючер и помещаем его в словарь

        await self.channel.default_exchange.publish(                                                                    # отправка серверу сообщения с запросом
            Message(
                json.dumps(msg, cls=BookJson).encode(),
                content_type="text",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name
            ),
            routing_key="rpc_queue"
        )
        return await future                                                                                             # ждем результат и получаем значение фьючура с помощью его id


client: RpcClient


async def main() -> None:

    print("Введите логин")
    login = input()
    print("Введите пароль")
    passwd = sha256(input().encode()).hexdigest()                # пароль передаем уже захэшированным, чтоб не кидать в открытую очередь пароль в "чистом виде"

    global client
    client = await RpcClient().connect(login, passwd)           # подключаемся

    connect_timer = 0                                           # счетчик ожидания ответа на запрос аутитентификации сервером
    while not client.is_connected:                              # пока подключение не подтвержденно, просто ждем ответа
        await asyncio.sleep(0.5)
        connect_timer += 0.5                                    # если 5 секунд нету ответа, то сервер выключен, выходим из программы
        if connect_timer == 5:
            print("Похоже, что сервер данный момент не активен. Повторите попытку позже")
            await client.disconn_alert()                        # все равно отправляем серверу сообщение об отключение, т.к. при включение он отработает попытку аутентификации
            asyncio.get_event_loop().stop()

    while client.is_connected:                                  # цикл, в котором клиент формирует свои запросы

        render_commands(client.is_admin)                        # выводим доступные действия

        task = await aioconsole.ainput()                        # асинхронно ждем ввода команды

        if not task.isdigit() or \
                (not client.is_admin and int(task) > 4) or\
                (client.is_admin and int(task) > 6):                # Если ввод пользователя содержит что-то кроме цифр или нету такой команды
            print("Неправильная команда!")
            continue                                                # В этом случае начинаем цикл заново, пусть пользователь заново вводит текст

        task = int(task)

        msg = {}  # Создаем пустой словарь

        if task == 0:
            msg["command"] = "read"
        if task == 1:
            msg["command"] = "add"
            msg["object"] = await create_book()             # Объект, передававаемый серверу, будет книгой, которую создаст процедура create_book()
        if task == 2:
            msg["command"] = "del"
            msg["object"] = await get_id()                  # Объект, передававаемый серверу, будет номером, который пользователь введет в процедуре get_id()
        if task == 3:
            msg["command"] = "clients"
        if task == 4:
            msg["command"] = "bye"
        if task == 5:
            msg["command"] = "stop"
        if task == 6:
            msg["command"] = "disconnect"
            print("Кого отключить?")
            msg["object"] = await aioconsole.ainput()       # Объект, передававаемый серверу, будет логином клиента, которого надо отключить

        response = await client.call(msg)                   # отправляем сообщение с командой серверу и ждем ответ
        content = {}  # Создаем пустой словарь Python

        try:                                                # Пытаемся преобразоывать данные
            content = json.loads(response)                  # Преобразываем данные из строки в формат словаря
        except Exception as error:                          # Преобразование не получилось - возникла ошибка
            print("Ошибка получения данных от сервера: ", error)
            print("Клиент выключается...")
            await client.disconn_alert()
            client.loop.stop()
            return

        # Начинаем обработку данных, полученных от сервера
        if task == 0:
            if content:                                             # Если словарь с данным от сервера не пустой
                print(content[0]['id'])
                print_books(BookJson.from_json(content))            # Печатаем список книг
            else:
                print("Список пуст")
        if task == 1:
            print(content)                                          # Печатаем полученный ответ на экране
        if task == 2:
            print(content)
        if task == 3:
            print_clients(content)                                  # выводим всех активных клиентов
        if task == 4:
            print("Клиент выключается...")
            await client.disconn_alert()                            # при запросе на добровольное отключение, сообщаем серверу об отключение
            client.loop.stop()
            return
        if task == 5:
            print(content)
        if task == 6:
            print(content)


def render_commands(is_admin: bool):                                # вывод доступных пользователю команд
    print("Что делаем?")
    print("0 - Просмотреть список книг")
    print("1 - Добавить книгу")
    print("2 - Удалить книгу")
    print("3 - Список активных пользователей")
    print("4 - Выйти из программмы")
    if is_admin:
        print("5 - Выключить сервер")
        print("6 - Отключить пользователя")


def print_clients(clients):                                         # вывод всех активных клиентов
    for c in clients:
        print(c)


def print_books(books):                                             # выводит список книг на экран
    print ("="*15)
    for i in books:
        print ("%s - %s - %s - %s" % (i.id, i.name, i.author, i.pages))
    print ("="*15)


async def create_book():                                            # Создаем объект книги
    print("Введите название книги:")
    name = await aioconsole.ainput()
    print("Введите автора книги:")
    author = await aioconsole.ainput()
    print("Введите количество страниц книги:")
    pages = await aioconsole.ainput()

    book = Book(name, author, int(pages))
    return book


async def get_id():                                                 # получаем от пользователя номер удаляемой книги
    while True:                                                     # Бесконечный цикл, пока пользователь не введет правильный номер
        print("Введите номер книги:")
        id = await aioconsole.ainput()
        if id.isdigit():
            return id                                               # Возвращаем id
        print ("Неправильный номер")                                # Пишем, что номер неправильный и цикл повторяется


async def signal_handler(signal):                                   # обработка сигналы о выходе из программы не с помощью специальной команды,
    try:
        await client.disconn_alert()                                # чтоб все равно уведомить сервер об отключении
        client.loop.stop()
    except NameError:                                               # если пытаемся закрыть программу до объявления пользователя (ввод логина и пароля)
        asyncio.get_event_loop().stop()


if __name__ == "__main__":
    asyncio.ensure_future(main())
    event_loop = asyncio.get_event_loop()

    for signame in ('SIGINT', 'SIGTERM'):                           # вешаем перехват сигналов SIGINT и SIGTERM
        event_loop.add_signal_handler(getattr(signal, signame),
                                lambda signame=signame: asyncio.create_task(signal_handler(signame)))

    event_loop.run_forever()