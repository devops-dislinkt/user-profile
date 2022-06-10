from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import threading
import json
from user_profile_service import config
from . import profile_service
from flask import current_app, Flask


class ConsumerThread(threading.Thread):
    def __init__(self, app: Flask):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.app = app

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.create_topic()
        consumer = KafkaConsumer(
            bootstrap_servers=config.KAFKA_1,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        consumer.subscribe(config.KAFKA_TOPIC)
        for message in consumer:
            with self.app.app_context():
                current_app.logger.info(
                    "Received message with username : %s", message.value["username"]
                )

                if message.value.get("username") and message.value.get("new_username"):
                    old_username, new_username = (
                        message.value["username"],
                        message.value["new_username"],
                    )
                    profile_service.update_username(old_username, new_username)
                elif message.value.get("username"):
                    profile_service.create_profile(message.value["username"])
                else:
                    current_app.logger.error("empty message received.")

    def create_topic(self):
        admin_client = KafkaAdminClient(
            bootstrap_servers=config.KAFKA_1, client_id="test"
        )
        topic = NewTopic(
            name=config.KAFKA_TOPIC, num_partitions=1, replication_factor=1
        )
        try:
            admin_client.create_topics(new_topics=[topic], validate_only=False)
        except Exception as e:
            with self.app.app_context():
                current_app.logger.error("Failed to add topic reason: {}".format(e))
