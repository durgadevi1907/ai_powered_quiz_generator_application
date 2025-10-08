import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QuizForm from './components/QuizForm';
import QuizPage from './components/QuizPage';
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
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>QuizOMania</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<QuizForm />} />
            <Route path="/quiz" element={<QuizPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

