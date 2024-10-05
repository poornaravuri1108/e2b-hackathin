import openai
import json
import os
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

SYSTEM_PROMPT = """
You are an expert code reviewer specializing in Python. Analyze the given code and provide a response in the following format:

1. Refactored code (full implementation)
2. Vulnerabilities detected in original code (one line)
3. Changes made in refactored code (one line)
4. Time complexity/efficiency of original code (one line)
5. Time complexity/efficiency of refactored code (one line)

ALWAYS FORMAT YOUR RESPONSE IN MARKDOWN
ALWAYS INCLUDE THE REFACTORED CODE IN A PYTHON CODE BLOCK
ENSURE THE REFACTORED CODE INCLUDES DATABASE AND TABLE INITIALIZATION
"""

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

def code_interpret(e2b_code_interpreter, code):
    print("Running code interpreter...")
    # Replace input() with a mock input value
    modified_code = code.replace("input(", "'mock_user' #")
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
    exec = e2b_code_interpreter.notebook.exec_cell(
        modified_code,
        on_stdout=lambda stdout: print("[Code Interpreter]", stdout),
        on_stderr=lambda stderr: print("[Code Interpreter]", stderr),
    )

    return exec

def match_code_block(llm_response):
    import re
    pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
    match = pattern.search(llm_response)
    if match:
        return match.group(1)
    return ""

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
        refactored_code = match_code_block(response_message)

        # Extract information from the review
        lines = response_message.split('\n')
        vulnerabilities = ""
        changes = ""
        time_complexity_original = ""
        time_complexity_refactored = ""

        for line in lines:
            if line.startswith('2.'):
                vulnerabilities = line.replace('2.', '').strip()
            elif line.startswith('3.'):
                changes = line.replace('3.', '').strip()
            elif line.startswith('4.'):
                time_complexity_original = line.replace('4.', '').strip()
            elif line.startswith('5.'):
                time_complexity_refactored = line.replace('5.', '').strip()

        original_execution = code_interpret(code_interpreter, code)
        refactored_execution = code_interpret(code_interpreter, refactored_code)

        original_compilation_status, original_compilation_message = classify_compilation(original_execution)
        refactored_compilation_status, refactored_compilation_message = classify_compilation(refactored_execution)

        return {
            "suggested_code": refactored_code,
            "vulnerabilities": vulnerabilities,
            "time_complexity": time_complexity_original,
            "suggested_vulnerabilities": changes,
            "suggested_time_complexity": time_complexity_refactored,
            "compiled_status": f"{original_compilation_status}: {original_compilation_message}",
            "code_efficiency": f"{refactored_compilation_status}: {refactored_compilation_message}"
        }

def process_code(code):
    return review_code(code)