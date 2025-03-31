import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from auth import hash_password
from models import Session, User


async def create_administrator(session: AsyncSession, name: str, password: str):
    user = User(name=name, password=hash_password(password), role="admin")
    session.add(user)
    await session.commit()


async def main():
    async with Session() as session:
        await create_administrator(session, name='name', password='password')


if __name__ == "__main__":
    asyncio.run(main())