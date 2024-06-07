import logging
import boto3
from typing import List
from fastapi import FastAPI, Response, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Types checking in python

# Backend Server for the Train Schedule App
# Jacob Lowe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Started the server")
app = FastAPI()


# Setting up CORS middleware for information being able to be
# accessed from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production needs actual domains
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"], # Accept, Content-Type, Authorization
)

# Helper functions
def check_time_format(time: str):
    logger.info(f"Checking time: {time}")
    if len(time) != 8 and len(time) != 7:
        raise HTTPException(status_code=400, 
                            detail="Invalid time format: length")
    if ":" not in time:
        raise HTTPException(status_code=400, 
                            detail="Invalid time format: missing :")
    
# REST API for GET and POST requests
class Post(BaseModel):
    train_name: str
    arrival_time: List[str]

# GET request to check if the server is running
@app.get("/api/v1/health")
async def health_check():
    logger.info("Request at health check endpoint")
    return {"status": "OK"}

# POST request to create a new train post schedule
@app.post("/api/v1/posts")
async def create_post(post: Post):
    logger.info(f"Request to create a new post with title: {post.train_name}")
    # post_id = db.insert(post)
    # return {"id": post_id, **post.dict()}
    if (len(post.arrival_time) == 0):
        raise HTTPException(status_code=400, detail="No arrival times provided")
    for time in post.arrival_time:
       check_time_format(time) 
    return {"id": 1, "train_name": post.train_name,
             "arrival_time": post.arrival_time}
@app.get("api/v1/get_train_schedule")

# Websockets for real-time updates on cached data from REST GET requests
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

