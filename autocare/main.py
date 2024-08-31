import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import address, auth, users, vehicle, vehicle_problems

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vehicle.router)
app.include_router(vehicle_problems.router)
app.include_router(address.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods="*",
    allow_headers="*",
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
