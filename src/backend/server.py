import logging
import boto3
import typing
import strawberry
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Types checking in python
from strawberry.fastapi import GraphQLRouter

# Backend Server for the Train Schedule App
# Jacob Lowe
# This file is the backend server that shows both REST and GraphQL APIs

# Setting up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Started the server")
logger.info("You can access strawberry GraphQL playground at http://127.0.0.1:8080/graphql")
# Setting up the FastAPI app
app = FastAPI()
# GraphQL API for the Train Schedule App
# Function to get the train


# Helper functions
def check_name_format(name: str):
    logger.info(f"Checking name: {name}")
    if len(name) < 3:
        raise HTTPException(status_code=400, 
                            detail="Invalid name format: length")
    if not name.isalnum():
        raise HTTPException(status_code=400, 
                            detail="Invalid name format: not alpha")

# Function to check the time format
def check_time_format(time: str):
    logger.info(f"Checking time: {time}")
    if len(time) != 8 and len(time) != 7:
        raise HTTPException(status_code=400, 
                            detail="Invalid time format: length")
    if ":" not in time:
        raise HTTPException(status_code=400, 
                            detail="Invalid time format: missing :")
    
    
def get_trains():
    return [
        Train(
            train_name="DSFF",
            arrival_time=["12:00 PM", "11:00 AM"],
        ),
        Train(
            train_name="GFAE",
            arrival_time=["11:00 PM", "11:57 AM"],
        )
    ]

# Defining the Train and Query classes
@strawberry.type
class Train:
    train_name: str
    arrival_time: List[str]

@strawberry.type
class Query:
    trains: typing.List[Train] = strawberry.field(resolver=get_trains)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_train(self, train_name: str, arrival_time: List[str]) -> Train:
        if (len(arrival_time) == 0):
            logger.info("No arrival times provided!!!!!!!!!!!!!!!!!!!!!")
            raise HTTPException(status_code=400, detail="No arrival times provided")
        check_name_format(train_name)
        for time in arrival_time:
            check_time_format(time)
        print(f"Adding train: {train_name}")
        return Train(train_name=train_name, arrival_time=arrival_time)


# Setting up the GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# Setting up CORS middleware for information being able to be
# accessed from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production needs actual domains
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"], # Accept, Content-Type, Authorization
)


    
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
    check_name_format(post.train_name)
    # post_id = db.insert(post)
    # return {"id": post_id, **post.dict()}
    if (len(post.arrival_time) == 0):
        raise HTTPException(status_code=400, detail="No arrival times provided")
    for time in post.arrival_time:
       check_time_format(time) 
    return {"id": 1, "train_name": post.train_name,
             "arrival_time": post.arrival_time}


