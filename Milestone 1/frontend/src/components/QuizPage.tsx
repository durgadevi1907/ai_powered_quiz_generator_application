import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { QuizData } from '../App';
import './QuizPage.css';

const QuizPage: React.FC = () => {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<string[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [quizTopic, setQuizTopic] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const initializeQuiz = async () => {
      // Get quiz data from sessionStorage
      const storedQuizData = sessionStorage.getItem('quizData');
      const storedTopic = sessionStorage.getItem('quizTopic');
      const storedQuizId = sessionStorage.getItem('quizId');
      
      if (!storedQuizId) {
        // If no quiz ID, redirect to home
        navigate('/');
        return;
      }

      if (!storedQuizData || !storedTopic) {
        // Try to fetch quiz data using stored ID
        try {
          const token = localStorage.getItem('token');
          const response = await fetch(`/api/quiz/${storedQuizId}`, {
            headers: {
              'Authorization': token || ''
            }
          });

          if (!response.ok) {
            throw new Error('Failed to fetch quiz data');
          }

          const data = await response.json();
          sessionStorage.setItem('quizData', JSON.stringify(data));
          sessionStorage.setItem('quizTopic', data.topic);
          
          const formattedData: QuizData = {
            questions: data.questions.map((q: any) => ({
              question: q.question,
              options: q.options || [],
              answer: q.answer
            }))
          };
          
          setQuizData(formattedData);
          setQuizTopic(data.topic);
          setSelectedAnswers(new Array(formattedData.questions.length).fill(''));
          return;
        } catch (error) {
          console.error('Error fetching quiz data:', error);
          navigate('/');
          return;
        }
      }

      try {
        const parsedData = JSON.parse(storedQuizData);
        
        // Check if the data has the correct structure
        if (!parsedData.questions || !Array.isArray(parsedData.questions)) {
          throw new Error('Invalid quiz data structure');
        }
        
        // Transform the data into QuizData structure
        const formattedData: QuizData = {
          questions: parsedData.questions.map((q: any) => ({
            question: q.question,
            options: q.options || [],
            answer: q.answer
          }))
        };
        
        setQuizData(formattedData);
        setQuizTopic(storedTopic);
        setSelectedAnswers(new Array(formattedData.questions.length).fill(''));

      } catch (error) {
        console.error('Error parsing quiz data:', error);
        navigate('/');
      }
    };

    initializeQuiz();
  }, [navigate]);

  const handleAnswerSelect = (answer: string) => {
    const newAnswers = [...selectedAnswers];
    newAnswers[currentQuestion] = answer;
    setSelectedAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < (quizData?.questions.length || 0) - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      const score = calculateScore();
      const token = localStorage.getItem('token');
      const quizId = sessionStorage.getItem('quizId');
      
      if (!quizId) {
        console.error('No quiz ID found');
        return;
      }

      // Submit quiz results
      const response = await fetch('/api/quiz/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token || ''
        },
        body: JSON.stringify({
          quiz_id: parseInt(quizId),
          topic: quizTopic,
          score: score,
          total_questions: quizData?.questions.length || 0,
          answers: JSON.stringify(selectedAnswers)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Failed to submit quiz results:', errorData);
        return;
      }
      
      // Only clear storage and show results after successful submission
      sessionStorage.removeItem('quizId');
      sessionStorage.removeItem('quizData');
      sessionStorage.removeItem('quizTopic');
      setShowResults(true);
      
      // Refresh the dashboard data
      navigate('/dashboard', { replace: true });
      
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  const calculateScore = () => {
    if (!quizData) return 0;
    
    let correct = 0;
    quizData.questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.answer) {
        correct++;
      }
    });
    return correct;
  };

  const getScorePercentage = () => {
    if (!quizData) return 0;
    return Math.round((calculateScore() / quizData.questions.length) * 100);
  };

  const handleRetakeQuiz = () => {
    setCurrentQuestion(0);
    setSelectedAnswers(new Array(quizData?.questions.length || 0).fill(''));
    setShowResults(false);
  };

  const handleNewQuiz = () => {
    sessionStorage.removeItem('quizData');
    sessionStorage.removeItem('quizTopic');
    navigate('/');
  };

  if (!quizData) {
    return <div className="loading">Loading quiz...</div>;
  }

  if (showResults) {
    const score = calculateScore();
    const percentage = getScorePercentage();
    
    return (
      <div className="quiz-container">
        <div className="quiz-card results-card">
          <h2>Quiz Results</h2>
          <div className="score-display">
            <div className="score-circle">
              <span className="score-percentage">{percentage}%</span>
              <span className="score-fraction">{score}/{quizData.questions.length}</span>
            </div>
          </div>
          
          <div className="results-summary">
            <h3>Topic: {quizTopic}</h3>
            <p>You got {score} out of {quizData.questions.length} questions correct!</p>
          </div>

          <div className="question-review">
            <h4>Review Your Answers:</h4>
            {quizData.questions.map((question, index) => (
              <div key={index} className="review-item">
                <p className="review-question">{index + 1}. {question.question}</p>
                <div className="review-answers">
                  <p className={`review-answer ${selectedAnswers[index] === question.answer ? 'correct' : 'incorrect'}`}>
                    Your answer: {selectedAnswers[index] || 'Not answered'}
                  </p>
                  {selectedAnswers[index] !== question.answer && (
                    <p className="review-answer correct">
                      Correct answer: {question.answer}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="results-actions">
            <button onClick={handleRetakeQuiz} className="btn btn-secondary">
              Retake Quiz
            </button>
            <button onClick={handleNewQuiz} className="btn btn-primary">
              Create New Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  const question = quizData.questions[currentQuestion];
  const isLastQuestion = currentQuestion === quizData.questions.length - 1;
  const allQuestionsAnswered = selectedAnswers.every(answer => answer !== '');

  return (
    <div className="quiz-container">
      <div className="quiz-card">
        <div className="quiz-header">
          <h2>{quizTopic}</h2>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((currentQuestion + 1) / quizData.questions.length) * 100}%` }}
            ></div>
          </div>
          <p className="question-counter">
            Question {currentQuestion + 1} of {quizData.questions.length}
          </p>
        </div>

        <div className="question-section">
          <h3 className="question-text">{question.question}</h3>
          
          <div className="options-container">
            {question.options.map((option, index) => (
              <button
                key={index}
                className={`option-btn ${selectedAnswers[currentQuestion] === option ? 'selected' : ''}`}
                onClick={() => handleAnswerSelect(option)}
              >
                <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-navigation">
          <button 
            onClick={handlePrevious} 
            disabled={currentQuestion === 0}
            className="btn btn-secondary"
          >
            Previous
          </button>
          
          <div className="nav-center">
            {selectedAnswers[currentQuestion] && (
              <span className="answer-indicator">✓ Answered</span>
            )}
          </div>
          
          {isLastQuestion ? (
            <button 
              onClick={handleSubmit}
              disabled={!allQuestionsAnswered}
              className="btn btn-primary"
            >
              Submit Quiz
            </button>
          ) : (
            <button 
              onClick={handleNext}
              className="btn btn-primary"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizPage;
