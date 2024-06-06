// NewTrainServiceForm.tsx
// Jacob Lowe
import React, { useState, useEffect } from "react";
import type { TimePickerProps } from "antd";
import { Form, Input, Button, TimePicker } from "antd";

const NewTrainServiceForm: React.FC = () => {
  const [times, setTimes] = useState<string[]>([]);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);

  // Log every time the times array changes
  useEffect(() => {
    console.log("Times:", times);
  }, [times]);

  // Function to handle the time picker on change and set the current selected time
  const onChange: TimePickerProps["onChange"] = (time, timeString) => {
    if (typeof timeString === "string") {
      setSelectedTime(timeString);
      console.log("Time String:", timeString);
    }
  };
  // Function to handle the onAdd button click and add the selected time to the times array
  const onAdd = (values: any) => {
    if (selectedTime) {
      console.log("Adding:", values);
      setTimes((prevTimes) => [...prevTimes, selectedTime]);
    }
  };
  // Submit to the API on Click of the submit button
  const onFinish = (values: any) => {
    console.log("Submitting:", values);
    // POST request to API
  };

  return (
    <Form layout={"horizontal"} style={{ maxWidth: 600 }}>
      <Form.Item label="Name">
        <Input placeholder="input placeholder" />
      </Form.Item>
      <Form.Item label="New Time">
        <TimePicker use12Hours format="h:mm A" onChange={onChange} />;
      </Form.Item>
      <Form.Item label="List of Items">
        <div style={{ display: "flex", flexDirection: "row", gap: "10px" }}>
          {times.map((time, index) => (
            <span key={index}>{time}</span>
          ))}
        </div>
      </Form.Item>
      <Form.Item>
        <Button type="primary" onClick={onAdd}>
          Add time
        </Button>
        <Button type="primary" onClick={onFinish}>
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
};

export default NewTrainServiceForm;
