from config import TOKEN_TTL_SEC
from fastapi.params import Depends
from fastapi import Header, HTTPException
import uuid
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Session, Token
from typing import Annotated

async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]

async def get_token(
        x_token: Annotated[uuid.UUID, Header()], session:SessionDependency
) -> Token:
    query = select(Token).where(
        Token.token == x_token,
        Token.creation_time >= (datetime.datetime.now() - datetime.timedelta(seconds=TOKEN_TTL_SEC))
    )
    token = await session.scalars(query)
    if token is None:
        raise HTTPException(401, 'Token not found')
    return token

TokenDependency = Annotated[Token, Depends(get_token)]