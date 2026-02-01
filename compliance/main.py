import pika
import json
import time
import random
from Constants import Queues, Statuses, RabbitConfig

rabbit_config = RabbitConfig()

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
    waste_type = data['waste_type']
    
    print(f" [Compliance] Weryfikacja prawna dla: {waste_type} (ID: {req_id})")
    
    # --- TODO: SOAP Client ---
    
    time.sleep(10) # udajemy, że system rządowy mieli dane
    
    # Prosta logika: "radioactive" jest nielegalne, reszta ok
    if "radio" in waste_type.lower():
        status = Statuses.REJECTED
        print(" [Compliance] Decyzja: ODRZUCONO (Nielegalny odpad)")
    else:
        status = Statuses.APPROVED
        print(" [Compliance] Decyzja: ZATWIERDZONO (KPO wygenerowane)")
    # -----------------------------------------

    # Tutaj kończymy Sagę i wysyłamy wynik do kolejki wyników
    result_message = {
        "id": req_id,
        "status": status
    }

    ch.queue_declare(queue=Queues.RESULTS)
    ch.basic_publish(exchange='', routing_key=Queues.RESULTS, body=json.dumps(result_message))
    print(f" [Compliance] Wynik wysłany do results_queue: {result_message}")

def main():
    channel = get_channel()
    channel.queue_declare(queue=Queues.COMPLIANCE)

    print(' [Compliance] Czekam na wnioski do weryfikacji...')
    channel.basic_consume(queue=Queues.COMPLIANCE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    main()