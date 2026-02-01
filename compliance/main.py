import pika
import json
import time
import random
from Constants import Queues, Statuses, RabbitConfig
from zeep import Client

rabbit_config = RabbitConfig()

WSDL_URL = "http://compliance-soap:8001/?wsdl"
SERVICE_METHOD = "CheckWasteLegality"     

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

def call_soap_service(waste_type: str) -> bool:
    client = Client(WSDL_URL)
    response = getattr(client.service, SERVICE_METHOD)(wasteType=waste_type)
    return bool(response)

def callback(ch, method, properties, body):
    data = json.loads(body)
    req_id = data['id']
    waste_type = data['waste_type']
    
    print(f" [Compliance] Weryfikacja prawna dla: {waste_type} (ID: {req_id})")
    
    try:
        is_legal = call_soap_service(waste_type)
    except Exception as e:
        print(f" [Compliance] Błąd podczas wywoływania usługi SOAP: {e}")
        is_legal = False 
    
    if is_legal:
        status = Statuses.APPROVED
        print(" [Compliance] Decyzja: ZATWIERDZONO (KPO wygenerowane)")
    else:
        status = Statuses.REJECTED
        print(" [Compliance] Decyzja: ODRZUCONO (Nielegalny odpad)")

    time.sleep(10)

    print(" [Compliance] Koniec weryfikacji prawnej.")

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