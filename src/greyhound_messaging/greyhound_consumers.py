from abc import ABC, abstractmethod

from greyhound_messaging.adapters._abstracts.core_messaging import ConsumerMessageAdapter
from greyhound_messaging.model.greyhound_message import GreyhoundMessageRoot

class GreyhoundConsumer(ABC):

    def __init__(self):
        pass

    def message_received(self, message: GreyhoundMessageRoot) -> GreyhoundMessageRoot:

        return message

