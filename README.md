

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
# Some other behavior assumptions:  
○ You can assume that all trains have the same schedule each day (i.e. no special schedules for weekends and holidays).  
○ If there are no remaining times after the passed-in time value when multiple trains will be in the station simultaneously, the service should return the first time of the day when multiple trains arrive at the station simultaneously (since that’s when it’ll first happen tomorrow).  
○ If there are no instances when multiple trains are in the station at the same time, this method should return no time.  
○ You may define the API contract for this service however you wish, including the format used for accepting and returning time arguments. The endpoint should return a 200 response for valid requests, and a 4xx request for invalid requests (with actual HTTP code at your discretion).
# Service State  
### This web service has a key-value store for keeping state, with the following calls and characteristics:  
● You can call the db.set(key, value) method (with syntax adapted to the language of your choosing) to set the value associated with a key.  
○ This method can accept any object type as ‘value’, and does not return a value (unless the language you’re using mandates a return type, in which case use your discretion and state your assumption).  
○ You can call the db.fetch(key) method (with syntax adapted to the language of your choosing) to retrieve the object set at a key.  This method returns the object set at that key if the key is defined, undefined if not.  
● You can call the db.keys() method (with syntax adapted to the language of your choosing) to return the list of all defined keys in the database. This function returns an empty list if none have been defined.  
● This key-value store is thread-safe.  The service needs to use this hypothetical key-value store (with only these three methods available).
### Expectations and Assumptions  
● You can use whatever language, framework, and tools you feel most comfortable with.  
● You can use whatever schema and data types for the service endpoints that you feel makes the most sense.  
● You can use whatever dependencies are useful to solve the problem.  
● You do not need to worry about user authentication or accreditation as part of the prompt. All endpoints can be public to anonymous users.  
● You may mock out the implementation of the key-value store endpoints however it makes sense to test/validate/compile your implementation. (Or not at all. It’s acceptable if the service does not run for lack of an implementation for the DB interface methods).  
● It’s OK to make additional assumptions that aren’t encoded in this prompt – just be sure to document them.  
● You may ask any questions you need to pursue this prompt, including questions to clarify assumptions around performance requirements, scale, etc.


# My Approach
## API Choice
Deciding between GraphQL and REST. 
- GraphQL is good for many complex queries and is more complex than REST and handles under and over-fetching better. It also puts everything into a singular endpoint that is parsed.
- REST is Simple and straight forward and a good, scalable API choice
- I compare the server response timings between both in this project

# Database choice
- Key Value Pairs are required and I will be using them specifically for caching as I wanted to dive deeper into how databases work especially relational databases.
- For my relational database I choice TimescaleDB. It extends off PostgreSQL and is used for large datasets of timestamped data and includes optimizations for this type of data. Its an API that is usable on the basic sense for SQL queries but can also be learned upon through further project research.

# Optimization Strategys
- On GET requests either from REST or GraphQL if a train name or timeset is not in a key value pair dictionary it will be added to one for caching purposes
- 3 Caches are used to minimize expensive Database calls
- Instance 1 - Key - Arrival Time, Value - List of Train Names
- Instance 2 - Key - Train Name, Value - List of Arrival Times
-  Instance 3 - Key - Arrival Time, Value - Closest Next Multiple Trains

[GraphQL - FastAPI (tiangolo.com)](https://fastapi.tiangolo.com/how-to/graphql/)
[FastAPI | 🍓 Strawberry GraphQL](https://strawberry.rocks/docs/integrations/fastapi#options)
Python Env managed by [[Conda]]
[Timescale Documentation | Install TimescaleDB from Docker container](https://docs.timescale.com/self-hosted/latest/install/installation-docker/)
[Timescale Documentation | Tables and hypertables](https://docs.timescale.com/getting-started/latest/tables-hypertables/)

Note:
GraphQL always returns 400 it receives a process. Throwing 200 in the body response of the message

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

## REST is better for smaller less complex Queries and is prefered over GraphQl because REST has a 50% reduction in response time from the server. When there are more database queries and entries that are needed this reduction is crucial.

This could be due to needing to parse the query statement. Once there's more complex data requirements and a potential for over and under-fetching, GraphQL would be preferred over REST. 

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
