import openai
import json
import sys
import os
from dotenv import load_dotenv
from e2b_code_interpreter import CodeInterpreter

# Load environment variables
load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

# Configure OpenAI client for Fireworks AI
client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

# System prompt for code review
SYSTEM_PROMPT = """
You are an expert code reviewer specializing in Python. Your task is to analyze the given code for quality issues and potential security vulnerabilities. Provide a detailed review focusing on:

1. Code quality: Identify areas for improvement in terms of readability, maintainability, and efficiency.
2. Security vulnerabilities: Detect potential security issues such as SQL injection, XSS, or other common vulnerabilities.
3. Best practices: Suggest improvements based on Python best practices and common design patterns.
4. Performance: Identify any performance bottlenecks or areas for optimization.

Format your response as a markdown report with sections for each category. Include code snippets and explanations for your suggestions.
"""

def code_review(code):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Please review the following Python code:\n\n```python\n{code}\n```"}
    ]

    response = client.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-405b-instruct",
        messages=messages,
    )

    return response.choices[0].message.content

def main():
    if len(sys.argv) < 2:
        print("Usage: python code_review_tool.py ")
        sys.exit(1)

    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    review_report = code_review(code)
    print(review_report)

if __name__ == "__main__":
    main()