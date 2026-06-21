from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_db
from schemas import UserCreate, UserUpdate, UserResponse
from crud import get_users, get_user, create_user, update_user, delete_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Example Metrics API", lifespan=lifespan)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
def root():
    return {"status": "ok", "message": "Prometheus metrics available at /metrics"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/users", response_model=UserResponse, status_code=201)
async def create(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, data)


@app.get("/users", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await get_users(db)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=204)
async def delete(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
