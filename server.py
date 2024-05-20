# from python 
import logging
import os
from pathlib import Path

# from uvicorn
import uvicorn

#from FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes.routes import app_routes
from fastapi.middleware.cors import CORSMiddleware


script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "src/views/static/")

# app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")


app = FastAPI()
app.include_router(app_routes)

app.mount("/static", StaticFiles(directory=st_abs_file_path ), name="static")


"""app.mount(
    "/static",
      
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / 'ed_websocket/src/views/static'),
    name="static",
)"""

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://192.168.100.7:8080",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5000",
    "http://192.168.0.22:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# To run uvicorn server:app --reload
# web: uvicorn server:app --host=0.0.0.0 --port=${PORT:-5000} --ws-ping-interval 300 --ws-ping-timeout 300
# web: uvicorn --host=0.0.0.0 --port=$PORT --ws-ping-interval 300 --ws-ping-timeout 300 --workers 1 server:app