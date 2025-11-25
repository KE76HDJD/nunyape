import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from .models import PresentationResponse

logger = logging.getLogger('presentation-streaming')

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.presentation_sessions: Dict[str, set] = {}
    
    async def connect(self, websocket: WebSocket, presentation_id: str, user_id: str):
        await websocket.accept()
        connection_id = f"{presentation_id}_{user_id}"
        self.active_connections[connection_id] = websocket
        
        if presentation_id not in self.presentation_sessions:
            self.presentation_sessions[presentation_id] = set()
        self.presentation_sessions[presentation_id].add(connection_id)
        
        logger.info(f"User {user_id} connected to presentation {presentation_id}")
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from presentation sessions
        for presentation_id, connections in self.presentation_sessions.items():
            if connection_id in connections:
                connections.remove(connection_id)
                if not connections:
                    del self.presentation_sessions[presentation_id]
                break
    
    async def send_personal_message(self, message: str, connection_id: str):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_text(message)
    
    async def broadcast_to_presentation(self, message: str, presentation_id: str):
        if presentation_id in self.presentation_sessions:
            disconnected = []
            for connection_id in self.presentation_sessions[presentation_id]:
                try:
                    await self.active_connections[connection_id].send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send to {connection_id}: {e}")
                    disconnected.append(connection_id)
            
            # Clean up disconnected clients
            for connection_id in disconnected:
                self.disconnect(connection_id)

class PresentationStreamer:
    def __init__(self):
        self.manager = ConnectionManager()
        self.slide_events = asyncio.Queue()
    
    async def handle_slide_change(self, presentation_id: str, slide_number: int):
        """Handle slide change events"""
        event_data = {
            "type": "slide_change",
            "presentation_id": presentation_id,
            "slide_number": slide_number,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_presentation(
            json.dumps(event_data), presentation_id
        )
    
    async def handle_annotation(self, presentation_id: str, annotation_data: Dict[str, Any]):
        """Handle annotation events"""
        event_data = {
            "type": "annotation",
            "presentation_id": presentation_id,
            "data": annotation_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_presentation(
            json.dumps(event_data), presentation_id
        )
    
    async def handle_poll(self, presentation_id: str, poll_data: Dict[str, Any]):
        """Handle poll events"""
        event_data = {
            "type": "poll",
            "presentation_id": presentation_id,
            "data": poll_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_presentation(
            json.dumps(event_data), presentation_id
        )
    
    async def stream_presentation_updates(self, websocket: WebSocket, presentation_id: str, user_id: str):
        """Handle WebSocket connection for presentation streaming"""
        await self.manager.connect(websocket, presentation_id, user_id)
        connection_id = f"{presentation_id}_{user_id}"
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message["type"] == "slide_change":
                    await self.handle_slide_change(presentation_id, message["slide_number"])
                elif message["type"] == "annotation":
                    await self.handle_annotation(presentation_id, message["data"])
                elif message["type"] == "poll":
                    await self.handle_poll(presentation_id, message["data"])
                elif message["type"] == "chat_message":
                    await self.broadcast_chat_message(presentation_id, user_id, message["message"])
                    
        except WebSocketDisconnect:
            self.manager.disconnect(connection_id)
            logger.info(f"User {user_id} disconnected from presentation {presentation_id}")
    
    async def broadcast_chat_message(self, presentation_id: str, user_id: str, message: str):
        """Broadcast chat messages to all connected clients"""
        chat_data = {
            "type": "chat_message",
            "presentation_id": presentation_id,
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_presentation(
            json.dumps(chat_data), presentation_id
        )

class RealTimeCollaboration:
    def __init__(self):
        self.cursors = {}  # Store cursor positions
        self.annotations = {}  # Store annotations per presentation
    
    async def update_cursor_position(self, presentation_id: str, user_id: str, position: Dict[str, float]):
        """Update cursor position for a user"""
        if presentation_id not in self.cursors:
            self.cursors[presentation_id] = {}
        
        self.cursors[presentation_id][user_id] = {
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast cursor update to other users
        event_data = {
            "type": "cursor_update",
            "presentation_id": presentation_id,
            "user_id": user_id,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        streamer = PresentationStreamer()
        await streamer.manager.broadcast_to_presentation(
            json.dumps(event_data), presentation_id
        )