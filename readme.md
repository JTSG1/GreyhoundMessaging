# Greyhound Messaging Library

Greyhound is a messaging abstraction library designed for event-based microservices. It supports multiple messaging backends (e.g. RabbitMQ, Kafka) and provides a CLI for validating and testing configurations with minimal setup.

## 🔧 CLI Usage

```bash
greyhound --config /path/to/config.yaml
```

The CLI allows you to run consumer/producer pairs defined via YAML config, making it ideal for integration testing or lightweight orchestration.

## ⚙️ Configuration Format

Configuration is YAML-based, with a `producer` and `consumer` section. Each defines:

- `backend`: which system to use (`RABBITMQ`, `KAFKA`)
- `queue`: the queue or topic name
- `connection_params`: backend-specific connection details

### 🐰 Example: RabbitMQ → RabbitMQ

```yaml
producer:
  backend: RABBITMQ
  queue: default_producer_queue
  connection_params:
    host: localhost
    port: 5672
    virtual_host: /
    credentials:
      username: guest
      password: guest

consumer:
  backend: RABBITMQ
  queue: default_consumer_queue
  connection_params:
    host: localhost
    port: 5672
    virtual_host: /
    credentials:
      username: guest
      password: guest
```

### 🦄 Example: Kafka → Kafka

```yaml
producer:
  backend: KAFKA
  queue: default_producer_queue
  connection_params:
    bootstrap_servers: localhost:9092
    group_id: test-consumer-group

consumer:
  backend: KAFKA
  queue: default_consumer_queue
  connection_params:
    bootstrap_servers: localhost:9092
    group_id: test-consumer-group
```

### 🔁 Mixed Example: Kafka → RabbitMQ

```yaml
producer:
  backend: KAFKA
  queue: default_producer_queue
  connection_params:
    bootstrap_servers: localhost:9092
    group_id: test-consumer-group

consumer:
  backend: RABBITMQ
  queue: default_consumer_queue
  connection_params:
    host: localhost
    port: 5672
    virtual_host: /
    credentials:
      username: guest
      password: guest
```

Greyhound supports cross-protocol messaging out of the box — no glue code required.

## 📦 Message Schema

All messages follow a standard structure (`GreyhoundMessageRoot`) with embedded stages and custom payloads.

```json
{
  "event_type": "test.event",
  "is_dry_run": false,
  "stages": [
    {
      "destination": "service-X",
      "inputs": {"key": "value"},
      "outputs": {"result": "success"},
      "parameters": {"param1": "value1"}
    }
  ],
  "payload": {
    "data": "test"
  },
  "metadata": {
    "correlation_id": "12345",
    "message_id": "msg-123",
    "timestamp": "2023-10-01T12:00:00Z",
    "priority": 1,
    "retry_count": 0,
    "error_message": "",
    "custom_headers": {
      "header1": "value1"
    }
  }
}
```

The `payload` field is free-form and can contain domain-specific data.

## 📁 See Also

- `example_configs/`: more configuration variants
- CLI help: `greyhound --help`