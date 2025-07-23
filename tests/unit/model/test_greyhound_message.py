import pytest
from datetime import datetime
from pydantic import ValidationError
from copy import deepcopy

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
            "timestamp": datetime.utcnow(),
            "priority": 1,
            "retry_count": 0,
            "error_message": None,
            "custom_headers": {"header1": "value1"}
        }
    }


def test_message_parses_successfully(valid_message):
    msg = GreyhoundMessageRoot(**valid_message)

    assert msg.event_type == "test.event"
    assert msg.is_dry_run is False
    assert msg.payload["data"] == "test"
    assert msg.stages[0].destination == "service-X"
    assert msg.metadata.correlation_id == "12345"
    assert msg.metadata.priority == 1


def test_missing_required_field_raises(valid_message):
    broken = deepcopy(valid_message)
    del broken["event_type"]

    with pytest.raises(ValidationError):
        GreyhoundMessageRoot(**broken)


def test_invalid_payload_type_raises(valid_message):
    broken = deepcopy(valid_message)
    broken["payload"] = "should-be-dict"

    with pytest.raises(ValidationError):
        GreyhoundMessageRoot(**broken)


def test_invalid_is_dry_run_type_raises(valid_message):
    broken = deepcopy(valid_message)
    broken["is_dry_run"] = "not-a-bool"

    with pytest.raises(ValidationError):
        GreyhoundMessageRoot(**broken)


def test_default_values_populated_when_omitted():
    msg = GreyhoundMessageRoot(
        event_type="default.test",
        payload={"x": 1},
        metadata={
            "correlation_id": "12345",
            "message_id": "msg-123",
            "timestamp": datetime.utcnow(),
            "priority": 1,
            "retry_count": 0,
            "error_message": None,
            "custom_headers": {"header1": "value1"}
        }
    )

    assert msg.is_dry_run is False
    assert msg.metadata.retry_count == 0
    assert isinstance(msg.metadata.custom_headers, dict)
    assert msg.stages == []
    assert msg.metadata.timestamp is not None