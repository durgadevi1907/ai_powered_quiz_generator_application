"""
Backwards Compatibility Module
This module maintains backwards compatibility with code using the old llm_gemini imports.
All functionality has been migrated to llm_groq.py
"""

from .llm_groq import (
    GroqAIService,
    GeminiClient,
    AIService,
    get_groq_service,
    get_gemini_llm,
    groq_llm,
    gemini_llm,
    generate_questions,
    QuizQuestion,
    QuizQuestionSet
)

__all__ = [
    'GroqAIService',
    'GeminiClient',
    'AIService',
    'get_groq_service',
    'get_gemini_llm',
    'groq_llm',
    'gemini_llm',
    'generate_questions',
    'QuizQuestion',
    'QuizQuestionSet'
]
