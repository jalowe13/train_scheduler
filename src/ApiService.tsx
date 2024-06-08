// Api Service for the application
// Jacob Lowe

// This object contains functions that make requests to the API
const url: string = "http://127.0.0.1:8080";
const api_version: string = "/api/v1/";

// GraphQL API Functions
// Health Check for the GraphQL API
async function healthCheckGraphQL() {
  return null;
}
// Post to the GraphQL API
async function postGraphQL(endpoint: string, data: any) {
  console.log("[GRAPHQL] POSTING TO ENDPOINT:", endpoint, "WITH DATA:", data);
  return null;
}
// REST API Functions
// Generalized funciton to make POST requests to the API (DRY method)
async function postAPI(endpoint: string, body = null, options = {}) {
  console.log(
    "POSTING TO ENDPOINT:",
    endpoint,
    "WITH BODY:",
    body,
    "AND OPTIONS:",
    options
  );
  console.log(`POSTING ${url}${api_version}${endpoint}`);
  try {
    const response = await fetch(`${url}${api_version}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : null,
      ...options,
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("An error occurred while posting to the endpoint:", error);
    return null; // This needs to return the error somehow other than the console
  }
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
      return postGraphQL("posts", data);
    }
    return postAPI("posts", data);
  },
};
