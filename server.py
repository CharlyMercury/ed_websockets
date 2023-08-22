# from python 
import logging
from pathlib import Path

# from uvicorn
import uvicorn

#from FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes.routes import app_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(app_routes)


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / 'ed_websocket\\src\\views\\static'),
    name="static",
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# To run uvicorn server:app --reload
