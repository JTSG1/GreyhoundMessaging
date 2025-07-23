
from curses import raw

from pydantic import ValidationError
from greyhound_messaging.adapters._abstracts.core_messaging import ConsumerMessageAdapter, ProducerMessageAdapter
from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot
import pika
import json

class RabbitMQBlockingConsumerAdapter(ConsumerMessageAdapter):
    """
    RabbitMQ implementation of the ConsumerMessageAdapter.
    """
    def __init__(
            self, 
            consumer: GreyhoundConsumer, 
            queue_name: str,
            connection_params: pika.ConnectionParameters
            ):
        """
        Initialize the RabbitMQ consumer adapter with connection parameters.
        
        :param connection_params: Parameters for connecting to RabbitMQ.
        """
        self.connection_params: pika.ConnectionParameters = connection_params
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue_name)
        self.consumer = consumer

    @classmethod
    def from_config(cls, consumer: GreyhoundConsumer, config: dict):
        """
        Create an instance of RabbitMQBlockingConsumerAdapter from configuration.
        
        :param consumer: The GreyhoundConsumer instance to use.
        :param queue_name: The name of the RabbitMQ queue to consume from.
        :return: An instance of RabbitMQBlockingConsumerAdapter.
        """

        connection_params = pika.ConnectionParameters(
            host = config.get("host", "localhost"),
            port = config.get("port", 5672),
            virtual_host = config.get("virtual_host", "/"),
            credentials = pika.PlainCredentials(
                username = config.get("credentials", {}).get("username", "guest"),
                password = config.get("credentials", {}).get("password", "guest")
            )
        )

        return cls(consumer, config.get("queue"), connection_params)

    def consume(self) -> GreyhoundMessageRoot:
        """
        Consume a message from RabbitMQ.
        """
        self.channel.basic_consume(queue=self.queue_name,
                      auto_ack=False,
                      on_message_callback=self.message_received)
        self.channel.start_consuming()

    def message_received(self, ch, method, properties, body):
        """
        Callback for when a message is received.
        """
        try:
            raw = json.loads(body.decode("utf-8"))
            greyhound_message = GreyhoundMessageRoot(**raw)
        except (json.JSONDecodeError, ValidationError) as e:
            # Log or push to DLQ
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        self.consumer.message_received(greyhound_message)
        ch.basic_ack(delivery_tag=method.delivery_tag)


class RabbitMQBlockingProducerAdapter(ProducerMessageAdapter):
    """
    RabbitMQ implementation of the ProducerMessageAdapter.
    """

    def __init__(
            self, 
            queue_name: str,
            connection_params: pika.ConnectionParameters,
            ):
        """
        Initialize the RabbitMQ producer adapter with connection parameters.
        
        :param connection_params: Parameters for connecting to RabbitMQ.
        """
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.channel.queue_declare(queue_name)

    @classmethod
    def from_config(cls, config: dict):
        """
        Create an instance of RabbitMQBlockingProducerAdapter from configuration.
        
        :param config: Configuration dictionary containing connection parameters and queue name.
        :return: An instance of RabbitMQBlockingProducerAdapter.
        """
        connection_params = pika.ConnectionParameters(
            host = config.get("host", "localhost"),
            port = config.get("port", 5672),
            virtual_host = config.get("virtual_host", "/"),
            credentials = pika.PlainCredentials(
                username = config.get("credentials", {}).get("username", "guest"),
                password = config.get("credentials", {}).get("password", "guest")
            )
        )
        return cls(queue_name=config.get("queue"), connection_params=connection_params)

    def produce(self, message: GreyhoundMessageRoot):
        """
        Produce a message to RabbitMQ.
        """
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=message.model_dump_json())
