import streamlit as st
from code_review_tool import process_code

def initialize_session_state():
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

    code_input = st.text_area("Submit your code for review", height=300)

    if st.button("Send Code"):
        st.session_state['code'] = code_input

        with st.spinner("Reviewing code..."):
            review_results = process_code(code_input)
            if not review_results:
                st.error("Failed to process the code. Please try again.")
                return
            st.session_state['suggested_code'] = review_results.get("suggested_code", "")
            st.session_state['vulnerabilities'] = review_results.get("vulnerabilities", "")
            st.session_state['time_complexity'] = review_results.get("time_complexity", "")
            st.session_state['suggested_vulnerabilities'] = review_results.get("suggested_vulnerabilities", "")
            st.session_state['suggested_time_complexity'] = review_results.get("suggested_time_complexity", "")
            st.session_state['compiled_status'] = review_results.get("compiled_status", "")
            st.session_state['code_efficiency'] = review_results.get("code_efficiency", "")

    if st.session_state['code']:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Your Code:")
            st.code(st.session_state['code'], language='python')
            
            st.subheader("Code Vulnerabilities:")
            if st.session_state['vulnerabilities']:
                st.write(st.session_state['vulnerabilities'])
            else:
                st.write("No vulnerabilities detected.")

            st.subheader("Time Complexity:")
            if st.session_state['time_complexity']:
                st.write(st.session_state['time_complexity'])
            else:
                st.write("No time complexity information available.")

            st.subheader("Compile Status:")
            if st.session_state['compiled_status']:
                st.write(st.session_state['compiled_status'])
            else:
                st.write("No compilation status available.")

        with col2:
            if st.session_state.get('suggested_code'):
                st.subheader("Suggested Code:")
                st.code(st.session_state['suggested_code'], language='python')

                st.subheader("Suggested Code Changes:")
                if st.session_state['suggested_vulnerabilities']:
                    st.write(st.session_state['suggested_vulnerabilities'])
                else:
                    st.write("No changes suggested.")

                st.subheader("Suggested Code Time Complexity:")
                if st.session_state['suggested_time_complexity']:
                    st.write(st.session_state['suggested_time_complexity'])
                else:
                    st.write("No time complexity information available for the refactored code.")

                st.subheader("Suggested Code Compile Status and Efficiency:")
                if st.session_state['code_efficiency']:
                    st.write(st.session_state['code_efficiency'])
                else:
                    st.write("No compilation or efficiency information available for the refactored code.")

def main():
    initialize_session_state()
    code_submission_page()

if __name__ == "__main__":
    main()