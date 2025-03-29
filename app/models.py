from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import Integer, String, func, Float, UUID, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import config
import uuid
from custom_types import Role

engine = create_async_engine(config.PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {
            "id": self.id
        }

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    tokens: Mapped[list["Token"]] = relationship("Token", lazy="joined", back_populates="user")
    advertisement: Mapped[list["Advertisement"]] = relationship("Advertisement", back_populates="owner", lazy="joined")
    role: Mapped[Role] = mapped_column(String, default='user')

    @property
    def dict(self):
        return {'id': self.id, 'name': self.name}

class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, server_default=func.gen_random_uuid())
    creation_time: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(User, lazy="joined", back_populates="tokens")

    @property
    def dict(self):
        return {'token': self.token}

class Advertisement(Base):
    __tablename__ = "advertisements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date_created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="advertisement", lazy="joined")

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "date_created": int(self.date_created.timestamp()),
            'owner_id': self.owner_id
        }

ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]

async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_orm():
    await engine.dispose()