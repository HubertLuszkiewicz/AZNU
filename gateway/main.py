import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pika
import uuid
import json
import redis
from Constants import Queues, Statuses, RabbitConfig

rabbit_config = RabbitConfig()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis") 
r = redis.Redis(host=REDIS_HOST, port=6379)

class DisposalRequest(BaseModel):
    waste_type: str
    weight: float

def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_config.HOST, rabbit_config.PORT))
    return connection.channel()

@app.post("/request")
def create_request(item: DisposalRequest):
    request_id = str(uuid.uuid4())
    
    r.set(request_id, Statuses.STARTED)

    message = {
        "id": request_id,
        "waste_type": item.waste_type,
        "weight": item.weight
    }
    
    channel = get_channel()
    channel.queue_declare(queue=Queues.LOGISTICS)
    channel.basic_publish(exchange='', routing_key=Queues.LOGISTICS, body=json.dumps(message))
    print(f" [Gateway] Wysłano zlecenie do Logistics: {message}")

    return {"id": request_id, "status": Statuses.STARTED}

@app.get("/request/{request_id}")
def get_status(request_id: str):
    status = r.get(request_id)
    
    if status is None:
        return {"error": "Nie znaleziono zlecenia"}
    
    print(f" [Gateway] Pobieranie statusu dla {request_id}: {status.decode('utf-8')}")

    return {"id": request_id, "status": status.decode('utf-8')}