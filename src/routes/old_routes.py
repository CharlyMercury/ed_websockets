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

received_count = 0
received_all_event = threading.Event()

app_routes = APIRouter()
manager = SocketManager()


database_schools = [
    [
        {"plantel": " Prepa 1"},
        {
            "pcb_parameters": {
                "turn_on_time": [6, 0, 0],
                "turn_off_time": [20, 0, 0],
                "days_turned_on": ["mon", "tue", "wed", "thu", "fri"],
                "timezone_offset": -6,
                "wifi_parameters": {
                    "ssid": "IZZI-6D04",
                    "password": "F0AF85386D04",
                },
                "pcb_id": 1,
                "pcb_details":
                    ["Pcb instalado en la Prepa 1. ", "Módulo instalado en la entrada principal del edificio. "],
                "pcb_version": 1.1,
                "color_leds": {
                    "stand_by_color_led": "blue",
                    "ok_student_color_led": "green",
                    "error_student_color_led": "red",
                }
            },
            "actions": {
                "import_students": False,
                "sync_data": False,
                "schema_creation": False
            },
            "environment_variables": {
                "app_server_url": "https://www.edumediamanager.com",
                "tipo_modulo": "check_in_out_edumedia",
                "timezone": "America/Mexico_City",
                "plantel_identificador": "nnccopos82",
                "plantel_nombre": "PREPA*1",
                "individuo_identificador": "RFID",
            },
            "status": {
                "raspberry": False,
                "esp32": False
            }
        }
    ]
]

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


@app_routes.get(path='/', response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("access_control_module_status.html", {"request": request, "variable": database_schools})


@app_routes.get(path='/prepa1')
async def get(request: Request):

    return {"prepa1": "Successfully"}


@app_routes.post(path='/prepa1')
async def send_request_aws(request: Request):

    return {"prepa1": "Successfully"}


@app_routes.get(path='/iot/disconnect')
async def get(request: Request):
    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_client.mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
    return {"status": "Disconencted Successfully"}

@app_routes.post(path="/response")
async def destination_endpoint(request: Request):
    global last_response
    data = await request.json()
    last_response = data
    return JSONResponse(content=last_response)

@app_routes.post(path="/updatejson")
async def destination_endpoint(request: Request):
    data = await request.json()
    update_json(data)
    return JSONResponse(content=last_response)

@app_routes.get(path='/response', response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("response_module.html", {"request": request, "variable": last_response})

@app_routes.websocket(path="/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            data_json.update({"id_response":client_id})
            data = json.dumps(data_json)
            print(data_json)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")


def update_json(data):
    raspberry_response = data["raspberry_response"]["pcb_parameters"]
    json_sended = data["json_sended"]
    
    for key, values in raspberry_response.items():
        if "Actualizado" in values:
            database_schools[0][1]["pcb_parameters"][key] = json_sended["pcb_parameters"][key]
