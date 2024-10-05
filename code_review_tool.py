import openai
import json
import re
import os
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

SYSTEM_PROMPT = """
You are an expert code reviewer specializing in Python. Analyze the given code and provide a response in the following JSON format:

{
  "refactored_code": "<full implementation>",
  "vulnerabilities": "<vulnerabilities detected in original code (one line)>",
  "changes": "<changes made in refactored code (one line)>",
  "time_complexity_original": "<time complexity/efficiency of original code (one line)>",
  "time_complexity_refactored": "<time complexity/efficiency of refactored code (one line)>"
}

Ensure that the "refactored_code" field contains the code as a plain string without any markdown formatting or code blocks.
DO NOT INCLUDE ANY ADDITIONAL TEXT OUTSIDE THE JSON OBJECT.
"""

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

def code_interpret(e2b_code_interpreter, code):
    print("Running code interpreter...")
    # Replace input() with a mock input value
    modified_code = code.replace("input(", "'Vasek_E2B' #")
    # Add database and table initialization
    init_code = """
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    # Insert a mock user
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES ('Vasek_E2B')")
    conn.commit()
    conn.close()

init_db()
"""
    modified_code = init_code + modified_code
    exec_result = e2b_code_interpreter.notebook.exec_cell(
        modified_code,
        on_stdout=lambda stdout: print("[Code Interpreter]", stdout),
        on_stderr=lambda stderr: print("[Code Interpreter]", stderr),
    )

    return exec_result

def extract_json(llm_response):
    try:
        # Try to find JSON-like content
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            print("No JSON-like content found in the response.")
            return None
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return None

def classify_compilation(execution_result):
    if execution_result.error:
        return "Not Compiled", f"Error: {execution_result.error}"
    else:
        stdout = execution_result.logs.stdout
        return "Compiled", f"Successfully compiled and executed. Output: {stdout}"

def review_code(code):
    with CodeInterpreter(api_key=E2B_API_KEY) as code_interpreter:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Please review the following Python code:\n\n```python\n{code}\n```"}
        ]

        response = client.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-405b-instruct",
            messages=messages,
        )

        response_message = response.choices[0].message.content

        # Debugging: Print the language model's response
        print("Language Model Response:\n", response_message)

        response_data = extract_json(response_message)

        if not response_data:
            print("Failed to parse JSON response.")
            return {
                "suggested_code": "",
                "vulnerabilities": "Error in processing",
                "time_complexity": "Error in processing",
                "suggested_vulnerabilities": "Error in processing",
                "suggested_time_complexity": "Error in processing",
                "compiled_status": "Error in processing",
                "code_efficiency": "Error in processing"
            }

        # Extract refactored code
        refactored_code = response_data.get("refactored_code", "")

        vulnerabilities = response_data.get("vulnerabilities", "")
        changes = response_data.get("changes", "")
        time_complexity_original = response_data.get("time_complexity_original", "")
        time_complexity_refactored = response_data.get("time_complexity_refactored", "")

        original_execution = code_interpret(code_interpreter, code)
        refactored_execution = code_interpret(code_interpreter, refactored_code)

        _, original_compilation_message = classify_compilation(original_execution)
        _, refactored_compilation_message = classify_compilation(refactored_execution)

        return {
            "suggested_code": refactored_code,
            "vulnerabilities": vulnerabilities,
            "time_complexity": time_complexity_original,
            "suggested_vulnerabilities": changes,
            "suggested_time_complexity": time_complexity_refactored,
            "compiled_status": original_compilation_message,
            "code_efficiency": refactored_compilation_message
        }

def process_code(code):
    return review_code(code)
