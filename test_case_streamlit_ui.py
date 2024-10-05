import streamlit as st
import matplotlib.pyplot as plt
from test_case_streamlit import request_suggested_test_cases, run_tests_with_coverage

st.title("Test Case Generation Tool")

st.write("Upload your Python sample code and existing test cases. Fireworks AI will suggest additional test cases, and we'll calculate code coverage for both.")

source_code_input = st.text_area("Sample Code", height=200, placeholder="Paste your Python sample code here...")
test_cases_input = st.text_area("Test Cases", height=200, placeholder="Paste your test cases here...")

if st.button("Generate Suggested Test Cases and Run"):
    if source_code_input and test_cases_input:
        with st.spinner("Requesting suggested test cases from Fireworks AI..."):
            suggested_test_cases = request_suggested_test_cases(source_code_input, test_cases_input)

        st.write("### User-provided Test Cases")
        st.code(test_cases_input, language="python")

        st.write("### Fireworks AI Suggested Test Cases")
        if suggested_test_cases:
            st.code(suggested_test_cases, language="python")
        else:
            st.write("No suggested test cases were generated.")

        combined_test_cases = test_cases_input + "\n\n" + suggested_test_cases
        success, coverage_percent = run_tests_with_coverage(source_code_input, combined_test_cases)

        st.write("### Test Execution Results")
        st.write(f"Test Execution Success: {'Yes' if success else 'No'}")
        st.write(f"Code Coverage: {coverage_percent:.2f}%")

        st.write("### Code Coverage Pie Chart")
        covered = coverage_percent
        not_covered = 100 - coverage_percent

        fig, ax = plt.subplots()
        ax.pie([covered, not_covered], labels=['Covered', 'Not Covered'], autopct='%1.1f%%', colors=['#4CAF50', '#F44336'], startangle=90)
        ax.axis('equal')  
        st.pyplot(fig)

    else:
        st.error("Please enter both the sample code and test cases.")
