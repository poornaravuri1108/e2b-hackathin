import openai
import json
import sys
import os
import re
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")
# print(f"FIREWORKS_API_KEY {FIREWORKS_API_KEY}")

SYSTEM_PROMPT = """
You are an expert code reviewer specializing in Python. Analyze the given code and provide a response in the following template:

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
    exec = e2b_code_interpreter.notebook.exec_cell(
        modified_code,
        on_stdout=lambda stdout: print("[Code Interpreter]", stdout),
        on_stderr=lambda stderr: print("[Code Interpreter]", stderr),
    )

    return exec

pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
def match_code_block(llm_response):
    match = pattern.search(llm_response)
    if match:
        code = match.group(1)
        return code
    return ""

def classify_compilation(execution_result):
    if execution_result.error:
        return "Not Compiled", f"Error: {execution_result.error}"
    else:
        stdout = execution_result.logs.stdout
        return "Compiled", f"Successfully compiled and executed. Output: {stdout}"

def perform_code_review(code):
    with CodeInterpreter(api_key=E2B_API_KEY) as code_interpreter:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Please review the following Python code:\n\n```python\n{code}\n```"}
        ]

        response = client.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-405b-instruct",
            messages=messages,
        )

        response_message = response.choices[0].message
        review = response_message.content
        refactored_code = match_code_block(response_message.content)

        original_execution = code_interpret(code_interpreter, code)
        refactored_execution = code_interpret(code_interpreter, refactored_code)

        original_compilation_status, original_compilation_message = classify_compilation(original_execution)
        refactored_compilation_status, refactored_compilation_message = classify_compilation(refactored_execution)

        return {
            "review": review,
            "original_execution": {
                "status": original_compilation_status,
                "message": original_compilation_message,
                "stderr": original_execution.logs.stderr,
            },
            "refactored_execution": {
                "status": refactored_compilation_status,
                "message": refactored_compilation_message,
                "stderr": refactored_execution.logs.stderr,
            }
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_python_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    result = perform_code_review(code)

    print("\n=== Code Review ===")
    print(result["review"])

    print("\n=== Original Code Execution ===")
    print("Status:", result["original_execution"]["status"])
    print("Message:", result["original_execution"]["message"])
    print("Stderr:", result["original_execution"]["stderr"])

    print("\n=== Refactored Code Execution ===")
    print("Status:", result["refactored_execution"]["status"])
    print("Message:", result["refactored_execution"]["message"])
    print("Stderr:", result["refactored_execution"]["stderr"])

if __name__ == "__main__":
    main()