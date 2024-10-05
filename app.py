import streamlit as st
from code_review_tool import process_code

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
    st.title("Code Submission and Review")

    code_input = st.text_area("Submit your code for review", height=300, key="code_input")
    
    if st.button("Send Code"):
        st.session_state['code'] = code_input

        with st.spinner("Reviewing code..."):
            review_results = process_code(code_input)
            st.session_state['suggested_code'] = review_results.get("suggested_code", "")
            st.session_state['vulnerabilities'] = review_results.get("vulnerabilities", "")
            st.session_state['time_complexity'] = review_results.get("time_complexity", "")
            st.session_state['suggested_vulnerabilities'] = review_results.get("suggested_vulnerabilities", "")
            st.session_state['suggested_time_complexity'] = review_results.get("suggested_time_complexity", "")
            st.session_state['compiled_status'] = review_results.get("compiled_status", "")
            st.session_state['code_efficiency'] = review_results.get("code_efficiency", "")

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

            st.subheader("Suggested Code Changes:")
            st.write(st.session_state['suggested_vulnerabilities'])
            st.subheader("Suggested Code Time Complexity:")
            st.write(st.session_state['suggested_time_complexity'])

            st.subheader("Suggested Code Compile Status and Efficiency:")
            st.write(st.session_state['code_efficiency'])

def main():
    code_submission_page()

if __name__ == "__main__":
    main()