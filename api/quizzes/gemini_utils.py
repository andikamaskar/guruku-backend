import google.generativeai as genai
from django.conf import settings
import json
import typing_extensions as typing

# Re-configure if needed, or rely on settings.GEMINI_API_KEY
genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the schema for the response
class Option(typing.TypedDict):
    text: str

class Question(typing.TypedDict):
    text: str
    options: list[str]
    answer: str
    points: int
    order: int

class QuizAndQuestions(typing.TypedDict):
    questions: list[Question]

def generate_quiz_from_file(file_path: str, mime_type: str, num_questions: int = 5) -> list[Question]:
    """
    Generates quiz questions from a file using Gemini, returning structured JSON.
    """
    try:
        # 1. Upload File
        print(f"Uploading file: {file_path}")
        uploaded_file = genai.upload_file(file_path, mime_type=mime_type)
        print(f"File uploaded: {uploaded_file.uri}")

        # 2. Configure Model
        # 2. Configure Model
        # Optimized for Flash Lite to prevent looping
        generation_config = {
            "temperature": 0.1, # Low temperature for clearer logic
            "response_mime_type": "application/json",
            "max_output_tokens": 8192, # Prevent infinite loops
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config=generation_config
        )

        # 3. Generate Content
        prompt_text = f"""
        You are an educational assistant. 
        TASK: Extract ALL multiple-choice questions from the attached document, up to a maximum of {num_questions}.
        
        RULES:
        1. If the document has existing questions, USE THEM.
        2. If the document has an Answer Key (Kunci Jawaban), USE IT for the 'answer' field.
        3. If no key is found, deduce the correct answer.
        4. Return ONLY a valid JSON List. No markdown formatting, no plain text.
        
        JSON SCHEMA:
        [
          {{
            "text": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Exact string of correct option",
            "points": 10,
            "order": 1
          }}
        ]
        """
        
        prompt = prompt_text
        
        response = model.generate_content([uploaded_file, prompt])
        
        # 4. Parse Response
        try:
            questions_json = json.loads(response.text)
            return questions_json
        except json.JSONDecodeError:
            print("Failed to decode JSON:", response.text)
            return []

    except Exception as e:
        print(f"Error in generate_quiz_from_file: {e}")
        return []
