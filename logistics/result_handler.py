import os
import time
import pika
import json
import redis
from Constants import Queues, RabbitConfig

rabbit_config = RabbitConfig()
REDIS_HOST = os.getenv("REDIS_HOST", "redis") 
r = redis.Redis(host=REDIS_HOST, port=6379)

def get_channel():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    rabbit_config.HOST, 
                    rabbit_config.PORT
                )
            )
            return connection.channel()
        
        except pika.exceptions.AMQPConnectionError:
            print(" [Compliance] Nie można połączyć się z RabbitMQ, ponawianie próby za 5 sekund...")
            time.sleep(5)


def callback(ch, method, properties, body):
    data = json.loads(body)
    req_id = data['id']
    status = data['status']

    print(f" [Logistics Results] Odebrano wynik dla {req_id}: {status}")

    r.set(req_id, status)
    print(" [Logistics Results] Zaktualizowano status w Redis.")


def main():
    channel = get_channel()
    channel.queue_declare(queue=Queues.RESULTS)

    print(' [Logistics Results] Czekam na wyniki z Compliance...')
    channel.basic_consume(queue=Queues.RESULTS, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()