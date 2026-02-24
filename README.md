# Quizomania - Quiz Generation Platform

A full-stack quiz generation application that uses Google's Gemini AI to dynamically generate multiple-choice questions on any topic.

## Project Structure

```
quizomania/
├── backend/               # Flask Python backend
│   ├── app.py            # Main Flask application
│   ├── config.py         # Configuration settings
│   ├── run_server.py     # Server entry point
│   ├── requirements.txt   # Python dependencies
│   ├── .env              # Environment variables (API keys)
│   ├── controllers/      # Business logic controllers
│   │   ├── auth_controller.py
│   │   └── question_controller.py
│   ├── routes/           # API endpoints
│   │   ├── auth_routes.py
│   │   ├── question_routes.py
│   │   ├── quiz_routes.py
│   │   ├── dashboard_routes.py
│   │   └── debug_routes.py
│   ├── models/           # Database models
│   │   ├── auth_models.py
│   │   └── question_models.py
│   ├── database/         # Database setup
│   │   └── db.py
│   └── utils/            # Utility functions
│       └── llm_gemini.py # Gemini AI integration
│
└── frontend/             # React TypeScript frontend
    ├── package.json
    ├── tsconfig.json
    ├── public/
    ├── src/
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── components/
    │       ├── QuizForm.tsx
    │       ├── QuizPage.tsx
    │       ├── auth/
    │       │   ├── Login.tsx
    │       │   └── Register.tsx
    │       ├── dashboard/
    │       │   └── Dashboard.tsx
    │       └── navbar/
    │           └── Navbar.tsx
    └── build/            # Production build
```

## Features

- **AI-Powered Question Generation** - Uses Google Gemini API to generate contextually relevant multiple-choice questions
- **User Authentication** - Register and login functionality
- **Quiz Dashboard** - View quiz history and statistics
- **Dynamic Topics** - Generate quizzes on any topic
- **Multiple Choice Format** - 4 option multiple-choice questions with validation

## Prerequisites

- **Python 3.8+**
- **Node.js 14+** and npm
- **Google Gemini API Key** - Get it from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **SQLite** or configured database

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create or update `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   FLASK_ENV=development
   ```

4. **Run the backend server:**
   ```bash
   python app.py
   # or
   python run_server.py
   ```
   Server runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   # or set port explicitly
   set PORT=3001 && npm start  # Windows
   export PORT=3001 && npm start  # Linux/Mac
   ```
   Frontend runs on `http://localhost:3001`

## API Endpoints

### Question Generation
- **POST** `/api/questions/generate` - Generate quiz questions
  ```json
  {
    "topic": "python",
    "number_questions": 5
  }
  ```

### Authentication
- **POST** `/api/auth/register` - User registration
- **POST** `/api/auth/login` - User login

### Dashboard
- **GET** `/api/dashboard` - Get user dashboard data

### Quiz Management
- **GET** `/api/quiz` - Get all quizzes
- **POST** `/api/quiz` - Create new quiz

## Gemini Model Configuration

The project uses **gemini-2.0-flash** model on the stable v1 API endpoint.

**Model location:** [backend/utils/llm_gemini.py](backend/utils/llm_gemini.py)

### Current Configuration
- **Model:** `gemini-2.0-flash`
- **API Version:** `v1` (stable)
- **Endpoint:** `https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent`

### Rate Limiting & Quotas
The free tier has limited requests. If you encounter 429 (Too Many Requests) errors:

1. **Add Billing to Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Add a credit card to enable paid access
   - This significantly increases rate limits

2. **Wait for quota reset** - Free tier quotas reset daily

3. **Use different API key** - Create a new project with a new API key

## Troubleshooting

### 429 Rate Limit Error
```
Error: 429 Client Error: Too Many Requests
```
**Solution:** Add billing to your Google Cloud project or use a different API key with available quota.

### API Key Not Found
```
Error: Neither GOOGLE_API_KEY nor GEMINI_API_KEY found
```
**Solution:** Ensure `.env` file contains `GOOGLE_API_KEY=your_key_here`

### Port Already in Use
```
Error: Address already in use
```
**Solution:** Kill the process or use a different port:
```bash
# Frontend on different port
set PORT=3002 && npm start

# Backend on different port
python app.py  # Configure in config.py
```

### Python Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Install requirements:
```bash
pip install -r requirements.txt
```

## Development

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Build for Production
```bash
# Frontend build
cd frontend
npm run build

# Output in frontend/build/
```

## Dependencies

### Backend (Python)
- Flask - Web framework
- Flask-CORS - CORS handling
- python-dotenv - Environment variables
- google-generativeai - Gemini API
- requests - HTTP client
- pydantic - Data validation
- langchain-google-genai - LangChain integration

### Frontend (TypeScript/React)
- React 18
- TypeScript
- Axios - HTTP client
- React Router - Routing

## Environment Variables

### `.env` file (Backend)
```env
GOOGLE_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Infosys Project - 2025

## Support

For issues with:
- **Gemini API:** Check [Google AI Documentation](https://ai.google.dev/)
- **Flask:** Check [Flask Documentation](https://flask.palletsprojects.com/)
- **React:** Check [React Documentation](https://react.dev/)

## Notes

- The backend uses Flask with SQLite by default
- Frontend is built with React and TypeScript
- API communication uses REST endpoints
- Gemini API is used for AI-powered question generation
- Rate limits apply to free tier - upgrade for production use
