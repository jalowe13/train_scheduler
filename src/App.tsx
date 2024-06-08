import "./App.css";
import React, { useCallback } from "react";
import { Button, message } from "antd";
import { apiService } from "./ApiService.tsx";
import NewTrainServiceForm from "./Form.tsx";
import RequestSchedule from "./RequestSchedule.tsx";

// Train Line App
// Jacob Lowe

const App: React.FC = () => {
  // Message State
  const [messageApi, contextHolder] = message.useMessage();
  const info = () => {
    messageApi.info("Request Submitted");
  };
  // Button click event handler
  const handleButtonClick = useCallback(
    async (apiFunction: () => Promise<any>) => {
      console.log(`Button clicked!`);
      try {
        const data = await apiFunction();
        console.log(data);
      } catch (error) {
        console.error(`Failed to fetch data`, error);
      }
    },
    [] // The array is the dependency list for the callback that holds all variables it depends on
  );
  return (
    <div className="App">
      <header className="App-header">
        {contextHolder}
        <NewTrainServiceForm
          handleButtonClick={handleButtonClick}
          info={info}
        />
        <RequestSchedule />
        <div>
          <Button onClick={() => handleButtonClick(apiService.healthCheck)}>
            Health Check
          </Button>
        </div>
      </header>
    </div>
  );
};

export default App;
