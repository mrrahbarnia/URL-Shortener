import typing as T

from confluent_kafka.aio import AIOProducer

from src.core.config import ENVS

KAFKA_CFG = {
    "bootstrap.servers": "kafka:9092",
    "client.id": ENVS.KAFKA.URL_SHORTENER_PRODUCER_CLIENT_ID,
}


class KafkaProducer:
    def __init__(self, producer: AIOProducer | None = None) -> None:
        self.producer = producer

    async def start(self) -> None:
        if self.producer is None:
            self.producer = AIOProducer(KAFKA_CFG)

    async def stop(self) -> None:
        if self.producer is not None:
            await self.producer.flush()
            await self.producer.close()
            self.producer = None

    async def send_message(self, topic: str, key: str | None, value: str) -> T.Any:
        if self.producer is None:
            raise RuntimeError(
                "Kafka producer not started, first call start() during app startup."
            )
        delivery_future = await self.producer.produce(topic=topic, key=key, value=value)
        return await delivery_future


PRODUCER = KafkaProducer()
