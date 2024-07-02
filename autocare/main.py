from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import models
from database import engine
from routers import users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods="*",
    allow_headers="*",
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
