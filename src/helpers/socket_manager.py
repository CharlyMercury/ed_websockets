"""
    Socket Manager
    User this module to generate an manage a connection between server-client
"""

from typing import List
from fastapi import WebSocket
import json

class SocketManager:
    """ Class to create a server socket manager """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ids = []
    
    async def connect(self, websocket: WebSocket):
        """ Connection server-client function """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """ Send message to the corresponded connected client sockets"""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """ Send message to all clients """
        for connection in self.active_connections:
            await connection.send_text(message)