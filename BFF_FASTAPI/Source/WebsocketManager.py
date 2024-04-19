import logging

from fastapi import WebSocket
from fastapi.websockets import WebSocketState, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        logging.info('WebSocket connected')

    @staticmethod
    async def disconnect(websocket: WebSocket):
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
            logging.info('WebSocket disconnected')
        else:
            logging.info('WebSocket is already disconnected')

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            logging.info(f'WebSocket sent message "{message}"')
        except WebSocketDisconnect:
            self.connections.remove(websocket)
            await websocket.close()
            logging.exception('Client disconnected. Cleaned up')

    async def broadcast(self, message: str):
        for connection in self.connections:
            await self.send_message(message, connection)
            logging.info(f'WebSocket broadcast sent a message "{message}"')
