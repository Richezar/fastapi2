from fastapi import FastAPI, HTTPException, Query
from schema import (CreateAdvertisementRequest,
                    UpdateAdvertisementRequest,
                    CreateAdvertisementResponse,
                    DeleteAdvertisementResponse,
                    GetAdvertisementResponse,
                    LoginRequest,
                    LoginResponse,
                    CreateUserRequest,
                    CreateUserResponse,
                    GetUserResponse,
                    UpdateUserRequest,
                    DeleteUserResponse
                    )
from lifespan import lifespan
from dependancy import SessionDependency, TokenDependency
import crud
import models
import auth
from sqlalchemy.future import select

app = FastAPI(
    title='Advertisement',
    lifespan=lifespan
)


@app.post("/advertisement", tags=['Advertisement'], response_model=CreateAdvertisementResponse)
async def create_advertisement(ad: CreateAdvertisementRequest, session: SessionDependency, token: TokenDependency):
    ad_orm_obj = models.Advertisement(title=ad.title,
                                      description=ad.description,
                                      price=ad.price,
                                      owner_id=token.user_id)
    await crud.add_item(session, ad_orm_obj)
    return ad_orm_obj.id_dict


@app.patch("/advertisement/{ad_id}", tags=['Advertisement'])
async def update_advertisement(ad_id: int, ad_data: UpdateAdvertisementRequest, session: SessionDependency, token: TokenDependency):
    ad = await session.get(models.Advertisement, ad_id)
    if ad.owner_id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    for field, value in ad_data.dict(exclude_unset=True).items():
        setattr(ad, field, value)
    session.add(ad)
    await session.commit()
    return {"status": "success", "advertisement": ad.dict}

@app.patch("/user/{us_id}", tags=['User'])
async def update_user(us_id: int, us_data: UpdateUserRequest, session: SessionDependency, token: TokenDependency):
    us = await session.get(models.User, us_id)
    if not us:
        raise HTTPException(status_code=404, detail="User not found")
    if token.user.role != "admin" and token.user_id != us.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if us_data.password:
        us_data.password = auth.hash_password(us_data.password)
    for field, value in us_data.dict(exclude_unset=True).items():
        setattr(us, field, value)
    session.add(us)
    await session.commit()
    return {"status": "success", "user": us.dict}

@app.get("/advertisement/{ad_id}", tags=['Advertisement'], response_model=GetAdvertisementResponse)
async def get_advertisement(ad_id: int, session: SessionDependency):
    ad_orm_obj = await crud.get_item_by_id(session, models.Advertisement, ad_id)
    return ad_orm_obj.dict

@app.get("/user/{us_id}", tags=['User'], response_model=GetUserResponse)
async def get_user(us_id: int, session: SessionDependency):
    us_orm_obj = await crud.get_item_by_id(session, models.User, us_id)
    return us_orm_obj.dict

@app.get("/advertisement", tags=['Advertisement'], response_model=list[GetAdvertisementResponse])
async def get_query_sting_advertisement(session: SessionDependency,
                                        title: str = Query(None),
                                        description: str = Query(None),
                                        price: float = Query(None),
                                        owner: str = Query(None)
                                        ):
    stmt = select(models.Advertisement)
    if title:
        stmt = stmt.where(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        stmt = stmt.where(models.Advertisement.description.ilike(f"%{description}%"))
    if price:
        stmt = stmt.where(models.Advertisement.price == price)
    if owner:
        stmt = stmt.where(models.Advertisement.owner == owner)
    result = await session.execute(stmt)
    ads = result.scalars().all()
    return ads

@app.delete("/advertisement/{ad_id}", tags=['Advertisement'], response_model=DeleteAdvertisementResponse)
async def delete_advertisement(ad_id: int, session: SessionDependency, token: TokenDependency):
    ad = await session.get(models.Advertisement, ad_id)
    if ad.owner_id != token.user_id and token.user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    await crud.delete_item(session, models.Advertisement, ad_id)
    return {"status": "success"}

@app.delete("/user/{us_id}", tags=['User'], response_model=DeleteUserResponse)
async def delete_user(us_id: int, session: SessionDependency, token: TokenDependency):
    if token.user.role != "admin" or token.user.role != "user":
        raise HTTPException(status_code=403, detail="Forbidden")
    await crud.delete_item(session, models.User, us_id)
    return {"status": "success"}

@app.post("/login", tags=["Login"], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    query = select(models.User).where(models.User.name == login_data.name)
    user = await session.scalar(query)
    if user is None:
        raise HTTPException(401, "Invalid credentionals")
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentionals")
    token = models.Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict

@app.post("/user", tags=['User'], response_model=CreateUserResponse)
async def create_user(user_data: CreateUserRequest, session: SessionDependency):
    user_dict = user_data.model_dump(exclude_unset=True)
    user_dict['password'] = auth.hash_password(user_dict['password'])
    user_orm_obj = models.User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.id_dict