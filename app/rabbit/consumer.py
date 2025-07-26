from app.config import settings, router_broker

import asyncio
import aio_pika


@router_broker.subscriber("tiptop")
async def process_message(message: aio_pika.IncomingMessage):
    from app.main import bot

    async with message.process():  # автоматически подтверждает сообщение после блока
        body = message.body.decode()
        # print(f"Received message: {body}")

        await bot.send_message(
            chat_id=settings.CHAT_ID,
            text=body)

        # Здесь добавьте вашу логику обработки сообщения
        # Например, сохранить в базу, отправить уведомление и т.д.
        # После выхода из блока message.process() сообщение будет подтверждено и удалено из очереди

async def start_consumer():
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("tiptop", durable=True)

        # Запуск потребителя
        await queue.consume(process_message)

        print("Начинаю слушать очередь 'tiptop'...")
        # Чтобы слушать бесконечно, используем asyncio.Event()
        await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(start_consumer())
# Запуск потребителя в основном приложении или в отдельной задаче
# Например, в вашем основном файле:
# asyncio.create_task(consume_messages())
