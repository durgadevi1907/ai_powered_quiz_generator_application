import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import QuizForm from './components/QuizForm';
import QuizPage from './components/QuizPage';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Navbar from './components/navbar/Navbar';
import './App.css';

export interface Question {
  question: string;
  options: string[];
  answer: string;
}

export interface QuizData {
  questions: Question[];
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on load
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (token: string) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('token');
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Navbar isAuthenticated={isAuthenticated} onLogout={handleLogout} />
        <main>
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                !isAuthenticated ? (
                  <Login onLogin={handleLogin} />
                ) : (
                  <Navigate to="/quiz" />
                )
              } 
            />
            <Route 
              path="/register" 
              element={
                !isAuthenticated ? (
                  <Register />
                ) : (
                  <Navigate to="/quiz" />
                )
              } 
            />

            {/* Protected Routes */}
            <Route 
              path="/quiz" 
              element={
                isAuthenticated ? (
                  <QuizPage />
                ) : (
                  <Navigate to="/login" />
                )
              } 
            />
            <Route 
              path="/" 
              element={
                isAuthenticated ? (
                  <QuizForm />
                ) : (
                  <Navigate to="/login" />
                )
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

