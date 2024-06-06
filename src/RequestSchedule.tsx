//  RequestSchedule.tsx
//  Jacob Lowe

import React from "react";
import { Form, TimePicker, Button } from "antd";

const RequestSchedule: React.FC = () => {
  return (
    <Form layout="horizontal" style={{ maxWidth: 600 }}>
      <h1> Request Train Line Schedule </h1>
      <Form.Item label="Requested Time">
        <TimePicker use12Hours format="h:mm A" />
      </Form.Item>
      <Button type="primary">Request Schedule</Button>
    </Form>
  );
};
export default RequestSchedule;
