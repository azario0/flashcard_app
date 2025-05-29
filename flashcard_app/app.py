import os
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_dev')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# --- Helper Functions (adapted from notebook) ---

def extract_text_from_pdf_stream(pdf_stream):
    """Extracts text from a PDF file stream."""
    text = ""
    try:
        pdf_bytes = pdf_stream.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None, f"Error extracting text from PDF: {e}"
    return text, None

def generate_flashcards_gemini_flash(
    api_key: str,
    text_input: str,
    max_flashcards: int = 15, # Default to 15 as in example output
    temperature: float = 0.3,
    count_tokens_before_sending: bool = True
) -> tuple[list[dict], str | None]:
    """
    Generates flashcard (question-answer) pairs from the given text using Gemini 1.5 Flash.
    Returns a tuple: (list_of_flashcards, error_message_or_None).
    """
    if not api_key:
        return [], "Error: API key must be provided."
    if not text_input or not text_input.strip():
        return [], "Warning: Input text for flashcard generation is empty."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash-latest',
        generation_config=genai.types.GenerationConfig(temperature=temperature),
    )

    prompt = f"""
    You are an expert flashcard creator. Your task is to analyze the following text and generate concise question-answer pairs suitable for flashcards.
    The questions should test understanding of key concepts, facts, definitions, or important relationships mentioned in the text.
    The answers should be directly derivable from the text and be as brief as possible while still being accurate and complete.
    Aim to generate up to {max_flashcards} flashcard pairs.

    Format your output STRICTLY as a JSON list of objects. Each object must have a "question" key and an "answer" key.
    Do NOT include any introductory text, explanations, or markdown formatting like ```json ... ``` outside of the JSON structure itself.
    Just return the raw JSON list.

    Example of expected JSON output format:
    [
        {{"question": "What is the primary function of mitochondria?", "answer": "To generate most of the cell's supply of adenosine triphosphate (ATP), used as a source of chemical energy."}},
        {{"question": "Who developed the theory of relativity?", "answer": "Albert Einstein."}}
    ]

    Here is the text to process:
    ---
    {text_input}
    ---

    Generate the flashcards now:
    """

    if count_tokens_before_sending:
        try:
            token_count_response = model.count_tokens(prompt)
            print(f"Estimated token count for the prompt: {token_count_response.total_tokens}")
            # The notebook used a limit of 10000, let's respect that for now.
            # Gemini 1.5 Flash has a much larger context window (1M tokens).
            # This custom limit might be for cost/performance reasons by the original author.
            if token_count_response.total_tokens >= 10000:
                return [], f"Error: The document is too long. Prompt tokens: {token_count_response.total_tokens}. Processing limit: 10,000 tokens."
        except Exception as e:
            print(f"Could not count tokens: {e}. Proceeding with generation attempt.")
            # Optionally, you could return an error here:
            # return [], f"Error: Could not count tokens before sending: {e}"

    try:
        print("Sending request to Gemini API for generation...")
        response = model.generate_content(prompt)

        if not response.parts:
            error_msg = "Warning: Gemini API returned no parts in the response."
            if response.prompt_feedback:
                error_msg += f" Prompt feedback: {response.prompt_feedback}"
            print(error_msg)
            return [], error_msg

        raw_json_text = response.text
        # Try to extract JSON from markdown code blocks if present
        match = re.search(r"```(json)?\s*([\s\S]*?)\s*```", raw_json_text, re.IGNORECASE)
        if match:
            cleaned_json_text = match.group(2)
        else:
            cleaned_json_text = raw_json_text.strip()
        
        # Further attempt to find a list if the cleaning wasn't perfect
        if cleaned_json_text and not (cleaned_json_text.startswith('[') and cleaned_json_text.endswith(']')):
            list_match = re.search(r"(\[[^\]]*\])", cleaned_json_text) # Simple regex for a list
            if list_match:
                cleaned_json_text = list_match.group(1)
            else: # If still not a list, assume it's malformed
                print(f"Warning: Gemini API response does not appear to be a valid JSON list. Raw: {raw_json_text}")
                # return [], "Error: Could not extract a valid JSON list from the API response."
                # Try parsing anyway, might work if it's just missing ```
                pass


        flashcards = json.loads(cleaned_json_text)

        if not isinstance(flashcards, list):
            return [], f"Error: Parsed JSON is not a list. Got: {type(flashcards)}"
        
        valid_flashcards = []
        for item in flashcards:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                valid_flashcards.append(item)
            else:
                print(f"Warning: Invalid flashcard item format skipped: {item}")
        
        if not valid_flashcards:
             return [], "Warning: No valid flashcards were generated or parsed from the model's response."

        print(f"Successfully generated {len(valid_flashcards)} flashcards.")
        return valid_flashcards, None

    except json.JSONDecodeError as e:
        raw_resp_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'No response text available'
        print(f"Error: Could not decode JSON from Gemini response: {e}")
        print(f"Raw response from Gemini:\n---\n{raw_resp_text}\n---")
        return [], f"Error: Could not decode JSON from Gemini response. Details: {e}"
    except Exception as e:
        err_msg = f"An unexpected error occurred during flashcard generation: {e}"
        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
            err_msg += f" Prompt feedback: {response.prompt_feedback}"
        print(err_msg)
        return [], err_msg

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if not GEMINI_API_KEY:
        flash("Error: GEMINI_API_KEY is not configured on the server.", "danger")
        # You might want to render a specific error page or disable functionality
    
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No PDF file part in the request.', 'warning')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No PDF file selected.', 'warning')
            return redirect(request.url)

        if file and file.filename.endswith('.pdf'):
            if not GEMINI_API_KEY:
                flash("Cannot process PDF: GEMINI_API_KEY is not set.", "danger")
                return redirect(request.url)

            pdf_text, err = extract_text_from_pdf_stream(file.stream)
            if err:
                flash(err, 'danger')
                return redirect(request.url)
            if not pdf_text:
                 flash('Could not extract any text from the PDF.', 'warning')
                 return redirect(request.url)

            flash('PDF text extracted. Generating flashcards...', 'info')
            # Using max_flashcards=15 as per notebook's example output count
            flashcards, error_msg = generate_flashcards_gemini_flash(GEMINI_API_KEY, pdf_text, max_flashcards=4)

            if error_msg:
                flash(error_msg, 'danger')
                return redirect(request.url) # Or render index with error
            
            if not flashcards:
                flash('No flashcards could be generated from this PDF.', 'warning')
                return redirect(request.url)

            session['flashcards'] = flashcards
            session['current_q_index'] = 0
            session['user_answers'] = []
            flash(f'{len(flashcards)} flashcards generated successfully!', 'success')
            return redirect(url_for('quiz'))
        else:
            flash('Invalid file type. Please upload a PDF.', 'warning')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'flashcards' not in session or not session['flashcards']:
        flash('No flashcards available. Please upload a PDF first.', 'info')
        return redirect(url_for('index'))

    flashcards = session['flashcards']
    current_q_index = session.get('current_q_index', 0)

    if request.method == 'POST':
        user_answer = request.form.get('answer', '')
        user_answers = session.get('user_answers', [])
        user_answers.append(user_answer)
        session['user_answers'] = user_answers
        current_q_index += 1
        session['current_q_index'] = current_q_index
        # No flash message here, just proceed to next question or results

    if current_q_index >= len(flashcards):
        return redirect(url_for('results'))

    current_flashcard = flashcards[current_q_index]
    return render_template('quiz.html', 
                           question=current_flashcard['question'],
                           q_num=current_q_index + 1,
                           total_qs=len(flashcards))

@app.route('/results')
def results():
    if 'flashcards' not in session or 'user_answers' not in session:
        flash('Quiz data not found. Please start a new quiz.', 'info')
        return redirect(url_for('index'))

    flashcards = session['flashcards']
    user_answers = session['user_answers']
    
    if len(user_answers) != len(flashcards):
        flash('Mismatch in answers and questions. Please restart.', 'warning')
        # Potentially clear session here or handle more gracefully
        return redirect(url_for('restart'))

    score = 0
    detailed_results = []

    for i, card in enumerate(flashcards):
        correct_answer_norm = card['answer'].strip().lower()
        user_answer_norm = user_answers[i].strip().lower()
        is_correct = (correct_answer_norm == user_answer_norm)
        if is_correct:
            score += 1
        detailed_results.append({
            'question': card['question'],
            'correct_answer': card['answer'],
            'user_answer': user_answers[i],
            'is_correct': is_correct
        })
    
    # Clear specific session data after results are calculated
    # session.pop('flashcards', None)
    # session.pop('current_q_index', None)
    # session.pop('user_answers', None)
    # Decided to keep session data until 'restart' for now, allows refresh of results page.

    return render_template('results.html',
                           score=score,
                           total_qs=len(flashcards),
                           results=detailed_results)

@app.route('/restart')
def restart():
    session.pop('flashcards', None)
    session.pop('current_q_index', None)
    session.pop('user_answers', None)
    flash('Quiz reset. You can upload a new PDF.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY environment variable is not set. The application might not function correctly.")
    app.run(debug=True)