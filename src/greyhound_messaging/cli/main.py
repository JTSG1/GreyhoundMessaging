import click
import yaml
from greyhound_messaging.adapters import adapter_factory_consumer, adapter_factory_producer
from greyhound_messaging.cli.cli_consumer import CliConsumer  # you wire this

@click.command()
@click.option('--config', type=click.Path(exists=True), required=True, help='Path to config YAML.')
def consume(config):
    """
    Start a greyhound consumer using the specified config.
    """
    with open(config, 'r') as f:
        config_data = yaml.safe_load(f)

    print(f"Config loaded successfully")
    print(f"Consumer backend: {config_data['consumer']['backend']}")
    print(f"Producer backend: {config_data['producer']['backend']}")

    producer = adapter_factory_producer(config_data)
    consumer = CliConsumer(producer=producer)
    adapter = adapter_factory_consumer(consumer, config_data)

    click.echo("Starting consumer loop. Press Ctrl+C to exit.")
    try:
        adapter.consume()
    except KeyboardInterrupt:
        click.echo("Shutdown requested. Cleaning up...")
        adapter.close()
        if hasattr(producer, "flush_all"):
            producer.flush_all()

if __name__ == '__main__':
    consume()