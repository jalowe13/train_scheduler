// Api Service for the application
// Jacob Lowe

// This object contains functions that make requests to the API
const url: string = "http://127.0.0.1:8080";
const api_version: string = "/api/v1/";
export const apiService = {
  // This function makes a request to the health check endpoint
  async healthCheck() {
    try {
      const response = await fetch(`${url}${api_version}health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(
        "An error occurred while fetching the health check endpoint:",
        error
      );
      return null; // This needs to return the error somehow other than the console
    }
  },
};
