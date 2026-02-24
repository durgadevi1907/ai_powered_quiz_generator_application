from utils.llm_groq import gemini_llm

def test_question_generation():
    try:
        # Try to generate one question about a simple topic
        questions = gemini_llm.generate_questions("Python basics", 1)
        print("Successfully generated question:")
        print(questions)
        return True
    except Exception as e:
        print(f"Error generating question: {str(e)}")
        return False

if __name__ == "__main__":
    test_question_generation()