import logging
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Types checking in python


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Started the server")
app = FastAPI()

# def versus async def
# def for requests and sqlite3
# async def for httpx and aiohttp


# Setting up CORS middleware for information being able to be
# accessed from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Post(BaseModel):
    title: str
    content: str

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/api/v1/health")
async def health_check():
    logger.info("Request at health check endpoint")
    return {"status": "OK"}

@app.post("/api/v1/posts")
async def create_post(post: Post):
    logger.info(f"Request to create a new post with title: {post.title}")
    # post_id = db.insert(post)
    # return {"id": post_id, **post.dict()}
    return {"id": 1, "title": post.title, "content": post.content}


