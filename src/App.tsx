import "./App.css";
import React, { useCallback, useState } from "react";
import { Switch, message } from "antd";
import NewTrainServiceForm from "./Form.tsx";
import RequestSchedule from "./RequestSchedule.tsx";

// Train Line App
// Jacob Lowe

const App: React.FC = () => {
  // API Service State
  const [isGraphQL, setIsGraphQL] = useState(true);
  // Message State
  const [messageApi, contextHolder] = message.useMessage();
  // Data State
  const [data, setData] = useState(null);
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
        setData(data); // Set the data state
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

        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div style={{ marginTop: "100px", marginRight: "100px" }}>
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
            <h6>API Type</h6>
            <Switch
              checkedChildren="GraphQL"
              unCheckedChildren="REST"
              defaultChecked
              onChange={(checked) => setIsGraphQL(checked)}
            />
          </div>

          <div style={{ maxWidth: "50%" }}>
            <h3>Output</h3>
            {data ? (
              <pre style={{ fontSize: "12px" }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            ) : null}
          </div>
        </div>
      </header>
    </div>
  );
};

export default App;
