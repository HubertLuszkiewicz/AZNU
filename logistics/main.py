import os
import pika
import json
import time
import redis
from Constants import Queues, Statuses, RabbitConfig

rabbit_config = RabbitConfig()

REDIS_HOST = os.getenv("REDIS_HOST", "redis") 
r = redis.Redis(host=REDIS_HOST, port=6379)

def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_config.HOST, rabbit_config.PORT))
    return connection.channel()


def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [Logistics] Otrzymano zlecenie: {data}")
    
    req_id = data['id']

    time.sleep(5)
    print(" [Logistics] Miejsce w magazynie zarezerwowane.")

    # Przekazanie do Compliance Service (sprawdzenie prawne)
    # Tu zaczyna się SAGA - krok kolejny
    channel = get_channel()
    channel.queue_declare(queue=Queues.COMPLIANCE)
    channel.basic_publish(exchange='', routing_key=Queues.COMPLIANCE, body=json.dumps(data))
    r.set(req_id, Statuses.PENDING)
    print(" [Logistics] Przekazano do działu prawnego (Compliance)")


def main():
    channel = get_channel()
    channel.queue_declare(queue=Queues.LOGISTICS)

    print(' [Logistics] Czekam na wiadomości...')
    channel.basic_consume(queue=Queues.LOGISTICS, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()