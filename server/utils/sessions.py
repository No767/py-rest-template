import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator, Optional, Union

import asyncpg
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from utils import db

SESSION_EXPIRY = timedelta(days=7)
SESSION_RENEW_AFTER = timedelta(days=1)


class Session(BaseModel, frozen=True):
    token: str
    user_id: Optional[int]
    expires_at: datetime


async def authorize(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    db: Annotated[asyncpg.Pool, Depends(db.use)],
) -> AsyncGenerator[int, None]:
    """
    This function asserts the authorization header and returns the user ID if
    the token is valid.
    """
    async with db.acquire() as connection:
        authorization = creds.credentials
        now = datetime.now()

        session_query = """
        SELECT user_id
        FROM user_sessions
        WHERE token = $1 AND expires_at > $2;
        """
        session = await connection.fetchrow(session_query, authorization, now)

        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # If the session is after the renew threshold, renew the session.
        # Don't always renew the session, as that would force a database write on
        # every request.
        if (session.expires_at - SESSION_EXPIRY) + SESSION_RENEW_AFTER < now:
            query = """
            UPDATE user_session
            SET expires_at = $2
            WHERE token = $1;
            """
            new_expires_at = datetime.now() + SESSION_EXPIRY

            tr = connection.transaction()
            await tr.start()
            try:
                await connection.execute(query, authorization, new_expires_at)
            except Exception as e:
                await tr.rollback()
                raise HTTPException(status_code=500, detail=f"Fatal error: {e}")
            else:
                await tr.commit()

        yield session["user_id"]


async def new_session(
    user_id: int, *, connection: Union[asyncpg.Connection, asyncpg.Pool]
) -> Session:
    """
    This function creates a new session for a user and adds it to the database.
    The session is returned.
    """
    query = """
    INSERT INTO user_session (token, user_id, expires_at)
    VALUES ($1, $2, $3);
    """
    session = Session(
        token=generate_token(),
        user_id=user_id,
        expires_at=datetime.now() + SESSION_EXPIRY,
    )
    await connection.execute(query, *session.model_dump().values())
    return session


def generate_token() -> str:
    """
    This function generates a random token.
    """
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """
    This function hashes a password.
    """
    salt = secrets.token_bytes(16)
    hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return f"{salt.hex()}${hash.hex()}"


def verify_password(password: str, shash: str) -> bool:
    """
    This function verifies a password.
    """
    ssalt, shash = shash.split("$")
    osalt = bytes.fromhex(ssalt)
    ohash = bytes.fromhex(shash)
    return hmac.compare_digest(
        ohash,
        hashlib.pbkdf2_hmac("sha256", password.encode(), osalt, 100000),
    )
