import React from 'react';
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
                        <button onClick={() => navigate('/quiz')} className="nav-link">
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