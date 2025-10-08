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
    // Get quiz data from sessionStorage
    const storedQuizData = sessionStorage.getItem('quizData');
    const storedTopic = sessionStorage.getItem('quizTopic');
    
    if (!storedQuizData || !storedTopic) {
      // If no quiz data, redirect to home
      navigate('/');
      return;
    }

    try {
      const parsedData: QuizData = JSON.parse(storedQuizData);
      setQuizData(parsedData);
      setQuizTopic(storedTopic);
      setSelectedAnswers(new Array(parsedData.questions.length).fill(''));
    } catch (error) {
      console.error('Error parsing quiz data:', error);
      navigate('/');
    }
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

  const handleSubmit = () => {
    setShowResults(true);
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
