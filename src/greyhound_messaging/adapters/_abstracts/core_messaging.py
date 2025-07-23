from abc import ABC, abstractmethod

from greyhound_messaging.model import GreyhoundMessageRoot

class ConsumerMessageAdapter(ABC):
    """
    Abstract base class for consumer message adapters.
    This class defines the interface for consuming messages from a messaging system.
    """

    @abstractmethod
    def consume(self, callback) -> GreyhoundMessageRoot:
        """
        Consume a message from the messaging system.
        
        :param message: The message to be consumed.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

        """
        Acknowledge that a message has been successfully processed.
        
        :param message: The message to acknowledge.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

class ProducerMessageAdapter(ABC):
    """
    Abstract base class for producer message adapters.
    This class defines the interface for producing messages to a messaging system.
    """

    @abstractmethod
    def produce(self, message: GreyhoundMessageRoot):
        """
        Produce a message to the messaging system.
        
        :param message: The message to be produced.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
class BufferedProducerMessageAdapter(ProducerMessageAdapter):
    """
    Abstract base class for buffered producer message adapters.
    This class extends the ProducerMessageAdapter to include buffering functionality.
    """
    @abstractmethod
    def add_to_buffer(self, message: GreyhoundMessageRoot):
        """
        Add a message to the buffer for later production.
        
        :param message: The message to be added to the buffer.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    

    @abstractmethod
    def flush(self):
        """
        Flush any buffered messages to the messaging system.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")