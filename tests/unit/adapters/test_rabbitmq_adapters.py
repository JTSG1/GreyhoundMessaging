from unittest.mock import MagicMock

import pytest
from greyhound_messaging.adapters._implementations.rabbitmq_adapters import RabbitMQBlockingConsumerAdapter
import pika
from datetime import datetime
import json

from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot

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

def test_adapter_init_with_mocked_connection_params():
    # Arrange
    mock_consumer = MagicMock()
    mock_params = pika.ConnectionParameters("localhost")  # use a real one
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    # Inject into BlockingConnection manually (replace constructor after import)
    pika.BlockingConnection = MagicMock(return_value=mock_connection)
    mock_connection.channel.return_value = mock_channel

    # Act
    adapter = RabbitMQBlockingConsumerAdapter(
        consumer=mock_consumer,
        queue_name="test-queue",
        connection_params=mock_params
    )

    # Assert
    assert adapter.queue_name == "test-queue"
    assert adapter.consumer == mock_consumer

def test_adapter_calls_consumer_method(valid_message):
    # Arrange
    mock_consumer = MagicMock()
    mock_params = pika.ConnectionParameters("localhost")
    mock_connection = MagicMock()
    mock_channel = MagicMock()

    pika.BlockingConnection = MagicMock(return_value=mock_connection)
    mock_connection.channel.return_value = mock_channel

    adapter = RabbitMQBlockingConsumerAdapter(
        consumer=mock_consumer,
        queue_name="test-queue",
        connection_params=mock_params
    )

    # Act
    adapter.message_received(
        ch=mock_channel,
        method=MagicMock(delivery_tag=1),
        properties=None,
        body=json.dumps(valid_message).encode("utf-8")
    )

    # Assert
    mock_consumer.message_received.assert_called_once()