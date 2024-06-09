// NewTrainServiceForm.tsx
// Jacob Lowe
import React, { useState, useEffect } from "react";
import type { TimePickerProps } from "antd";
import dayjs from "dayjs";
import { apiService } from "./ApiService.tsx";
import { Form, Input, Button, TimePicker } from "antd";
import { DeleteOutlined } from "@ant-design/icons";

// Interface for the POST data that can be sent
interface PostData {
  train_name: string;
  arrival_time: string[];
}

// Interface for the props of the NewTrainServiceForm component
// Function prop that takes apiFunction as an argument with PostData as an argument
// returns a Promise of any type, but the function itself
//  doesnt return anything
interface NewTrainServiceFormProps {
  handleButtonClick: (apiFunction: () => Promise<any>) => void;
  info: () => void;
  isGraphQL: boolean;
}

const NewTrainServiceForm: React.FC<NewTrainServiceFormProps> = ({
  handleButtonClick,
  info,
  isGraphQL,
}) => {
  // States
  // Times
  const [times, setTimes] = useState<string[]>([]); // List of times
  const [selectedTime, setSelectedTime] = useState<string | null>(null); // Currently selected time
  // Train Name
  const [name, setName] = useState("");
  // PostData state
  const [postData, setPostData] = useState<PostData>({
    train_name: "UNKNOWN TRAIN LINE",
    arrival_time: [],
  });

  // Every time the name or times changes update the postData arrival_time
  useEffect(() => {
    setPostData({ train_name: name, arrival_time: times });
  }, [name, times]);
  // Log every time the times array changes
  // useEffect(() => {
  //   console.log(postData);
  // }, [postData]);

  // Every time times changes change the postData arrival_time

  // Function to handle the time picker on change and set the current selected time
  const onChange: TimePickerProps["onChange"] = (time) => {
    if (time) {
      setSelectedTime(time.format("h:mm A"));
    } else {
      setSelectedTime(null);
    }
  };
  // Function to handle the onAdd button click and add the selected time to the times array
  const onAdd = (values: any) => {
    if (selectedTime && !times.includes(selectedTime)) {
      console.log("Adding:", values);
      setTimes((prevTimes) => [...prevTimes, selectedTime]);
    }
  };

  // Handle Submission of Form Data on Click if it is REST or GraphQL
  const handleSubmit = () => {
    info();
    handleButtonClick(() => apiService.submitForm(isGraphQL, postData));
    // Commented out to not clear the form after submission
    // setSelectedTime(null);
    // setTimes([]);
    // setName("");
  };

  // Submit to the API on Click of the submit button
  // const onFinish = (values: any) => {
  //   console.log("Submitting:", values);
  //   // POST request to API
  // };
  // Return the form with the time picker and the list of times
  return (
    <Form layout={"horizontal"} style={{ maxWidth: 600 }}>
      <h1> New Train Line Schedule</h1>
      <Form.Item label="Name">
        <Input
          style={{ width: "9ch" }}
          maxLength={4}
          value={name}
          onChange={(e) => setName(e.target.value.toUpperCase())}
        />
      </Form.Item>
      <Form.Item label="New Time">
        <TimePicker
          style={{ width: "16ch" }}
          use12Hours
          format="h:mm A"
          value={selectedTime ? dayjs(selectedTime, "h:mm A") : null}
          onChange={onChange}
        />
        ;
      </Form.Item>
      <Form.Item label="List of Items">
        <div style={{ display: "flex", flexDirection: "row", gap: "10px" }}>
          {times.map((time, index) => (
            <span key={index}>
              {time}
              <div>
                <Button
                  type="primary"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => {
                    // Remove the time at the index _ is the element not used in callback function
                    setTimes(times.filter((_, i) => i !== index));
                  }}
                />
              </div>
            </span>
          ))}
        </div>
      </Form.Item>
      <Form.Item>
        <Button type="primary" onClick={onAdd}>
          Add time
        </Button>
        <Button
          type="primary"
          // apiService.healthCheck isnt called until the button is clicked
          onClick={() => {
            handleSubmit();
          }}
        >
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
};

export default NewTrainServiceForm;
