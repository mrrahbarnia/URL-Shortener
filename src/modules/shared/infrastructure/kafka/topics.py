from confluent_kafka.admin import AdminClient, NewTopic  # type: ignore

from src.core.config import ENVS


def create_topics() -> None:
    admin = AdminClient({"bootstrap.servers": "kafka:9092"})
    topic = NewTopic(
        topic=ENVS.KAFKA.URL_SHORTENER_TOPIC_NAME,
        num_partitions=ENVS.KAFKA.URL_SHORTENER_TOPIC_NUM_PARTITIONS,
        replication_factor=ENVS.KAFKA.URL_SHORTENER_TOPIC_REPLICATION_FACTOR,
        config={
            "min.insync.replicas": str(
                ENVS.KAFKA.URL_SHORTENER_TOPIC_MIN_INSYNC_REPLICA
            )
        },
    )

    fs = admin.create_topics([topic])  # type: ignore

    for topic, f in fs.items():  # type: ignore
        try:
            f.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
