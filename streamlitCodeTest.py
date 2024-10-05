import streamlit as st
from e2b_interpreter import compile_code
from fireworks_code_review import review_code  
import requests


if 'code' not in st.session_state:
    st.session_state['code'] = ''
if 'suggested_code' not in st.session_state:
    st.session_state['suggested_code'] = ''
if 'compiled_status' not in st.session_state:
    st.session_state['compiled_status'] = ''
if 'vulnerabilities' not in st.session_state:
    st.session_state['vulnerabilities'] = ''
if 'time_complexity' not in st.session_state:
    st.session_state['time_complexity'] = ''
if 'suggested_vulnerabilities' not in st.session_state:
    st.session_state['suggested_vulnerabilities'] = ''
if 'suggested_time_complexity' not in st.session_state:
    st.session_state['suggested_time_complexity'] = ''
if 'code_efficiency' not in st.session_state:
    st.session_state['code_efficiency'] = ''

def code_submission_page():
    st.title("Code Submission")

    code_input = st.text_area("Submit your code for review", height=300, key="code_input")
    
    if st.button("Send Code"):
        st.session_state['code'] = code_input

        review_results = review_code(code_input)  
        st.session_state['suggested_code'] = review_results.get("suggested_code", "")
        st.session_state['vulnerabilities'] = review_results.get("vulnerabilities", "")
        st.session_state['time_complexity'] = review_results.get("time_complexity", "")
        
        st.session_state['compiled_status'] = compile_code(st.session_state['code'])
        
        if st.session_state['suggested_code']:
            st.session_state['suggested_vulnerabilities'] = review_results.get("suggested_vulnerabilities", "")
            st.session_state['suggested_time_complexity'] = review_results.get("suggested_time_complexity", "")
            st.session_state['code_efficiency'] = compile_code(st.session_state['suggested_code'])

    if st.session_state['code']:
        st.subheader("Your Code:")
        st.text_area("Your Code", value=st.session_state['code'], height=150, disabled=True)
        
        st.subheader("Code Vulnerabilities:")
        st.write(st.session_state['vulnerabilities'])
        st.subheader("Time Complexity:")
        st.write(st.session_state['time_complexity'])

        st.subheader("Compile Status:")
        st.write(st.session_state['compiled_status'])

        if st.session_state['suggested_code']:
            st.subheader("Suggested Code:")
            st.text_area("Suggested Code", value=st.session_state['suggested_code'], height=150, disabled=True)

            st.subheader("Suggested Code Vulnerabilities:")
            st.write(st.session_state['suggested_vulnerabilities'])
            st.subheader("Suggested Code Time Complexity:")
            st.write(st.session_state['suggested_time_complexity'])

            st.subheader("Suggested Code Compile Status and Efficiency:")
            st.write(st.session_state['code_efficiency'])

        st.button("Proceed to Test Cases", on_click=test_case_page)


def test_case_page():
    st.title("Submit Test Cases")
    
    test_case_input = st.text_area("Submit your test cases", height=200, key="test_case_input")
    if st.button("Send Test Cases"):
        st.session_state['user_test_cases'] = test_case_input
        test_response = requests.post("https://fireworks_ai_api/check_test_cases", json={"test_cases": test_case_input})
        suggested_test_cases = test_response.json().get("suggested_test_cases", "")
        st.session_state['suggested_test_cases'] = suggested_test_cases

    if st.session_state['user_test_cases']:
        st.subheader("Your Test Cases:")
        st.text_area("Your Test Cases", value=st.session_state['user_test_cases'], height=150, disabled=True)
        st.subheader("Suggested Test Cases:")
        st.text_area("Suggested Test Cases", value=st.session_state['suggested_test_cases'], height=150, disabled=True)

        selected_test_cases = st.radio("Choose the test cases for checking coverage:", ("Your Test Cases", "Suggested Test Cases"))
        if st.button("Check Coverage"):
            test_cases_to_check = st.session_state['user_test_cases'] if selected_test_cases == "Your Test Cases" else st.session_state['suggested_test_cases']
            coverage_response = requests.post("https://e2b_code_interpreter/check_coverage", json={"test_cases": test_cases_to_check})
            coverage_report = coverage_response.json().get("coverage_report", "")
            st.session_state['coverage_report'] = coverage_report
            if st.session_state['coverage_report']:
                st.write(f"Test Case Coverage: {st.session_state['coverage_report']}")
                st.download_button("Download Coverage Report", data=st.session_state['coverage_report'], file_name="coverage_report.txt")

page = st.sidebar.selectbox("Choose Page", ["Code Submission", "Test Case Submission"])

if page == "Code Submission":
    code_submission_page()
elif page == "Test Case Submission":
    test_case_page()
