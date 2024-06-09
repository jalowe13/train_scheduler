import logging
import psycopg2
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

# Helper functions for database connection
def print_fetch(cursor):
    rows = cursor.fetchall()
    for row in rows:
        logger.info(row)

# Test a sample insert
def test_insert(cursor):
        # Insert a test record
    TEST_VALUE = "NOW(), 'Test Train', '2024-06-08 23:39:35'"
    logger.log(logging.INFO, f"Inserting test record: {TEST_VALUE}")
    cursor.execute(f"""
        INSERT INTO {DB_NAME} ({TIME_COLUMN}, {TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN}) 
        VALUES ({TEST_VALUE});
        """)
    # Test Selection to print out Train name and Arrival_time columns
    #cursor.execute(f"SELECT {TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN} FROM {DB_NAME};")
    cursor.execute(f"SELECT {TRAIN_NAME_COLUMN} FROM {DB_NAME};")
    # Print out the rows
    logger.info("Printing out the rows of Name column")
    print_fetch(cursor)
    cursor.execute(f"SELECT {ARRIVAL_TIME_COLUMN} FROM {DB_NAME};")
    logger.info("Printing out the rows of Time column")
    print_fetch(cursor)
    cursor.execute(f"""
    DELETE FROM {DB_NAME} 
    WHERE {TRAIN_NAME_COLUMN} = 'Test Train' AND {ARRIVAL_TIME_COLUMN} = '2024-06-08 23:39:35';
    """)
    # Print out the rows
    try:
        print_fetch(cursor)
    except psycopg2.ProgrammingError as e:
        logger.info("No rows to print")




# Setting up the connection to the database
CONNECTION = "postgresql://postgres:password@127.0.0.1:5432/postgres"
TESTING = True
# New database connection
def connect_to_db():
    try:
        db = psycopg2.connect(CONNECTION)
        logger.info("Connected to the database")
        return db
    except psycopg2.Error as e:
        logger.info("Unable to connect to the database")
        logger.info(e.pgerror)
        logger.info(e.diag.message_detail)
        return None
logger.info("Connecting to the database")
db = connect_to_db() # Database connection

# Setup Database if it does not exist
if db is not None:
    cursor = db.cursor()
    ## TIMESTAMPTZ is the timestamp with timezone
    ## time is the time created in the database
    DB_NAME : str = "train_schedule"
    TIME_COLUMN : str = "time"
    TRAIN_NAME_COLUMN : str = "train_name"
    ARRIVAL_TIME_COLUMN : str = "arrival_time"
    NAME_IDX : str = "ix_train_name_time"
    cursor.execute(f"""
        CREATE TABLE {DB_NAME} (
            {TIME_COLUMN} TIMESTAMPTZ NOT NULL, 
            {TRAIN_NAME_COLUMN} TEXT NOT NULL,
            {ARRIVAL_TIME_COLUMN} TIMESTAMPTZ NOT NULL
        );
        """)
    cursor.execute(f"SELECT create_hypertable('{DB_NAME}', '{TIME_COLUMN}');")
    cursor.execute(f"CREATE INDEX {NAME_IDX} ON {DB_NAME} ({TRAIN_NAME_COLUMN}, time DESC);")
    test_insert(cursor) 
    logger.info("Database setup completed")
else:
    print("Failed to connect to the database")




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
# GraphQL API for the Train Schedule App
# Function to get the train
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
        logger.info(f"Adding train: {train_name}")

        # TODO: Add the train to the database


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
    if (len(post.arrival_time) == 0):
        raise HTTPException(status_code=400, detail="No arrival times provided")
    for time in post.arrival_time:
       check_time_format(time) 

    # TODO: Add the train to the database

    return {"id": 1, "train_name": post.train_name,
             "arrival_time": post.arrival_time}


