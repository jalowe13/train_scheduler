import logging
import psycopg2
import typing
import strawberry
import threading
from typing import List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Types checking in python
from strawberry.fastapi import GraphQLRouter

# Backend Server for the Train Schedule App
# Jacob Lowe
# This file is the backend server that shows both REST and GraphQL APIs

# Included is a hypothetical key value store database for the train schedule
# But it is imporantly used as a cache for the train schedule data

# Instance 1 - Key - Arrival Time, Value - List of Train Names
# Instance 2 - Key - Train Name, Value - List of Arrival Times

class KeyValueStore:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def set(self, key, values):
        with self.lock:
            logging.info(f"Setting value for {key}: {values}")
            self.store[key] = list(values)

    def fetch(self, key):
        with self.lock:
            logging.info(f"~~~~~~~~~~~~~~~~~~~~~~~~Fetching value for {key}")
            value = self.store.get(key)
            logging.info(f"~~~~~~~~~~~~~~~~~~~~~~~~Value: {value}")
            return value
    def keys(self):
        with self.lock:
            logging.info(f"Fetching keys")
            logging.info(f"Keys: {list(self.store.keys())}")
            return list(self.store.keys())


# Setting up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Started the server")
logger.info("You can access strawberry GraphQL playground at http://127.0.0.1:8080/graphql")
# Setting up the FastAPI app
app = FastAPI()

# Helper functions for database connection
def print_fetch(cursor):
    if cursor.description is not None:  # Check if there are results to fetch
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    else:
        print("No results to fetch.")

# Select Name and Times to print
def select_name_time(cursor):
    # Test Selection to print out Train name and Arrival_time columns
    cursor.execute(f"SELECT {TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN} FROM {DB_NAME};")
    print_fetch(cursor)

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
    ## train_name is the name of the train
    ## arrival_time is the time the train arrives
    DB_NAME : str = "train_schedule"
    TIME_COLUMN : str = "time"
    TRAIN_NAME_COLUMN : str = "train_name"
    ARRIVAL_TIME_COLUMN : str = "arrival_time"
    NAME_IDX : str = "ix_train_name_time"
    cursor.execute(f"""
        CREATE TABLE {DB_NAME} (
            {TIME_COLUMN} TIMESTAMPTZ NOT NULL DEFAULT NOW(), 
            {TRAIN_NAME_COLUMN} TEXT NOT NULL,
            {ARRIVAL_TIME_COLUMN} TIMESTAMPTZ NOT NULL
        );
        """)
    cursor.execute(f"SELECT create_hypertable('{DB_NAME}', '{ARRIVAL_TIME_COLUMN}');")
    cursor.execute(f"CREATE INDEX {NAME_IDX} ON {DB_NAME} ({TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN} DESC);")
    logger.info("Database setup completed")
else:
    print("Failed to connect to the database")

kvs_arrival = KeyValueStore() # Arrival Time to Train Names
kvs_train = KeyValueStore() # Train Name to Arrival Times   

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

# Retrieve data from cache or db
# sql_params is a tuple to prevent SQL injection
# %s is a placeholder for a paramater
# Because 'sql_params' is a tuple, the SQL engine treats its values as data, not part of the SQL command.
# This means that even if a value in 'sql_params' contains SQL commands, they will not be executed.
def fetch_cache_or_db(cache, key, sql_query, sql_params):
    # Fetch all keys from the cache
    cached_keys = cache.keys()

    # Check if the key is in the cache
    if key in cached_keys:
        logger.info("Key found in cache")
        data = cache.fetch(key)
        logger.info(data)
    else:
        logger.info(f"{key} not found in cache")
        cursor.execute(sql_query, sql_params)
        data = cursor.fetchall()
        # Cache the result after doing database operation
        cache.set(key, data)

    return data

# GraphQL API for the Train Schedule App
# Function to get the train
# Defining the Train and Query classes
@strawberry.type
class Train:
    train_name: str
    arrival_time: List[str]

# Returns the arrival time and train names used for getting next multiple trains at a time
@strawberry.type
class TrainArrival:
    arrival_time: str
    train_names: List[str]

@strawberry.type
class Query:
    # Method to grab a time and all trains at that time from the cache
    # Input - arrival timestamp '2024-06-09 10:55:00'
    # Returns - List of train names
    # Test Selection of all trains at specific time
    @strawberry.field
    def trains_at_time(self, arrival_timestamp: str) -> List[str]:
        logger.info(arrival_timestamp)

        sql_query = f"""
            SELECT {TRAIN_NAME_COLUMN} 
            FROM {DB_NAME} 
            WHERE TO_CHAR({ARRIVAL_TIME_COLUMN}, 'YYYY-MM-DD HH24:MI:SS') = %s
        """
        trains = fetch_cache_or_db(kvs_arrival, arrival_timestamp, sql_query, (arrival_timestamp,))
        if not trains:
            error_detail = f"No trains found for time: '{arrival_timestamp}'"
            logger.error(error_detail)
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            logger.info("Trains found")
            train_names = [train_tuple[0] for train_tuple in trains]
        return train_names
    
    # Method to grab the next multiple trains after a specific time
    # Input - arrival timestamp '2024-06-09 10:55:00'
    # Returns - Arrival time and train names
    @strawberry.field
    def trains_next_multiple_times(self, arrival_timestamp: str) -> TrainArrival:
        logger.info(arrival_timestamp)
        time_to_query = arrival_timestamp # replace with the time you want to query
        sql_query = f"""
            SELECT DATE_TRUNC('minute', {ARRIVAL_TIME_COLUMN}) as arrival_time, ARRAY_AGG({TRAIN_NAME_COLUMN})
            FROM {DB_NAME}
            WHERE {ARRIVAL_TIME_COLUMN} > %s
            GROUP BY arrival_time
            HAVING COUNT({TRAIN_NAME_COLUMN}) > 1
            ORDER BY arrival_time
            LIMIT 1
        """
        result = fetch_cache_or_db(kvs_arrival, time_to_query, sql_query, (time_to_query,))
        if not result:
            error_detail = f"No simultaneous trains found after time: '{arrival_timestamp}'"
            logger.error(error_detail)
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            arrival_time, train_names = result[0]
            logger.info(f"Next simultaneous trains found at {arrival_time}: {train_names}")

        return TrainArrival(arrival_time=arrival_time, train_names=train_names)

    
    # Method to grab a train and all times for that train from the cache
    # Input - train name 'Train A'
    # Returns - List of arrival times
    # Test Selection of all times for a specific train
    @strawberry.field
    def times_for_train(self, train_name: str) -> List[str]:
        logger.info(train_name)
        sql_query = f"""
            SELECT {ARRIVAL_TIME_COLUMN} 
            FROM {DB_NAME} 
            WHERE {TRAIN_NAME_COLUMN} = %s
        """
        times = fetch_cache_or_db(kvs_train, train_name, sql_query, (train_name,))
        if not times:
            error_detail = f"No times found for train: '{train_name}'"
            logger.error(error_detail)
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            logger.info("Times found")
            arrival_times = [time_tuple[0] for time_tuple in times]
        return arrival_times

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_train(self, train_name: str, arrival_time: List[str]) -> Train:
        if (len(arrival_time) == 0):
            raise HTTPException(status_code=400, detail="No arrival times provided")
        check_name_format(train_name)
        for time in arrival_time:
            check_time_format(time)
        logger.info(f"Adding train: {train_name}")
        # Get current date as a string
        logger.info("Adding train to the database")
        current_date = datetime.now().strftime('%Y-%m-%d')
        total_rows_inserted = 0 # Total rows inserted
        # Fetch existing arrival times for the train
        for time in arrival_time:
            logger.info(f"arrival_time: {time}")
            arrival_time_24h = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')
            # Concatenate current date with arrival time
            arrival_timestamp = f"{current_date} {arrival_time_24h}"
            logger.info(f"arrival_timestamp: {arrival_timestamp}")
            # TODO: Check if entry already exists in the Database before adding
            cursor.execute(f"""
                INSERT INTO {DB_NAME} ({TIME_COLUMN}, {TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN}) 
                VALUES (NOW(),%s,%s );
                """, (train_name, arrival_timestamp))
            select_name_time(cursor)
            total_rows_inserted += 1
        print(f"Total rows inserted: {total_rows_inserted}")
        return Train(train_name=train_name, arrival_time=arrival_time)

# TODO: Delete database button

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


