from typing import Annotated, Optional

import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from utils import db
from utils.exceptions import ConflictException, NotFoundException, UnauthorizedException
from utils.requests import RouteRequest
from utils.responses import ConflictMessage, NotFoundMessage, UnauthorizedMessage
from utils.sessions import (
    Session,
    authorize,
    hash_password,
    new_session,
    verify_password,
)

router = APIRouter(tags=["Me"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post(
    "/login", responses={200: {"model": Session}, 401: {"model": UnauthorizedMessage}}
)
async def login(request: RouteRequest, req: LoginRequest) -> Session:
    """Logs in a member and returns a session token"""
    query = """
    SELECT member.id, member_passwords.passhash
    FROM member
    INNER JOIN member_passwords ON member.id = member_passwords.id
    WHERE email = $1;
    """

    async with request.app.pool.acquire() as connection:
        member = await request.app.pool.fetchrow(query, req.email)

        if not member:
            raise UnauthorizedException()

        if not verify_password(req.password, ""):
            raise UnauthorizedException()

        return await new_session(member.id, connection=connection)


class RegisterRequest(BaseModel):
    """
    This class is used to register a new user.
    """

    bio: str
    email: str
    password: str


@router.post(
    "/register", responses={200: {"model": Session}, 409: {"model": ConflictMessage}}
)
async def register(request: RouteRequest, req: RegisterRequest) -> Session:
    """Registers a new member, and returns a session token"""

    query = """
    WITH insert_member AS (
        INSERT INTO members (id, name, email, bio)
        VALUES ($1, $2, $3, $4)
        RETURNING id;
    )
    INSERT INTO member_passwords (id, passhash)
    VALUES ((SELECT id FROM insert_member), $5);
    """

    async with request.app.pool.acquire() as connection:
        tr = connection.transaction()
        await tr.start()

        new_member_id = db.generate_id()

        try:
            await connection.execute(
                query,
                new_member_id,
                *req.model_dump().values(),
                hash_password(req.password),
            )
        except asyncpg.UniqueViolationError:
            await tr.rollback()
            raise ConflictException()
        else:
            await tr.commit()

        return await new_session(new_member_id, connection=connection)


class MeResponse(BaseModel, frozen=True):
    id: int
    name: str
    email: str
    bio: str


@router.get(
    "/users/me", responses={200: {"model": MeResponse}, 404: {"model": NotFoundMessage}}
)
async def get_self(
    request: RouteRequest,
    me_id: Annotated[int, Depends(authorize)],
) -> MeResponse:
    """Obtains currently authenticated member's information"""
    query = """
    SELECT id, name, email, bio
    FROM member
    WHERE id = $1;
    """
    member = await request.app.pool.fetchrow(query, me_id)

    if not member:
        raise NotFoundException()

    return MeResponse(**dict(member))


class UpdateMemberRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = None


class Member(BaseModel):
    id: int
    name: str
    email: str
    bio: str


class MemberWithPasshash(Member):
    passhash: str


@router.patch("/users/me", responses={200: {"model": Member}})
async def update_member(
    request: RouteRequest,
    req: UpdateMemberRequest,
    me_id: Annotated[int, Depends(authorize)],
) -> Member:
    """Updates the specified authenticated user"""

    member_query = """
    SELECT member.id, member.name, member.bio, member.email, member_passwords.passhash
    FROM member
    INNER JOIN member_passwords ON member.id = member_passwords.id
    WHERE id = $1;
    """

    update_query = """
    WITH update_member AS (
        UPDATE member
            SET name = $2,
            SET bio = $3,
            SET email = $4
        WHERE id = $1
        RETURNING id;
    )
    UPDATE member_passwords
    SET passhash = $5
    WHERE id = (SELECT id FROM update_member)
    RETURNING id, name, bio, email;
    """

    async with request.app.pool.acquire() as connection:
        rows = await connection.fetchrow(member_query, me_id)
        copied_rows = MemberWithPasshash(**dict(rows))
        for key, value in req.model_dump().items():
            match key:
                case "password":
                    copied_rows.passhash = hash_password(value)
                case _:
                    setattr(copied_rows, key, value)

        updated_member = await connection.fetchrow(
            update_query, me_id, *copied_rows.model_dump().values()
        )

        return Member(**dict(updated_member))
