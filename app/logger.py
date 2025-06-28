# Ваш обработчик логов
from app.config import settings

import threading
import asyncio
from queue import Queue
from aiogram import Bot
import logging


class TelegramSender:
    def __init__(self, token):
        self.bot = Bot(token)
        self.queue = Queue()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._worker)
        self.thread.daemon = True
        self.thread.start()

    def _worker(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._send_messages())

    async def _send_messages(self):
        while True:
            chat_id, text = self.queue.get()
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
            except Exception as e:
                # Обработка ошибок
                pass

    def send(self, chat_id, text):
        self.queue.put((chat_id, text))


class TelegramHandler(logging.Handler):
    def __init__(self, sender: TelegramSender, chat_id):
        super().__init__()
        self.sender = sender
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        # Помещаем сообщение в очередь для отправки
        self.sender.send(self.chat_id, log_entry)


# Инициализация
sender = TelegramSender(settings.TOKEN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

telegram_handler = TelegramHandler(sender, settings.CHAT_ID)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
telegram_handler.setFormatter(formatter)

logger.addHandler(telegram_handler)