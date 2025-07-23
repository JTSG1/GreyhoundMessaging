
from unittest.mock import MagicMock
import pika
import pytest
from greyhound_messaging.adapters.adapter_factory import adapter_factory_consumer
from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
import json

from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot


class SimpleRabbitMQBlockingConsumer(GreyhoundConsumer):

    def __init__(self):
        super().__init__()
        self.was_message_received = False

    def message_received(self, message: GreyhoundMessageRoot) -> GreyhoundMessageRoot:
        
        self.was_message_received = True

        return message

@pytest.fixture
def config_fixture():
    return {
    "producer" : {
        "backend": "RABBITMQ",
        "host": "localhost",
        "port": 5672,
        "queue": "default_producer_queue",
        "connection_params": {
            "host": "localhost",
            "port": 5672,        
            "virtual_host": '/',
            "credentials": {
                "username": "guest",    
                "password": "guest"
            }
        }
    },
    "consumer": {
        "backend": "RABBITMQ",
        "host": "localhost",
        "port": 5672,
        "queue": "default_consumer_queue",
        "connection_params": {
            "host": "localhost",
            "port": 5672,        
            "virtual_host": '/',
            "credentials": {
                "username": "guest",    
                "password": "guest"
            }
        }
    }
}

@pytest.fixture
def valid_message():
    return {
        "event_type": "test.event",
        "is_dry_run": False,
        "stages": [
            {
                "destination": "service-X",
                "inputs": {"key": "value"},
                "outputs": {"result": "success"},
                "parameters": {"param1": "value1"}
            }
        ],
        "payload": {"data": "test"},
        "metadata": {
            "correlation_id": "12345",
            "message_id": "msg-123",
            "timestamp": "2023-10-01T12:00:00Z",
            "priority": 1,
            "retry_count": 0,
            "error_message": "",
            "custom_headers": {"header1": "value1"}
        }
    }

def test_simple_rabbitmq_blocking_consumer(config_fixture, valid_message):

    # Arrange
    consumer = SimpleRabbitMQBlockingConsumer()
    
    adapter = adapter_factory_consumer(
        consumer=consumer,
        configuration_properties=config_fixture
    )

    mock_params = pika.ConnectionParameters("localhost")
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    # Act
    adapter.message_received(
        ch=mock_channel,
        method=MagicMock(delivery_tag=1),
        properties=None,
        body=json.dumps(valid_message).encode("utf-8")
    )

    # Assert
    consumer.message_received = True