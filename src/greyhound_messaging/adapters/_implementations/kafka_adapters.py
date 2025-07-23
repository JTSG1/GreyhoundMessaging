from pydantic import ValidationError
from greyhound_messaging.adapters._abstracts.core_messaging import ConsumerMessageAdapter, ProducerMessageAdapter
from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot
from confluent_kafka import Consumer, Producer
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaConsumerAdapter(ConsumerMessageAdapter):
    """
    Kafka implementation of the ConsumerMessageAdapter.
    """
    def __init__(
            self, 
            consumer: GreyhoundConsumer, 
            queue_name: str,
            connection_params: dict
            ):
        """
        Initialize the Kafka consumer adapter with connection parameters.
        
        :param connection_params: Parameters for connecting to Kafka.
        """
        self.consuming_object = consumer
        self.queue_name = queue_name
        self.kafka_consumer = Consumer(connection_params)

    @classmethod
    def from_config(cls, consumer: GreyhoundConsumer, config: dict):
        """
        Create an instance of RabbitMQBlockingConsumerAdapter from configuration.
        
        :param consumer: The GreyhoundConsumer instance to use.
        :param queue_name: The name of the RabbitMQ queue to consume from.
        :return: An instance of RabbitMQBlockingConsumerAdapter.
        """

        connection_params = {
            'bootstrap.servers': config.get("bootstrap_servers", "localhost:9092"),
            'group.id': config.get("group_id", "greyhound_group"),
            'auto.offset.reset': config.get("auto_offset_reset", "earliest"),
            'enable.auto.commit': config.get("enable_auto_commit", False),
        }

        return cls(consumer, config.get("queue"), connection_params)

    def consume(self) -> GreyhoundMessageRoot:
        """
        Consume a message from RabbitMQ.
        """
        self.kafka_consumer.subscribe([self.queue_name])
        while True:
            msg = self.kafka_consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise Exception(f"Error consuming message: {msg.error()}") 
            try:
                raw = json.loads(msg.value().decode("utf-8"))
                greyhound_message = GreyhoundMessageRoot(**raw)
                self.consuming_object.message_received(greyhound_message)
                self.kafka_consumer.commit()
                return greyhound_message
            except (json.JSONDecodeError, ValidationError) as e:
                # Log or push to DLQ
                logging.error(f"Error decoding message: {e}")
            
            return None


class KafkaProducerAdapter(ProducerMessageAdapter):
    """
    RabbitMQ implementation of the ProducerMessageAdapter.
    """

    def __init__(
            self, 
            queue_name: str,
            connection_params: dict,
            ):
        """
        Initialize the Kafka producer adapter with connection parameters.
        
        :param connection_params: Parameters for connecting to Kafka.
        """
        self.queue_name = queue_name
        self.producer = Producer(connection_params)
        self.flush_every = connection_params.get("flush_every", 1000)
        self.producer_msg_count = 0

    @classmethod
    def from_config(cls, config: dict):
        """
        Create an instance of KafkaProducerAdapter from configuration.

        :param config: Configuration dictionary containing connection parameters and topic name.
        :return: An instance of KafkaProducerAdapter.
        """
        connection_params = {
            'bootstrap.servers': config.get("bootstrap_servers", "localhost:9092"),
            'client.id': config.get("client_id", "greyhound_producer"),
            'enable.auto.commit': False,
        }
        
        return cls(queue_name=config.get("queue"), connection_params=connection_params)

    def produce(self, message: GreyhoundMessageRoot):
        """
        Produce a message to Kafka.
        """
        try:
            raw = message.model_dump_json()
            self.producer.produce(self.queue_name, value=raw.encode("utf-8"))
            # flush here is not scalable and should be changed to a more efficient batching mechanism
            self.producer_msg_count += 1
            if self.producer_msg_count == self.flush_every:
                self.producer.flush()
                self.producer_msg_count = 0
        except Exception as e:
            # Log or push to DLQ
            raise Exception(f"Error producing message: {e}")

    def flush_all(self):
        self.producer.flush()