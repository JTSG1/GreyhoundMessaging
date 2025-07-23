from unittest.mock import MagicMock

import pika
import pytest
from greyhound_messaging.adapters.adapter_factory import adapter_factory_consumer, adapter_factory_producer
from greyhound_messaging.adapters._implementations.rabbitmq_adapters import RabbitMQBlockingConsumerAdapter, RabbitMQBlockingProducerAdapter

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
def config_fixture_invalid_backend():
    return {
    "producer" : {
        "backend": "SOME_UNKNOWN_BACKEND",
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
        "backend": "SOME_UNKNOWN_BACKEND",
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


def test_adapter_factory_creates_rabbitmq_blocking_consumer_adapter(config_fixture):
    # Arrange
    mock_consumer = MagicMock()
    mock_params = pika.ConnectionParameters("localhost")

    # Act
    adapter = adapter_factory_consumer(
        consumer=mock_consumer,
        configuration_properties=config_fixture
    )

    # Assert
    assert isinstance(adapter, RabbitMQBlockingConsumerAdapter)
    assert adapter.queue_name == "default_consumer_queue"
    assert adapter.consumer == mock_consumer

def test_adapter_factory_raises_value_error_for_unknown_consumer_adapter_type(config_fixture_invalid_backend):
    # Arrange
    mock_consumer = MagicMock()

    # Act & Assert
    with pytest.raises(ValueError, match="Unknown consumer adapter type: SOME_UNKNOWN_BACKEND"):
        adapter_factory_consumer(
            consumer=mock_consumer,
            configuration_properties=config_fixture_invalid_backend
        )

def test_adapter_factory_creates_rabbitmq_blocking_producer_adapter(config_fixture):
    # Arrange
    mock_params = pika.ConnectionParameters("localhost")

    # Act
    adapter = adapter_factory_producer(
        configuration_properties=config_fixture
    )

    # Assert
    assert isinstance(adapter, RabbitMQBlockingProducerAdapter)
    assert adapter.queue_name == "default_producer_queue"

def test_adapter_factory_raises_value_error_for_unknown_producer_adapter_type(config_fixture_invalid_backend):
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown producer adapter type: SOME_UNKNOWN_BACKEND"):
        adapter_factory_producer(
            configuration_properties=config_fixture_invalid_backend
        )