import os
import unittest
import coverage
import openai
import re
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")

client = openai.OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

def extract_python_code(suggestion_text):
    """
    Extract valid Python code from the Fireworks AI response.
    """
    print("Extracting Python code from Fireworks AI suggestion...")
    # Use regex to capture the Python code block
    pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
    match = pattern.search(suggestion_text)
    if match:
        print("Python code extracted successfully.")
        return match.group(1)
    print("Failed to extract Python code.")
    return ""

def request_suggested_test_cases(source_code, existing_test_cases):
    """
    Requests suggested test cases from Fireworks AI for the provided source code and existing test cases.
    """
    print("Requesting suggested test cases from Fireworks AI...")
    messages = [
        {"role": "system", "content": "Suggest additional test cases for the following Python code."},
        {"role": "user", "content": f"Code:\n```python\n{source_code}\n```\n\nExisting Test Cases:\n```python\n{existing_test_cases}\n```"}
    ]
    response = client.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-405b-instruct",
        messages=messages,
    )
    suggestion_text = response.choices[0].message.content
    return extract_python_code(suggestion_text)

def run_tests_with_coverage(source_code, test_cases):
    """
    Runs the provided test cases on the source code with code coverage measurement.
    """
    with open("source_code.py", "w") as f:
        f.write(source_code)

    with open("test_cases.py", "w") as f:
        f.write(test_cases)

    cov = coverage.Coverage(source=["source_code"])
    cov.start()

    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern="test_cases.py")
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    cov.stop()
    cov.save()

    coverage_percent = cov.report()
    return result.wasSuccessful(), coverage_percent

def read_file(file_path):
    """
    Reads the contents of a file.
    """
    with open(file_path, "r") as file:
        return file.read()

def main():
    source_code = read_file("sample_code.py")
    existing_test_cases = read_file("test_cases.py")

    suggested_test_cases = request_suggested_test_cases(source_code, existing_test_cases)
    print("Suggested Test Cases:\n", suggested_test_cases)

    combined_test_cases = existing_test_cases + "\n\n" + suggested_test_cases

    print("\nRunning user-provided and suggested test cases with coverage...\n")
    success, coverage_percent = run_tests_with_coverage(source_code, combined_test_cases)

    print(f"Test Execution Success: {success}")
    print(f"Code Coverage: {coverage_percent}%")

if __name__ == "__main__":
    main()
