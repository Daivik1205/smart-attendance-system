import React, { useEffect, useState } from 'react';
import { Table, Button, Form, Input, message } from 'antd';
import { ref, onValue, push, set } from 'firebase/database';
import { database } from '../firebase';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [form] = Form.useForm();

  useEffect(() => {
    const studentsRef = ref(database, 'students');
    onValue(studentsRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        const list = Object.entries(data).map(([key, val]) => ({
          student_id: key,
          name: val.name,
        }));
        setStudents(list);
      }
    });
  }, []);

  const onFinish = async (values) => {
    try {
      const res = await fetch('http://<YOUR-RPI-IP>:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });

      if (res.ok) {
        message.success('Student registered! Proceed with fingerprint and face scan.');
        form.resetFields();
      } else {
        message.error('Failed to register student.');
      }
    } catch (err) {
      console.error(err);
      message.error('Could not connect to backend.');
    }
  };

  const columns = [
    { title: 'Student ID', dataIndex: 'student_id', key: 'student_id' },
    { title: 'Full Name', dataIndex: 'name', key: 'name' },
  ];

  return (
    <div>
      <h2>Registered Students</h2>
      <Table dataSource={students} columns={columns} rowKey="student_id" />

      <h2 style={{ marginTop: 40 }}>Add New Student</h2>
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item name="student_id" label="Student ID" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="name" label="Full Name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Begin Biometric Enrollment
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Students;
