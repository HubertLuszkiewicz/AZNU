from enum import Enum

class Queues(str, Enum):
    LOGISTICS = "logistics_queue"

class Statuses(str, Enum):
    STARTED = "started"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RabbitConfig:
    HOST = 'localhost'
    PORT = 5672