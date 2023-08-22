import json
from typing import Annotated
from fastapi import APIRouter, Request, Form
from fastapi import Body
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from starlette.responses import FileResponse 
from fastapi.templating import Jinja2Templates

# From helpers server folder
from src.helpers.socket_manager import SocketManager

app_routes = APIRouter()
manager = SocketManager()


# Initialize Jinja2 templates
templates = Jinja2Templates(directory="src/views/")


@app_routes.get(path='/', response_class=HTMLResponse)
async def get(request: Request):
    device_params = {
        "plantel": " Prepa 1"
        
        }
    return templates.TemplateResponse("access_control_module_status.html", {"request": request, "variable": device_params})
    # return FileResponse('src/views/access_control_module_status.html')


@app_routes.websocket(path="/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client #{client_id} says: {data}")
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

