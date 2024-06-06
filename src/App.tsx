import "./App.css";
import React, { useCallback } from "react";
import { Button } from "antd";
import NewTrainServiceForm from "./Form.tsx";

// Train Line App
// Jacob Lowe

// This object contains functions that make requests to the API
const apiService = {
  // This function makes a request to the health check endpoint
  async healthCheck() {
    try {
      const response = await fetch("http://127.0.0.1:8080/api/v1/health");
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

const App: React.FC = () => {
  const handleButtonClick = useCallback(async () => {
    // Use callback to prevent infinite loop
    console.log(`Button clicked!`);
    const data = await apiService.healthCheck();
    if (data) {
      console.log(data);
    } else {
      console.error("Failed to fetch health check data");
    }
  }, []); // The array is the dependency list for the callback that holds
  //all variables it depends on
  return (
    <div className="App">
      <header className="App-header">
        <h1> New Train Line Schedule</h1>
        <NewTrainServiceForm />
        <Button onClick={() => handleButtonClick()}>Health Check</Button>
      </header>
    </div>
  );
};

export default App;
