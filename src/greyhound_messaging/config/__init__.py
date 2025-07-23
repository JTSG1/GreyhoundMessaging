
# Configuration module for the project
# This file is used to manage configuration settings.
# This is a placeholder for the actual configuration settings.
# Will be replaced with actual configuration properties wrapped in pydantic models.

CONFIGURATION_PROPERTIES = {
    "producer" : {
        "backend": "RABBITMQ",
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
