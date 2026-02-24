import React from 'react';
import './Navbar.css';
import { useNavigate } from 'react-router-dom';

interface NavbarProps {
    isAuthenticated: boolean;
    onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ isAuthenticated, onLogout }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('token');
        onLogout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand">QuizMania</div>
            <div className="navbar-links">
                {isAuthenticated ? (
                    <>
                        <button 
                            onClick={() => navigate('/dashboard')} 
                            className={`nav-link ${window.location.pathname === '/dashboard' ? 'active' : ''}`}
                        >
                            Dashboard
                        </button>
                        <button 
                            onClick={() => {
                                // Clear any existing quiz data
                                sessionStorage.removeItem('quizId');
                                sessionStorage.removeItem('quizData');
                                sessionStorage.removeItem('quizTopic');
                                navigate('/quiz-form');  // Navigate to quiz form instead of quiz
                            }} 
                            className={`nav-link ${window.location.pathname === '/quiz' ? 'active' : ''}`}
                        >
                            Quiz
                        </button>
                        <button onClick={handleLogout} className="nav-link logout">
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <button onClick={() => navigate('/login')} className="nav-link">
                            Login
                        </button>
                        <button onClick={() => navigate('/register')} className="nav-link">
                            Register
                        </button>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;