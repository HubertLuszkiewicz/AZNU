import pika
import json
import redis
from Constants import Queues, RabbitConfig

rabbit_config = RabbitConfig()
r = redis.Redis(host='localhost', port=6379, db=0)

def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_config.HOST, rabbit_config.PORT))
    return connection.channel()
    return connection.channel()


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