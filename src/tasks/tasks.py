from tasks.brokers import redis_broker
from tasks.services import GreetingService


@redis_broker
async def greet(name: str) -> None:
    GreetingService().say_hello(name)
