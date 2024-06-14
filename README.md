
# Train Scheduler Project
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/a92cc8bd-ca30-4774-abdf-7e90be55ec7f)
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/abe6a9fa-b7ca-4a9e-a51c-6f38b90f4741)


# Problem Statement Breakdown
# Context
#### We have a single train station that can have an arbitrary number of different train lines running through it. (e.g. the Fulton Street stop of the NYC MTA, which hosts the 2, 3, 4, 5, A, C, J, and Z lines).  We would like a service to manage the schedules of the different trains that run through this specific station.

# Objective & Requirements  
#### Write a small web service (with API) that provides endpoints that track and manage the train schedules for this specific station.  
# Service Capability  
### This web service should have the following capability  
● A means for clients to post a schedule for a new train line that runs through this station. This post should accept the following information:  
○ The name of the train line (a string that contains up to four  alphanumeric characters, e.g. ‘EWR0’, ‘ALP5’, ‘TOMO’, etc)  
○ The list of times when this particular train arrives at this station. These are specific to the minute the train arrives (i.e. ‘9:53 PM’)  
● A means for clients to get the next time multiple trains are going to be arriving at this station in the same minute. This request should accept a time value as an argument, and return a timestamp that reflects the next time two or more trains will arrive at this station simultaneously after the submitted time value.  

Capability Restrictions
- Train Line name 4 char limit e.g. ‘EWR0’, ‘ALP5’, ‘TOMO’, etc)  
- Arrival times to the minute 9:53pm
- Request for multiple trains arriving in  the same minute
	- Input time value
	- Return time Next time two or more trains arrive at the same time after the submitted time value


# My Approach
## Front-End
### React
For all web server requests, I use the built-in JavaScript Fetch API
React handles use states and are efficient with state-based rendering and component-based architecture
### ANT UED
For usage as a component library for UI elements for speed of development
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/42bce0db-1e1e-4755-848f-45ebe0183a2f)

## Back-End
### Framework Choice
#### Electron
For usage of hosting web applications separate from a web browser environment in its own contained window. Useful for creating web apps.
Popular web applications that use this specific framework include Discord, Slack, Visual Studio Code

![image](https://github.com/jalowe13/train_scheduler/assets/40873986/cad7fb56-3ac9-491e-a8c2-24d809515504)

### Language Choice
#### Python
For fast development of backend web application services. Usually doesn't offer type safety like C++ but this can be fixed with the typing package (Specifically used this for the List Type for List of strings List[str])
#### Uvicorn ASGI Server
For async communication between the client and the server to allow multiple long-lived connections at once and hot reloading
#### Node.js
For scripting and automation of scripts to run the frontend and backend on command

![image](https://github.com/jalowe13/train_scheduler/assets/40873986/054003b1-490c-4686-ba9d-126b3dee5e5a)

### Data Storage Choice
#### Key-Value Pairs
Key Value Pairs are required and I will be using them specifically for caching as I wanted to dive deeper into how databases work, especially relational databases.
KVP.keys() is implemented but not used due to the implementation. Scenarios to use keys would be doing an operation over the whole data set

#### Relational Database
Docker container with TimescaleDB
- For my relational database, I chose TimescaleDB. It extends off PostgreSQL and is used for large datasets of timestamped data and includes optimizations using hyper tables for this type of data. It's an API that is usable in the basic sense for SQL queries but can also be learned through further project research.
Docker container for isolation and containerization

Why Relational?
- For handling structured data such as train name and time, and relating one set or column of data to another.
- SQL for complex queries
```sql
    sql_query = f"""
        SELECT DATE_TRUNC('minute', {ARRIVAL_TIME_COLUMN}) as arrival_time,ARRAY_AGG({TRAIN_NAME_COLUMN})
        FROM {DB_NAME}
        WHERE {ARRIVAL_TIME_COLUMN} > %s
        GROUP BY arrival_time
        HAVING COUNT({TRAIN_NAME_COLUMN}) > 1
        ORDER BY arrival_time
        LIMIT 1
    """
```
- Round time to the minute
- Aggregate Train Names into a single array
- Get the times after the arrival timestamp %s
- Only filter trains with multiple arrival times
- Order by the arrival time after %s
- Only return 1 group 

- Indexing, or composite indexes to speed up queries (Mentioned in TimescaleDB documentation)
	- Ex: Tuple of train time and arrival time

```sql
cursor.execute(f"CREATE INDEX {NAME_IDX} ON {DB_NAME} ({TRAIN_NAME_COLUMN}, {ARRIVAL_TIME_COLUMN} DESC);")
```
Indexing 

### API Choice

[FastAPI | 🍓 Strawberry GraphQL](https://strawberry.rocks/docs/integrations/fastapi#options)

[GraphQL - FastAPI (tiangolo.com)](https://fastapi.tiangolo.com/how-to/graphql/)

![image](https://github.com/jalowe13/train_scheduler/assets/40873986/cf7e19bf-6918-4f17-9b61-bca358516b95)


For designing the [[GraphQL]] (with Strawberry to define type schema) and [[REST]] [[API]]

Note:
GraphQL always returns 400 when it receives a process. Throwing 200 in the body response of the message

Deciding between GraphQL and REST. 
- GraphQL is good for many complex queries and is more complex than REST and handles under and over-fetching better. It also puts everything into a singular endpoint that is parsed.
- REST is Simple and straight forward and a good, scalable API choice
- I compare the server response timings between both in this project

## Optimization Strategies
- On GET requests either from REST or GraphQL if a train name or time set is not in a key-value pair dictionary it will be added to one for caching purposes
- 3 Caches are used to minimize expensive Database calls
- Instance 1 - Key - Arrival Time, Value - List of Train Names
- Instance 2 - Key - Train Name, Value - List of Arrival Times
-  Instance 3 - Key - Arrival Time, Value - Closest Next Multiple Trains


## For Improvements 
- The APIS can be more generalized
- Flask can help with smaller applications and minimizing component usage
- Django can help with load balancing if it becomes big and complex enough

Q: GraphQL and security?
# Tests 
## PUSH Request of 1 Train Schedule with 4 times
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/26b142de-e349-4713-9f85-13ed522b83b1)

REST better on push
## GET Request of 1 Train Schedule
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/45b00b14-dfd9-4e06-bb35-c78262c8cd9b)
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/7fda41fb-4ca5-4857-baff-b93e3970eb39)

First Database Second Cached Pull
REST better on GET

## Request Next Train After Time and At Time
![image](https://github.com/jalowe13/train_scheduler/assets/40873986/b493fb64-f663-470a-82c7-7fc7b99f278c)
- Second is always a cache
- [1-4] GraphQL Outputs for 2 Queuing Train at Time and 2 for queueing multiple trains after time
- [5-8] REST Outputs for 2 Queuing Train at Time and 2 for queueing multiple trains after time

## REST is better for smaller less complex Queries and is preferred over GraphQl because REST has a 50% reduction in response time from the server. When there are more database queries and entries that are needed this reduction is crucial.

This could be due to needing to parse the query statement. Once there are more complex data requirements and a potential for over and under-fetching, GraphQL would be preferred over REST. 

## Example Queries 
## Trains at specific time
```js
trainsAtTime(arrivalTimestamp: "2024-06-09 20:00:00")
```
## Trains for specific name:
```javascript
{
  timesForTrain(trainName: "FEWA")
}
```
## Example Mutations for Test Cases
## This works with all REST and GraphQL fetches
[Strawberry GraphiQL](http://127.0.0.1:8082/graphql)
```javascript
mutation {
  addTrain1: addTrain(trainName: "TRN1", arrivalTime: ["06:30 AM", "12:45 PM", "05:15 PM", "10:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain2: addTrain(trainName: "TRN2", arrivalTime: ["07:00 AM", "12:45 PM", "04:00 PM", "09:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain3: addTrain(trainName: "TRN3", arrivalTime: ["06:30 AM", "01:00 PM", "05:15 PM", "11:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain4: addTrain(trainName: "TRN4", arrivalTime: ["07:00 AM", "02:00 PM", "04:00 PM", "10:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain5: addTrain(trainName: "TRN5", arrivalTime: ["08:00 AM", "12:45 PM", "06:00 PM", "09:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain6: addTrain(trainName: "TRN6", arrivalTime: ["06:30 AM", "02:00 PM", "05:15 PM", "11:00 PM"]) {
    trainName
    arrivalTime
  }
  addTrain7: addTrain(trainName: "TRN7", arrivalTime: ["07:00 AM", "01:00 PM", "04:00 PM", "10:00 PM"]) {
    trainName
    arrivalTime
  }
}

```
