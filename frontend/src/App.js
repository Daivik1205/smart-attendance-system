import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Students from './components/Students';
import Attendance from './components/Attendance';
import Layout from './components/Layout';
import { auth, database } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { ref, get } from 'firebase/database';
import { Spin, message } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      try {
        if (firebaseUser) {
          const uid = firebaseUser.uid;
          const snap = await get(ref(database, `users/${uid}`));
          
          if (!snap.exists()) {
            message.warning('User data not found. Please contact admin.');
            await auth.signOut();
            setUser(null);
            return;
          }

          const userData = snap.val();
          setUser({ ...userData, uid });
          
          // Redirect teachers from login/signup to students page
          if (['/login', '/signup'].includes(location.pathname)) {
            if (userData.role === 'teacher') {
              window.location.href = '/students';
            } else {
              window.location.href = '/attendance';
            }
          }
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error('Auth state error:', error);
        message.error('Error checking authentication status');
        setUser(null);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [location.pathname]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
      </div>
    );
  }

  return (
    <Routes>
      {!user ? (
        <>
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </>
      ) : (
        <Route 
          path="/" 
          element={<Layout user={user} setUser={setUser} />}
        >
          {user.role === 'teacher' ? (
            <>
              <Route path="students" element={<Students user={user} />} />
              <Route path="attendance" element={<Attendance user={user} />} />
              <Route index element={<Navigate to="students" replace />} />
              <Route path="*" element={<Navigate to="students" replace />} />
            </>
          ) : (
            <>
              <Route path="attendance" element={<Attendance user={user} />} />
              <Route index element={<Navigate to="attendance" replace />} />
              <Route path="*" element={<Navigate to="attendance" replace />} />
            </>
          )}
        </Route>
      )}
    </Routes>
  );
}

export default App;