from __future__ import annotations

from typing import AsyncGenerator

import asyncpg
from sonyflake import SonyFlake
from utils.requests import RouteRequest

_id_generator = SonyFlake()


def generate_id() -> int:
    if not _id_generator:
        raise RuntimeError("_id_generator is None")

    return _id_generator.next_id()


async def use(request: RouteRequest) -> AsyncGenerator[asyncpg.Pool, None]:
    yield request.app.pool
