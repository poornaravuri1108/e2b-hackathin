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
    pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
    match = pattern.search(suggestion_text)
    if match:
        return match.group(1)
    return ""

def request_suggested_test_cases(source_code, existing_test_cases):
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
