

from faststream.rabbit import RabbitBroker
from app.config import settings
from app.logger import logger

# @broker.get("/send_messenger")
# async def send_message_to_queue(body: str, QUEUE_NAME: str):
#
#     # Подключение к RabbitMQ
#     try:
#         await broker.broker.publish(
#             exchange="",
#             routing_key=QUEUE_NAME,
#             message=body
#         )
#         return {"data": "OK"}
#     except Exception as e:
#         logger.critical(e)


async def send_message_to_queue(router_broker_instance, body: str, QUEUE_NAME: str):
    try:
        result = await router_broker_instance.publish(body, QUEUE_NAME)

        return {"data": "OK"}
    except Exception as e:
        logger.critical(e)
        return {"error": str(e)}