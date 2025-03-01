from core import Server
from fastapi import Request


class RouteRequest(Request):
    app: Server
