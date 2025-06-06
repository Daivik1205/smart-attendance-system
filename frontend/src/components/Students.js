import React, { useState, useEffect } from 'react';
import { db } from '../firebase';
import { ref, onValue } from 'firebase/database';
import { Table, Button, Modal, Form, Input, message } from 'antd';
import 'antd/dist/antd.css';

const { TextArea } = Input;

function Students() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = () => {
    setLoading(true);
    try {
      const studentsRef = ref(db, 'students');
      onValue(studentsRef, (snapshot) => {
        const data = snapshot.val();
        const studentsList = [];
        
        if (data) {
          Object.keys(data).forEach(studentId => {
            studentsList.push({
              key: studentId,
              id: studentId,
              name: data[studentId].name,
              registeredAt: new Date(data[studentId].registered_at).toLocaleString()
            });
          });
          setStudents(studentsList);
        }
      });
    } catch (error) {
      message.error('Failed to fetch students');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Registered At', dataIndex: 'registeredAt', key: 'registeredAt' },
  ];

  return (
    <div className="students-container">
      <h1>Student Management</h1>
      <div className="controls">
        <Button type="primary" onClick={() => setVisible(true)}>
          Add Student
        </Button>
        <Button onClick={fetchStudents} loading={loading}>
          Refresh
        </Button>
      </div>
      <Table
        columns={columns}
        dataSource={students}
        loading={loading}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
}

export default Students;