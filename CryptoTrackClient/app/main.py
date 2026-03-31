from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__ in (None, ""):
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from app.routers import users, cryptocurrencies, favorites, notifications, fiat
    from app.database import engine, Base
else:
    from .routers import users, cryptocurrencies, favorites, notifications, fiat
    from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CryptoTrack API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(cryptocurrencies.router)
app.include_router(favorites.router)
app.include_router(notifications.router)
app.include_router(fiat.router)


@app.get("/")
def root():
    return {"message": "CryptoTrack API is running"}
