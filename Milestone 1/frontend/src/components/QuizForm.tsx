import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './QuizForm.css';

const QuizForm: React.FC = () => {
  const [topic, setTopic] = useState('');
  const [numberQuestions, setNumberQuestions] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    if (numberQuestions < 1 || numberQuestions > 20) {
      setError('Number of questions must be between 1 and 20');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/generate-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          number_questions: numberQuestions,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Store quiz data in sessionStorage to pass to quiz page
      sessionStorage.setItem('quizData', JSON.stringify(data));
      sessionStorage.setItem('quizTopic', topic.trim());
      
      // Navigate to quiz page
      navigate('/quiz');
    } catch (err) {
      console.error('Error generating questions:', err);
      setError('Failed to generate questions. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="quiz-form-container">
      <div className="quiz-form-card">
        <h2>Create Your Quiz</h2>
        <p className="subtitle">Generate personalized quizzes on any topic</p>
        
        <form onSubmit={handleSubmit} className="quiz-form">
          <div className="form-group">
            <label htmlFor="topic">Topic</label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a topic (e.g., Chemistry, History, Programming)"
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="numberQuestions">Number of Questions</label>
            <input
              type="number"
              id="numberQuestions"
              value={numberQuestions}
              onChange={(e) => setNumberQuestions(parseInt(e.target.value) || 1)}
              min="1"
              max="20"
              disabled={loading}
              required
            />
            <small>Choose between 1 and 20 questions</small>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="generate-btn">
            {loading ? (
              <>
                <span className="spinner"></span>
                Generating Questions...
              </>
            ) : (
              'Generate Quiz'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QuizForm;

