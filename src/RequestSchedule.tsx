//  RequestSchedule.tsx
//  Jacob Lowe

import React, { useState } from "react";
import { apiService } from "./ApiService.tsx";
import type { TimePickerProps } from "antd";
import dayjs from "dayjs";
import { Form, TimePicker, Button, Input } from "antd";

interface RequestScheduleProps {
  handleButtonClick: (apiFunction: () => Promise<any>) => any;
  info: () => void;
  isGraphQL: boolean;
}

const RequestSchedule: React.FC<RequestScheduleProps> = ({
  handleButtonClick,
  info,
  isGraphQL,
}) => {
  // States
  const [requestedTrain, setRequestedTrain] = useState<string>(""); // Requested Train
  const [requestedTime, setRequestedTime] = useState<string | null>(null); // Requested Time
  const onChange: TimePickerProps["onChange"] = (time) => {
    if (time) {
      setRequestedTime(time.format("h:mm A"));
    } else {
      setRequestedTime(null);
    }
  };
  return (
    <Form layout="horizontal" style={{ maxWidth: 600 }}>
      <h1> Request Train Line Schedule </h1>
      <Form.Item label="Requested Train">
        <Input
          style={{ width: "9ch" }}
          maxLength={4}
          value={requestedTrain}
          onChange={(e) => setRequestedTrain(e.target.value.toUpperCase())}
        />
      </Form.Item>
      <Button
        type="primary"
        onClick={() =>
          handleButtonClick(() => apiService.fetch(isGraphQL, requestedTrain))
            .then((data) => {
              // handle the returned data here
              console.log("I got the data for the train!");
              console.log(data);
            })
            .catch((error) => {
              // handle any errors here
              console.error(error);
            })
        }
      >
        Request Schedule by Train
      </Button>
      <Form.Item label="Requested Time">
        <TimePicker
          style={{ width: "16ch" }}
          use12Hours
          format="h:mm A"
          value={requestedTime ? dayjs(requestedTime, "h:mm A") : null}
          onChange={onChange}
        />
      </Form.Item>
      <Button
        type="primary"
        onClick={() =>
          handleButtonClick(() => apiService.fetch(isGraphQL, requestedTime))
            .then((data) => {
              // handle the returned data here
              console.log("I got the data for the time!");
              console.log(data);
            })
            .catch((error) => {
              // handle any errors
              console.error(error);
            })
        }
      >
        Request Schedule by Time
      </Button>
    </Form>
  );
};
export default RequestSchedule;
