"""REST API server for external integrations."""

from __future__ import annotations

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Any, Callable


class APIRouter:
    def __init__(self):
        self._routes: dict[str, dict[str, Callable]] = {}
        self._middleware: list[Callable] = []

    def add_route(self, method: str, path: str, handler: Callable):
        if path not in self._routes:
            self._routes[path] = {}
        self._routes[path][method.upper()] = handler

    def get(self, path: str, handler: Callable):
        self.add_route("GET", path, handler)

    def post(self, path: str, handler: Callable):
        self.add_route("POST", path, handler)

    def put(self, path: str, handler: Callable):
        self.add_route("PUT", path, handler)

    def delete(self, path: str, handler: Callable):
        self.add_route("DELETE", path, handler)

    def add_middleware(self, middleware: Callable):
        self._middleware.append(middleware)

    def match(self, method: str, path: str) -> tuple[Callable | None, dict]:
        if path in self._routes:
            handler = self._routes[path].get(method.upper())
            if handler:
                return handler, {}
        for route_path, methods in self._routes.items():
            if method.upper() in methods:
                params = self._extract_params(route_path, path)
                if params is not None:
                    return methods[method.upper()], params
        return None, {}

    def _extract_params(self, route_path: str, actual_path: str) -> dict | None:
        route_parts = route_path.strip("/").split("/")
        actual_parts = actual_path.strip("/").split("/")
        if len(route_parts) != len(actual_parts):
            return None
        params = {}
        for rp, ap in zip(route_parts, actual_parts):
            if rp.startswith("{") and rp.endswith("}"):
                params[rp[1:-1]] = ap
            elif rp != ap:
                return None
        return params


class Request:
    def __init__(self, method: str, path: str, headers: dict, body: str, query: dict):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query = query
        self.params: dict = {}

    def json(self) -> dict:
        try:
            return json.loads(self.body) if self.body else {}
        except json.JSONDecodeError:
            return {}

    def param(self, name: str) -> str:
        return self.params.get(name, "")

    def query_param(self, name: str) -> str:
        return self.query.get(name, [""])[0]


class Response:
    def __init__(self):
        self.status = 200
        self.headers = {"Content-Type": "application/json"}
        self.body = ""

    def set_status(self, code: int):
        self.status = code
        return self

    def set_header(self, key: str, value: str):
        self.headers[key] = value
        return self

    def json(self, data: Any):
        self.body = json.dumps(data, default=str)
        self.headers["Content-Type"] = "application/json"
        return self

    def text(self, data: str):
        self.body = data
        self.headers["Content-Type"] = "text/plain"
        return self

    def html(self, data: str):
        self.body = data
        self.headers["Content-Type"] = "text/html"
        return self


class APIHandler(BaseHTTPRequestHandler):
    router: APIRouter = None
    api_key: str = ""

    def log_message(self, format, *args):
        pass

    def _send_response(self, resp: Response):
        self.send_response(resp.status)
        for key, value in resp.headers.items():
            self.send_header(key, value)
        self.end_headers()
        if isinstance(resp.body, str):
            self.wfile.write(resp.body.encode())
        else:
            self.wfile.write(resp.body)

    def _handle(self):
        if self.api_key:
            auth = self.headers.get("Authorization", "")
            if not auth.endswith(self.api_key) and self.path != "/api/health":
                resp = Response().set_status(401).json({"error": "Unauthorized"})
                self._send_response(resp)
                return

        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else ""

        req = Request(self.command, parsed.path, dict(self.headers), body, query)
        resp = Response()

        handler, params = self.router.match(self.command, parsed.path)
        if handler:
            req.params = params
            for mw in self.router._middleware:
                try:
                    result = mw(req, resp)
                    if result is False:
                        self._send_response(resp)
                        return
                except Exception:
                    pass
            try:
                result = handler(req, resp)
                if isinstance(result, Response):
                    self._send_response(result)
                else:
                    self._send_response(resp.json(result) if result is not None else resp)
            except Exception as e:
                self._send_response(Response().set_status(500).json({"error": str(e)}))
        else:
            self._send_response(Response().set_status(404).json({"error": "Not found"}))

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_PUT(self):
        self._handle()

    def do_DELETE(self):
        self._handle()

    def do_OPTIONS(self):
        resp = Response()
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        resp.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self._send_response(resp)


class RESTServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, api_key: str = ""):
        self.host = host
        self.port = port
        self.router = APIRouter()
        self.api_key = api_key
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self, background: bool = True):
        APIHandler.router = self.router
        APIHandler.api_key = self.api_key
        self._server = HTTPServer((self.host, self.port), APIHandler)
        if background:
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
        else:
            self._server.serve_forever()

    def stop(self):
        if self._server:
            self._server.shutdown()

    def get_status(self) -> dict:
        return {
            "running": self._server is not None,
            "host": self.host,
            "port": self.port,
            "routes": len(self.router._routes),
        }
