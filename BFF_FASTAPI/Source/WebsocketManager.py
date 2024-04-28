"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [25.04.24]
Purpose: [System for working with websocket protocol.]
"""

import logging

from fastapi import WebSocket
from fastapi.websockets import WebSocketState, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        """Initializes ConnectionManager with an empty set of connections."""
        self.connections = set()

    async def connect(self, websocket: WebSocket):
        """
        Accepts a WebSocket connection and adds it to the set of connections.
        :param websocket: The WebSocket connection object.
        """

        await websocket.accept()
        self.connections.add(websocket)
        logging.info('WebSocket connected')

    @staticmethod
    async def disconnect(websocket: WebSocket):
        """
        Closes a WebSocket connection if it's not already disconnected.
        :param websocket: The WebSocket connection object.
        """
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
            logging.info('WebSocket disconnected')
        else:
            logging.info('WebSocket is already disconnected')

    async def send_message(self, message: str, websocket: WebSocket):
        """
        Sends a message over the WebSocket connection.
        :exception: If connection is disconnected.
        :param message: The message to be sent.
        :param websocket: The WebSocket connection object.
        """
        try:
            await websocket.send_text(message)
            logging.info(f'WebSocket sent message "{message}"')
        except WebSocketDisconnect:
            self.connections.remove(websocket)
            await websocket.close()
            logging.exception('Client disconnected. Cleaned up')

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all connected WebSocket clients.
        :param message: The message to be broadcast.
        """
        for connection in self.connections:
            await self.send_message(message, connection)
            logging.info(f'WebSocket broadcast sent a message "{message}"')
