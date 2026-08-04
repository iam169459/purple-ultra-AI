"""WebSocket server for remote control and real-time streaming."""

from __future__ import annotations

import asyncio
import json
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class WSMessage:
    type: str
    data: Any = None
    id: str = ""
    timestamp: float = field(default_factory=time.time)


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}
        self._history: list[WSMessage] = []
        self._max_history = 100

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        if event_type in self._subscribers:
            self._subscribers[event_type] = [cb for cb in self._subscribers[event_type] if cb != callback]

    def publish(self, event_type: str, data: Any = None):
        msg = WSMessage(type=event_type, data=data)
        self._history.append(msg)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(msg)
            except Exception:
                pass
        for callback in self._subscribers.get("*", []):
            try:
                callback(msg)
            except Exception:
                pass

    def get_history(self, event_type: str = None, count: int = 20) -> list[dict]:
        msgs = self._history
        if event_type:
            msgs = [m for m in msgs if m.type == event_type]
        return [{"type": m.type, "data": m.data, "timestamp": m.timestamp} for m in msgs[-count:]]


class MessageQueue:
    def __init__(self, max_size: int = 1000):
        self._queue: list[WSMessage] = []
        self._max_size = max_size
        self._consumers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()

    def enqueue(self, msg_type: str, data: Any = None, priority: int = 5):
        msg = WSMessage(type=msg_type, data=data)
        with self._lock:
            if len(self._queue) >= self._max_size:
                self._queue.pop(0)
            self._queue.append(msg)
        for consumer in self._consumers.get(msg_type, []):
            try:
                consumer(msg)
            except Exception:
                pass

    def dequeue(self) -> WSMessage | None:
        with self._lock:
            if self._queue:
                return self._queue.pop(0)
        return None

    def register_consumer(self, msg_type: str, callback: Callable):
        if msg_type not in self._consumers:
            self._consumers[msg_type] = []
        self._consumers[msg_type].append(callback)

    def size(self) -> int:
        return len(self._queue)

    def clear(self):
        with self._lock:
            self._queue.clear()


class WebSocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.event_bus = EventBus()
        self.message_queue = MessageQueue()
        self._clients: dict[str, Any] = {}
        self._running = False
        self._handlers: dict[str, Callable] = {}

    def register_handler(self, msg_type: str, handler: Callable):
        self._handlers[msg_type] = handler

    async def _handle_client(self, websocket, path=None):
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self._clients[client_id] = websocket
        self.event_bus.publish("client_connected", {"client_id": client_id})
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "unknown")
                    handler = self._handlers.get(msg_type)
                    if handler:
                        result = handler(data)
                        if asyncio.iscoroutine(result):
                            result = await result
                        await websocket.send(json.dumps({
                            "type": "response",
                            "request_type": msg_type,
                            "data": result,
                            "timestamp": time.time(),
                        }))
                    else:
                        self.event_bus.publish(msg_type, data)
                        self.message_queue.enqueue(msg_type, data)
                        await websocket.send(json.dumps({
                            "type": "ack",
                            "request_type": msg_type,
                            "timestamp": time.time(),
                        }))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
        except Exception:
            pass
        finally:
            del self._clients[client_id]
            self.event_bus.publish("client_disconnected", {"client_id": client_id})

    async def _broadcast(self, message: dict):
        text = json.dumps(message)
        for client_id, ws in list(self._clients.items()):
            try:
                await ws.send(text)
            except Exception:
                del self._clients[client_id]

    def broadcast(self, message: dict):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self._broadcast(message))
        finally:
            loop.close()

    def start(self):
        try:
            import websockets
            self._running = True
            async def run():
                async with websockets.serve(self._handle_client, self.host, self.port):
                    await asyncio.Future()
            asyncio.run(run())
        except ImportError:
            self._fallback_start()

    def _fallback_start(self):
        import socket
        import json as _json
        self._running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        server.settimeout(1.0)
        print(f"WebSocket server (fallback) listening on {self.host}:{self.port}")
        while self._running:
            try:
                client, addr = server.accept()
                threading.Thread(target=self._handle_tcp_client, args=(client, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                break
        server.close()

    def _handle_tcp_client(self, client, addr):
        try:
            data = client.recv(65536).decode()
            msg = json.loads(data)
            msg_type = msg.get("type", "unknown")
            handler = self._handlers.get(msg_type)
            if handler:
                result = handler(msg)
                client.send(json.dumps({"type": "response", "data": result}).encode())
            else:
                self.event_bus.publish(msg_type, msg)
                client.send(json.dumps({"type": "ack"}).encode())
        except Exception:
            pass
        finally:
            client.close()

    def stop(self):
        self._running = False

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "clients": len(self._clients),
            "host": self.host,
            "port": self.port,
            "queue_size": self.message_queue.size(),
        }
