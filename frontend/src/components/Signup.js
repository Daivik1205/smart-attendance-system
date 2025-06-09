// src/components/Signup.js
import React, { useState } from 'react';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { ref, set } from 'firebase/database';
import { auth, database } from '../firebase';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Select, Typography, Card, message } from 'antd';
import { MailOutlined, LockOutlined, IdcardOutlined, UserOutlined } from '@ant-design/icons';

const { Title, Text, Link } = Typography;
const { Option } = Select;

export default function Signup() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState('student');
  const navigate = useNavigate();

  const sendEnrollmentRequest = async (studentId, name) => {
    try {
      const response = await fetch('http://<YOUR_RPI_IP>:5000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          name: name
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send enrollment request');
      }

      return await response.json();
    } catch (error) {
      console.error('Enrollment request error:', error);
      throw error;
    }
  };

  const onFinish = async (values) => {
    setLoading(true);
    try {
      // Validate student ID and name if role is student
      if (values.role === 'student') {
        if (!values.studentId) {
          message.error('Please enter your student ID');
          setLoading(false);
          return;
        }
        if (!values.name) {
          message.error('Please enter your name');
          setLoading(false);
          return;
        }
      }

      // Create user with email and password
      const userCredential = await createUserWithEmailAndPassword(
        auth, 
        values.email, 
        values.password
      );
      const uid = userCredential.user.uid;

      // Save user data to database
      await set(ref(database, `users/${uid}`), {
        email: values.email,
        role: values.role,
        studentId: values.role === 'student' ? values.studentId : null,
        name: values.role === 'student' ? values.name : null,
        createdAt: new Date().toISOString()
      });

      // If student, send enrollment request to backend
      if (values.role === 'student') {
        await sendEnrollmentRequest(values.studentId, values.name);
        message.success('Account created successfully! Please complete biometric enrollment at the device.');
      } else {
        message.success('Account created successfully!');
      }

      navigate('/login');
      
    } catch (error) {
      let errorMessage = 'Signup failed. Please try again.';
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = 'Email already in use. Try logging in instead.';
      } else if (error.code === 'auth/weak-password') {
        errorMessage = 'Password should be at least 6 characters.';
      } else if (error.message.includes('enrollment request')) {
        errorMessage = 'Account created but enrollment request failed. Please contact support.';
      }
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      maxWidth: 500, 
      margin: '0 auto', 
      padding: '2rem',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Card 
        style={{ 
          width: '100%',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          borderRadius: 8
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3} style={{ marginBottom: 0 }}>Create Your Account</Title>
          <Text type="secondary">Join our learning community</Text>
        </div>

        <Form
          form={form}
          onFinish={onFinish}
          layout="vertical"
          onValuesChange={(changedValues) => {
            if (changedValues.role) setRole(changedValues.role);
          }}
          autoComplete="off"
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' },
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="your@email.com" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[
              { required: true, message: 'Please input your password!' },
              { min: 6, message: 'Password must be at least 6 characters!' },
            ]}
            hasFeedback
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="Create a password" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirm"
            label="Confirm Password"
            dependencies={['password']}
            hasFeedback
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('The two passwords do not match!'));
                },
              }),
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="Confirm your password" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="role"
            label="Role"
            initialValue="student"
          >
            <Select size="large">
              <Option value="student">Student</Option>
              <Option value="teacher">Teacher</Option>
            </Select>
          </Form.Item>

          {role === 'student' && (
            <>
              <Form.Item
                name="name"
                label="Full Name"
                rules={[{ required: true, message: 'Please input your full name!' }]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder="Enter your full name" 
                  size="large"
                />
              </Form.Item>

              <Form.Item
                name="studentId"
                label="Student ID"
                rules={[{ required: true, message: 'Please input your student ID!' }]}
              >
                <Input 
                  prefix={<IdcardOutlined />} 
                  placeholder="Enter your student ID" 
                  size="large"
                />
              </Form.Item>
            </>
          )}

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={loading}
              size="large"
              style={{ marginTop: 16 }}
            >
              Sign Up
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text>Already have an account?{' '}
            <Link 
              onClick={() => navigate('/login')} 
              style={{ cursor: 'pointer', fontWeight: 500 }}
            >
              Log in
            </Link>
          </Text>
        </div>
      </Card>
    </div>
  );
}