// src/components/Login.js
import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { ref, get } from 'firebase/database';
import { auth, database } from '../firebase';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, message, Typography, Card, Divider } from 'antd';
import { MailOutlined, LockOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const Login = ({ setUser }) => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async ({ email, password }) => {
    setLoading(true);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const uid = userCredential.user.uid;

      const userSnap = await get(ref(database, `users/${uid}`));
      const userData = userSnap.val();

      if (userData?.role) {
        setUser({ ...userData, uid });
        message.success('Login successful! Redirecting...');
        navigate(userData.role === 'teacher' ? '/students' : '/attendance');
      } else {
        message.error('Role not found. Please contact administrator.');
      }
    } catch (error) {
      message.error(error.message.includes('user-not-found') 
        ? 'User not found. Please check your email or sign up.'
        : error.message.includes('wrong-password')
        ? 'Incorrect password. Please try again.'
        : 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: '2rem' }}>
      <Card style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3}>Welcome Back</Title>
          <Text type="secondary">Sign in to continue</Text>
        </div>

        <Form
          name="loginForm"
          onFinish={onFinish}
          layout="vertical"
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
            <Input prefix={<MailOutlined />} placeholder="your@email.com" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Enter your password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              Log In
            </Button>
          </Form.Item>
        </Form>

        <Divider>or</Divider>

        <div style={{ textAlign: 'center' }}>
          <Text>Don't have an account?{' '}
            <Link to="/signup" style={{ fontWeight: 500 }}>
              Sign up now
            </Link>
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default Login;