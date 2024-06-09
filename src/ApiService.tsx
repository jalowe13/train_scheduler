import dayjs from "dayjs";

// Api Service for the application
// Jacob Lowe

// This object contains functions that make requests to the API
const url: string = "http://127.0.0.1:8080";
const api_version: string = "/api/v1/";
const GRAPHQL_API: string = `${url}/graphql`;

// Helper functions

// GraphQL API Functions
// Health Check for the GraphQL API
async function healthCheckGraphQL() {
  return null;
}
// GraphQL Mutation
// Mutation to add a train to the GraphQL API
// Mutation with variables
const mutation = `
mutation AddTrain($train_name: String!, $arrival_time: [String!]!) {
  addTrain(trainName: $train_name, arrivalTime: $arrival_time) {
    trainName
    arrivalTime
  }
}
`;

// Function to fetch data from the GraphQL API
// Data can be a string that contains a time or a train name
async function fetchGraphQL(data: string, queryType: string) {
  if (data === null || data === "") {
    throw new Error("Data is null or empty");
  }
  console.log("DATA:", data);
  console.log("QUERY TYPE:", queryType);
  let query = "";
  const currentDateString = dayjs().format("YYYY-MM-DD");
  const dateTimeString = `${currentDateString} ${data}`;
  const formattedData = dayjs(dateTimeString, "YYYY-MM-DD h:mm A").format(
    "YYYY-MM-DD HH:mm:ss"
  );
  switch (queryType) {
    case "timesForTrain": // This is fine
      query = `{timesForTrain(trainName: "${data}")}`;
      break;
    case "trainsAtTime": // This is fine
      query = `{trainsAtTime(arrivalTimestamp: "${formattedData}")}`;
      break;
    case "trainsNextMultipleTimes":
      query = `{trainsNextMultipleTimes(arrivalTimestamp: "${formattedData}") {arrivalTime, trainNames}}`;
      console.debug("QUERY:", query);
      break;
    default:
      throw new Error(`Invalid query type: ${queryType}`);
  }
  console.log("FETCHING:", query);

  try {
    const response = await fetch(GRAPHQL_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    });

    if (!response.ok) {
      throw new Error(`Network response was not ok: ${response.statusText}`);
    }

    const responseBody = await response.json();

    if (responseBody.data === undefined) {
      throw new Error("Data is undefined");
    }

    if (responseBody.errors) {
      throw new Error(`GraphQL Error: ${responseBody.errors[0].message}`);
    }
    return responseBody.data;
  } catch (error) {
    console.error("An error occurred:", error);
    throw error;
  }
}

async function postGraphQL(query: string, variables = {}) {
  const body = JSON.stringify({ query, variables });
  const options = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  };

  const response = await fetch(GRAPHQL_API, options);
  const responseBody = await response.json();

  return responseBody.data;
}

// REST API Functions
// Generalized funciton to make POST requests to the API (DRY method)
async function postAPI(endpoint: string, body = null, options = {}) {
  const response = await fetch(`${url}${api_version}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null,
    ...options,
  });

  return response.json();
}

// Generalized function to make FETCH requests to the API (DRY method)
async function fetchAPI(endpoint: string, options = {}) {
  console.log("FETCHING ENDPOINT:", endpoint, "WITH OPTIONS:", options);
  try {
    const response = await fetch(`${url}${api_version}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`An error occurred while FETCHING check ${endpoint}`, error);
    return null; // This needs to return the error somehow other than the console
  }
}

export const apiService = {
  healthCheck(isGraphQL: boolean) {
    if (isGraphQL) {
      return healthCheckGraphQL();
    } else {
      return fetchAPI("health");
    }
  },
  submitForm(isGraphQL: boolean, data: any) {
    if (isGraphQL) {
      return postGraphQL(mutation, data)
        .then((data) => {
          if (data) {
            return data;
          }
          throw new Error("No data returned from the GraphQL API");
        })
        .catch((error) => {
          console.error("An error occurred:", error);
          throw error;
        });
    }
    return postAPI("posts", data);
  },
  fetch(isGraphQL: boolean, data: string | null, queryType?: string) {
    console.log("FETCHING:", data);
    if (data === null) {
      console.log("Data is null");
      throw new Error("Data is null");
    }
    if (isGraphQL) {
      if (!queryType) {
        throw new Error("Query type is required for GraphQL fetch");
      }
      return fetchGraphQL(data, queryType);
    }
    return fetchAPI("posts");
  },
};
