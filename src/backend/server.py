import logging
from typing import List
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Types checking in python


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

class Post(BaseModel):
    train_name: str
    arrival_time: List[str]

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/api/v1/health")
async def health_check():
    logger.info("Request at health check endpoint")
    return {"status": "OK"}

@app.post("/api/v1/posts")
async def create_post(post: Post):
    logger.info(f"Request to create a new post with title: {post.train_name}")
    # post_id = db.insert(post)
    # return {"id": post_id, **post.dict()}
    if (len(post.arrival_time) == 0):
        raise HTTPException(status_code=400, detail="No arrival times provided")
    for time in post.arrival_time:
        logger.info(f"Checking time: {time}")
        if len(time) != 8 and len(time) != 7:
            raise HTTPException(status_code=400, 
                                detail="Invalid time format: length")
        if ":" not in time:
            raise HTTPException(status_code=400, 
                                detail="Invalid time format: missing :")
    return {"id": 1, "train_name": post.train_name,
             "arrival_time": post.arrival_time}


