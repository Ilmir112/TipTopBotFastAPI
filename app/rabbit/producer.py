

from app.config import settings, router_broker
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


async def send_message_to_queue(body: str, QUEUE_NAME: str):
    try:
        result = await router_broker.publish(body, QUEUE_NAME)

        return {"data": "OK"}
    except Exception as e:
        logger.critical(e)
        return {"error": str(e)}