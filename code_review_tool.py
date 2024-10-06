import openai
import json
import re
import os
import sqlite3
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

# Use a consistent database name throughout the code
DB_NAME = 'code_review.db'

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

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS code_reviews
                 (id INTEGER PRIMARY KEY, user_id INTEGER, code TEXT, suggested_code TEXT,
                  vulnerabilities TEXT, time_complexity TEXT, suggested_vulnerabilities TEXT,
                  suggested_time_complexity TEXT, compiled_status TEXT, code_efficiency TEXT,
                  status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS review_votes
                 (id INTEGER PRIMARY KEY, review_id INTEGER, user_id INTEGER, vote TEXT)''')
    conn.commit()
    conn.close()

def code_interpret(e2b_code_interpreter, code):
    print("Running code interpreter...")
    modified_code = code.replace("input(", "'mock_input' #")
    test_db_name = DB_NAME  # Use the same database name
    init_code = f"""
import sqlite3

def init_test_db():
    conn = sqlite3.connect('{test_db_name}')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL)')
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES ('test_user')")
    conn.commit()
    return conn

conn = init_test_db()
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

def add_user(username, password, role):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
              (username, password, role))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def submit_review(user_id, code, review_results):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO code_reviews 
    (user_id, code, suggested_code, vulnerabilities, time_complexity, 
    suggested_vulnerabilities, suggested_time_complexity, compiled_status, 
    code_efficiency, status) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, code, review_results['suggested_code'], 
          review_results['vulnerabilities'], review_results['time_complexity'],
          review_results['suggested_vulnerabilities'], 
          review_results['suggested_time_complexity'],
          review_results['compiled_status'], review_results['code_efficiency'],
          'Pending'))
    review_id = c.lastrowid
    conn.commit()
    conn.close()
    return review_id

def get_pending_reviews():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    SELECT cr.id, u.username, cr.code, cr.suggested_code, cr.vulnerabilities, 
           cr.time_complexity, cr.suggested_vulnerabilities, cr.suggested_time_complexity, 
           cr.compiled_status, cr.code_efficiency
    FROM code_reviews cr
    JOIN users u ON cr.user_id = u.id
    WHERE cr.status = 'Pending'
    """)
    reviews = c.fetchall()
    conn.close()
    return reviews

def vote_on_review(review_id, user_id, vote):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO review_votes (review_id, user_id, vote) VALUES (?, ?, ?)",
              (review_id, user_id, vote))
    conn.commit()

    c.execute("SELECT vote, COUNT(*) FROM review_votes WHERE review_id = ? GROUP BY vote", (review_id,))
    votes = dict(c.fetchall())
    
    if votes.get('disapprove', 0) > 1:
        c.execute("UPDATE code_reviews SET status = 'Rejected' WHERE id = ?", (review_id,))
    elif votes.get('approve', 0) >= 2:
        c.execute("UPDATE code_reviews SET status = 'Approved' WHERE id = ?", (review_id,))
    
    conn.commit()
    conn.close()

def get_approved_reviews():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    SELECT cr.id, u.username, cr.code, cr.suggested_code, cr.vulnerabilities, 
           cr.time_complexity, cr.suggested_vulnerabilities, cr.suggested_time_complexity, 
           cr.compiled_status, cr.code_efficiency
    FROM code_reviews cr
    JOIN users u ON cr.user_id = u.id
    WHERE cr.status = 'Approved'
    """)
    reviews = c.fetchall()
    conn.close()
    return reviews

def approve_review(review_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE code_reviews SET status = 'Final Approval' WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

# Initialize the database
init_db()

# Add test users if they don't exist
if not get_user('developer1'):
    add_user('developer1', 'password1', 'developer')
if not get_user('developer2'):
    add_user('developer2', 'password2', 'developer')
if not get_user('teamlead'):
    add_user('teamlead', 'password3', 'team_lead')

# Test function to ensure database is working
def test_db():
    user = get_user('developer1')
    if user:
        print(f"Test user found: {dict(user)}")
    else:
        print("Test user not found. Database might not be initialized correctly.")

def main():
    # Ensure the database is initialized before running main
    init_db()
    test_db()
    
    user_input = 'developer1'  # Simulating input in the code interpreter environment
    user = get_user(user_input)
    if user:
        print(f"User found: {dict(user)}")
    else:
        print("User not found")

if __name__ == "__main__":
    main()

# Sample code to be interpreted
sample_code = """
import sqlite3

def get_user(username):
    conn = sqlite3.connect('code_review.db')  # Use the consistent database name
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

def main():
    user_input = input("Enter username: ")
    user = get_user(user_input)
    if user:
        print(f"User found: {user}")
    else:
        print("User not found")

if __name__ == "__main__":
    main()
"""