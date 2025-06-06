import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { auth } from './firebase';
import Login from './components/Login';
import Attendance from './components/Attendance';
import Students from './components/Students';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <div className="app">
        <Switch>
          <Route exact path="/login">
            {user ? <Redirect to="/attendance" /> : <Login />}
          </Route>
          <PrivateRoute path="/attendance" user={user}>
            <Attendance />
          </PrivateRoute>
          <PrivateRoute path="/students" user={user}>
            <Students />
          </PrivateRoute>
          <Route path="/">
            {user ? <Redirect to="/attendance" /> : <Redirect to="/login" />}
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

function PrivateRoute({ children, user, ...rest }) {
  return (
    <Route
      {...rest}
      render={({ location }) =>
        user ? (
          children
        ) : (
          <Redirect
            to={{
              pathname: "/login",
              state: { from: location }
            }}
          />
        )
      }
    />
  );
}

export default App;