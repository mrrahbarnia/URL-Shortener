from confluent_kafka.admin import AdminClient, NewTopic  # type: ignore


def create_topics() -> None:
    admin = AdminClient({"bootstrap.servers": "kafka:9092"})
    topic = NewTopic(
        topic="url-shortener.link.visited",
        num_partitions=9,
        replication_factor=1,
        config={"min.insync.replicas": "1"},
    )

    fs = admin.create_topics([topic])  # type: ignore

    for topic, f in fs.items():  # type: ignore
        try:
            f.result()
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
