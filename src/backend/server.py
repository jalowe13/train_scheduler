import logging
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware


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

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/api/v1/health")
async def health_check():
    logger.info("Request at health check endpoint")
    return {"status": "OK"}

@app.get("/api/v1/submit")
async def submit():
    logger.info("Request at submit endpoint")
    return {"status": "OK"}


