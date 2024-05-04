import json
from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi import Body
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from starlette.responses import FileResponse 
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from src.aws_client import AwsMqttClient
import threading
import os

# From helpers server folder
from src.helpers.socket_manager import SocketManager


app_routes = APIRouter()
manager = SocketManager()

# Get the current working directory
current_path = os.getcwd()
file_path_src = os.path.join(current_path, 'src')
file_path_certificates = os.path.join(file_path_src, 'certificates')

with open(file=file_path_src + r'\parameters_configuration.json', mode='r', encoding='utf-8') as file:
    parameters = json.load(file)
endpoint = "a1svajesngnqg2-ats.iot.us-east-1.amazonaws.com"
port = 443
cert = file_path_certificates + r"\routiva_laser_machine_1_8080.cert.pem"
key = file_path_certificates + r"\routiva_laser_machine_1_8080.private.key"
ca = file_path_certificates + r"\root-CA.crt"
client_id = "technical_support"
topics_subs = [
    f'update/esp32/response',
    f'update/db/response',
    f'status/response']

mqtt_client = AwsMqttClient(endpoint, port, cert, key, ca, client_id, topics_subs, parameters)
mqtt_client.subscribe_to_topics()

last_response = {}

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/views/")


@app_routes.get(path='/')
async def get(request: Request):
    return {"home": "home"}


@app_routes.get(path='/status')
async def get_status(plantel: str, modulo: int):
    message_status = {
        "plantel": plantel,
        "modulo": f"modulo{modulo}",
    }
    mqtt_client.publish_to_topics(topic_pub_="status/", input_message=message_status)
    return {"prepa1": "Successfully"}


@app_routes.get(path='/update/db')
async def get_update_db(plantel: str, modulo: int):
    message_status = {
        "plantel": plantel,
        "modulo": f"modulo{modulo}",
    }
    mqtt_client.publish_to_topics(topic_pub_="update/db/cbtis0/modulo1", input_message=message_status)
    return {"prepa1": "Successfully"}


@app_routes.get(path='/update/esp32')
async def get_update_esp32(plantel: str, modulo: int):
    message_status = {
        "plantel": plantel,
        "modulo": f"modulo{modulo}",
    }
    mqtt_client.publish_to_topics(topic_pub_="update/esp32/cbtis0/modulo1", input_message=message_status)
    return {"prepa1": "Successfully"}


@app_routes.get(path='/iot/disconnect')
async def get(request: Request):
    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_client.mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
    return {"status": "Disconencted Successfully"}
