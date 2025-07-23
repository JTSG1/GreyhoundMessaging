import json
from datetime import datetime
from greyhound_messaging.adapters._implementations.kafka_adapters import KafkaConsumerAdapter
from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot
from unittest.mock import MagicMock, patch
import pytest

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

def test_kafka_adapter_calls_consumer_method(valid_message):
    # Arrange
    mock_consumer = MagicMock(spec=GreyhoundConsumer)
    mock_msg = MagicMock()
    mock_msg.value.return_value = json.dumps(valid_message).encode("utf-8")
    mock_msg.error.return_value = None

    with patch("greyhound_messaging.adapters._implementations.kafka_adapters.Consumer") as MockKafkaConsumer:
        kafka_mock_instance = MockKafkaConsumer.return_value
        kafka_mock_instance.poll.side_effect = [mock_msg, KeyboardInterrupt]

        adapter = KafkaConsumerAdapter(
            consumer=mock_consumer,
            queue_name="test-topic",
            connection_params={
                "bootstrap.servers": "localhost:9092",
                "group.id": "test-group"
            }
        )

        # Act
        try:
            adapter.consume()
        except KeyboardInterrupt:
            pass  # simulate clean exit

        # Assert
        mock_consumer.message_received.assert_called_once()