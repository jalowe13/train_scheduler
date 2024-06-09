import "./App.css";
import React, { useCallback, useState } from "react";
import { Button, Switch, message } from "antd";
import { apiService } from "./ApiService.tsx";
import NewTrainServiceForm from "./Form.tsx";
import RequestSchedule from "./RequestSchedule.tsx";

// Train Line App
// Jacob Lowe

const App: React.FC = () => {
  // API Service State
  const [isGraphQL, setIsGraphQL] = useState(true);
  // Message State
  const [messageApi, contextHolder] = message.useMessage();
  const info = () => {
    messageApi.info("Request Submitted");
  };
  // Button click event handler
  const handleButtonClick = useCallback(
    async (apiFunction: (isGraphQL: boolean) => Promise<any>) => {
      console.log(`Button clicked!`);
      console.log(`GraphQL: ${isGraphQL}`);
      try {
        const data = await apiFunction(isGraphQL);
        console.log("Api data:", data);
        return data;
      } catch (error) {
        console.error(`Failed to fetch data`, error);
      }
    },
    [isGraphQL] // The array is the dependency list for the callback that holds all variables it depends on
  );
  return (
    <div className="App">
      <header className="App-header">
        {contextHolder}
        <NewTrainServiceForm
          handleButtonClick={handleButtonClick}
          info={info}
          isGraphQL={isGraphQL}
        />
        <RequestSchedule
          handleButtonClick={handleButtonClick}
          info={info}
          isGraphQL={isGraphQL}
        />
        <div>
          <h4>API Type</h4>
          <Switch
            checkedChildren="GraphQL"
            unCheckedChildren="REST"
            defaultChecked
            onChange={(checked) => setIsGraphQL(checked)}
          />
          <h5>Debug</h5>
          <Button onClick={() => handleButtonClick(apiService.healthCheck)}>
            Health Check
          </Button>
        </div>
      </header>
    </div>
  );
};

export default App;
