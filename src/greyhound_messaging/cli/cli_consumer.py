from greyhound_messaging.greyhound_consumers import GreyhoundConsumer
from greyhound_messaging.model import GreyhoundMessageRoot


class CliConsumer(GreyhoundConsumer):
    
    def __init__(self, producer=None):
        self.producer = producer
        super().__init__()
    
    def message_received(self, message: GreyhoundMessageRoot):
        # Implement your message processing logic here
        print(f"Processing message: {message.event_type}")
        self.producer.produce(message)
        print(f"Message produced: {message.event_type}")