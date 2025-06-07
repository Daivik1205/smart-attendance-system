import React from 'react';
import { Layout as AntLayout, Menu } from 'antd';
import { useNavigate, Outlet, Link } from 'react-router-dom';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';

const { Header, Content, Footer } = AntLayout;

const Layout = ({ user, setUser }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut(auth);
    setUser(null);
    navigate('/login');
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: 'white', fontWeight: 'bold', fontSize: 18 }}>Smart Attendance</div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[]}
          items={[
            { key: 'attendance', label: <Link to="/attendance">Attendance</Link> },
            ...(user.role === 'teacher' ? [{ key: 'students', label: <Link to="/students">Students</Link> }] : []),
            { key: 'logout', label: <span onClick={handleLogout} style={{ cursor: 'pointer' }}>Logout</span> },
          ]}
        />
      </Header>
      <Content style={{ padding: '20px 50px' }}>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center' }}>©2025 Smart Attendance</Footer>
    </AntLayout>
  );
};

export default Layout;
