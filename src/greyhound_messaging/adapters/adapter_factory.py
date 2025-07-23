from greyhound_messaging.adapters._implementations.kafka_adapters import KafkaConsumerAdapter, KafkaProducerAdapter
from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
from greyhound_messaging.adapters._implementations.rabbitmq_adapters import RabbitMQBlockingConsumerAdapter, RabbitMQBlockingProducerAdapter
from greyhound_messaging.config import CONFIGURATION_PROPERTIES

adapters = {
    "RABBITMQ": {
        "consumer": RabbitMQBlockingConsumerAdapter,
        "producer": RabbitMQBlockingProducerAdapter
    },
    "KAFKA": {
        "consumer": KafkaConsumerAdapter,
        "producer": KafkaProducerAdapter
    }
}

def adapter_factory_consumer(consumer: GreyhoundConsumer, configuration_properties = CONFIGURATION_PROPERTIES):

    type = configuration_properties.get("consumer").get("backend")

    consumer_cls = adapters.get(type, {}).get("consumer")
    if consumer_cls is None:
        raise ValueError(f"Unknown consumer adapter type: {type}")

    return consumer_cls.from_config(consumer=consumer, config=configuration_properties["consumer"])

def adapter_factory_producer(configuration_properties = CONFIGURATION_PROPERTIES):

    type = configuration_properties.get("producer").get("backend")

    producer_cls = adapters.get(type, {}).get("producer")
    if producer_cls is None:
        raise ValueError(f"Unknown producer adapter type: {type}")
    return producer_cls.from_config(config=configuration_properties["producer"])