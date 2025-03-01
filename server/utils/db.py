from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

import asyncpg
from fastapi import HTTPException
from utils.requests import RouteRequest

async def use(request: RouteRequest) -> AsyncGenerator[asyncpg.Pool, None]:
    """
    This function is a context manager that yields a database session.
    Use this in FastAPI route functions to access the database.
    """
    yield request.app.pool
