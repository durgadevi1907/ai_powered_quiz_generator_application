import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell
} from 'recharts';
import './Dashboard.css';

interface QuizAttempt {
  id: number;
  topic: string;
  date: string;
  score: number;
  totalQuestions: number;
  status: 'completed' | 'incomplete';
}

interface DashboardStats {
  totalQuizzes: number;
  averageScore: number;
  highestScore: number;
  lowestScore: number;
}

const Dashboard: React.FC = (): JSX.Element => {
  const navigate = useNavigate();
  const [recentQuizzes, setRecentQuizzes] = useState<QuizAttempt[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalQuizzes: 0,
    averageScore: 0,
    highestScore: 0,
    lowestScore: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const fetchDashboardData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch('http://localhost:5000/api/dashboard/stats', {
        headers: {
          'Authorization': token
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setRecentQuizzes(data.recentQuizzes);
      setStats(data.stats);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchDashboardData();

    // Set up an interval to refresh data every 30 seconds
    const intervalId = setInterval(fetchDashboardData, 30000);

    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [fetchDashboardData]);

  const resumeQuiz = async (quizId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5000/api/quiz/${quizId}`, {
        headers: {
          'Authorization': token || ''
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quiz data');
      }

      const data = await response.json();
      
      // Verify the data has questions
      if (!data.questions || !Array.isArray(data.questions)) {
        throw new Error('Invalid quiz data received');
      }
      
      // Format the quiz data
      const quizData = {
        questions: data.questions.map((q: any) => ({
          question: q.question,
          options: q.options,
          answer: q.answer
        }))
      };
      
      // Store quiz data in session storage
      sessionStorage.setItem('quizData', JSON.stringify(quizData));
      sessionStorage.setItem('quizTopic', data.topic);
      sessionStorage.setItem('quizId', data.id.toString());
      
      // Navigate to quiz page
      navigate('/quiz');
    } catch (error) {
      console.error('Error resuming quiz:', error);
      setError('Failed to resume quiz. Please try again.');
    }
  };

  const startNewQuiz = () => {
    navigate('/quiz-form');  // Navigate to the quiz form
  };

  if (loading) return <div className="dashboard-loading">Loading dashboard...</div>;
  if (error) return <div className="dashboard-error">{error}</div>;

  return (
    <div className="dashboard-container">
      <h1>Quiz Dashboard</h1>
      
      <div className="dashboard-actions">
        <button onClick={startNewQuiz} className="generate-quiz-btn">
          Generate New Quiz →
        </button>
      </div>

      <div className="dashboard-stats">
        <div className="stat-cards">
          <div className="stat-card">
            <h3>TOTAL QUIZZES</h3>
            <p>{stats.totalQuizzes}</p>
          </div>
          <div className="stat-card">
            <h3>AVERAGE SCORE</h3>
            <p>{stats.averageScore.toFixed(1)}%</p>
          </div>
          <div className="stat-card">
            <h3>HIGHEST SCORE</h3>
            <p>{stats.highestScore}%</p>
          </div>
          <div className="stat-card">
            <h3>LOWEST SCORE</h3>
            <p>{stats.lowestScore}%</p>
          </div>
          <div className="stat-card">
            <h3>INCOMPLETE QUIZZES</h3>
            <p>{recentQuizzes.filter(q => q.status === 'incomplete').length}</p>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart performance-trend">
            <h3>Performance Trend</h3>
            <LineChart width={700} height={300} data={recentQuizzes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#8884d8" />
            </LineChart>
          </div>

          <div className="chart status-distribution">
            <h3>Quiz Status Distribution</h3>
            <PieChart width={300} height={300}>
              <Pie
                data={[
                  { name: 'Completed', value: recentQuizzes.filter(q => q.status === 'completed').length },
                  { name: 'Incomplete', value: recentQuizzes.filter(q => q.status === 'incomplete').length }
                ]}
                cx={150}
                cy={150}
                innerRadius={60}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {recentQuizzes.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </div>
        </div>

        <div className="recent-quizzes">
          <h3>Recent Quiz Attempts (Last 10)</h3>
          <table className="quiz-table">
            <thead>
              <tr>
                <th>TOPIC</th>
                <th>QUESTIONS</th>
                <th>SCORE</th>
                <th>PERCENTAGE</th>
                <th>STATUS</th>
                <th>DATE</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {recentQuizzes.slice(0, 10).map((quiz) => (
                <tr key={quiz.id} className={quiz.status.toLowerCase()}>
                  <td>{quiz.topic}</td>
                  <td>{quiz.totalQuestions}</td>
                  <td>{quiz.score}/{quiz.totalQuestions}</td>
                  <td>{((quiz.score / quiz.totalQuestions) * 100).toFixed(0)}%</td>
                  <td className="status-cell">{quiz.status}</td>
                  <td>{new Date(quiz.date).toLocaleString()}</td>
                  <td>
                    {quiz.status === 'incomplete' && (
                      <button onClick={() => resumeQuiz(quiz.id)} className="resume-btn">
                        Resume
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;