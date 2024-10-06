import streamlit as st
import matplotlib.pyplot as plt
from code_review_tool import process_code, authenticate, submit_review, get_pending_reviews, vote_on_review, get_approved_reviews, approve_review
from test_case_streamlit import request_suggested_test_cases, run_tests_with_coverage

def initialize_session_state():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state['user'] = user
            st.session_state['role'] = user[3]
            st.success(f"Logged in as {user[1]} ({user[3]})")
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state['user'] = None
    st.session_state['role'] = None

def code_submission_page():
    st.title("Code Submission and Review")

    code_input = st.text_area("Submit your code for review", height=300)

    if st.button("Send Code"):
        with st.spinner("Reviewing code..."):
            review_results = process_code(code_input)
            if review_results:
                review_id = submit_review(st.session_state['user'][0], code_input, review_results)
                st.success(f"Code review submitted successfully. Review ID: {review_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Your Code:")
                    st.code(code_input, language='python')
                    st.subheader("Vulnerabilities:")
                    st.write(review_results['vulnerabilities'])
                    st.subheader("Time Complexity:")
                    st.write(review_results['time_complexity'])
                    st.subheader("Compile Status:")
                    st.write(review_results['compiled_status'])
                
                with col2:
                    st.subheader("Suggested Code:")
                    st.code(review_results['suggested_code'], language='python')
                    st.subheader("Suggested Changes:")
                    st.write(review_results['suggested_vulnerabilities'])
                    st.subheader("Suggested Time Complexity:")
                    st.write(review_results['suggested_time_complexity'])
                    st.subheader("Suggested Code Efficiency:")
                    st.write(review_results['code_efficiency'])
            else:
                st.error("Failed to process the code. Please try again.")

def review_voting_page():
    st.title("Review Voting")

    reviews = get_pending_reviews()

    for review in reviews:
        st.subheader(f"Review by {review[1]}")
        col1, col2 = st.columns(2)
        with col1:
            st.code(review[2], language='python')
            st.write(f"Vulnerabilities: {review[4]}")
            st.write(f"Time Complexity: {review[5]}")
            st.write(f"Compile Status: {review[8]}")
        with col2:
            st.code(review[3], language='python')
            st.write(f"Suggested Changes: {review[6]}")
            st.write(f"Suggested Time Complexity: {review[7]}")
            st.write(f"Code Efficiency: {review[9]}")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Approve", key=f"approve_{review[0]}"):
                vote_on_review(review[0], st.session_state['user'][0], 'approve')
                st.success("Vote recorded")
        with col4:
            if st.button("Disapprove", key=f"disapprove_{review[0]}"):
                vote_on_review(review[0], st.session_state['user'][0], 'disapprove')
                st.success("Vote recorded")

def team_lead_approval_page():
    st.title("Team Lead Approval")

    reviews = get_approved_reviews()

    for review in reviews:
        st.subheader(f"Review by {review[1]}")
        col1, col2 = st.columns(2)
        with col1:
            st.code(review[2], language='python')
            st.write(f"Vulnerabilities: {review[4]}")
            st.write(f"Time Complexity: {review[5]}")
            st.write(f"Compile Status: {review[8]}")
        with col2:
            st.code(review[3], language='python')
            st.write(f"Suggested Changes: {review[6]}")
            st.write(f"Suggested Time Complexity: {review[7]}")
            st.write(f"Code Efficiency: {review[9]}")
        
        if st.button("Approve", key=f"approve_{review[0]}"):
            approve_review(review[0])
            st.success("Review approved")

def test_case_generation_page():
    st.title("Test Case Generation Tool")

    st.write("Upload your Python sample code and existing test cases.")

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

def main():
    st.set_page_config(page_title="Code Review and Test Case System", layout="wide")

    initialize_session_state()

    if st.session_state['user'] is None:
        login()
    else:
        st.sidebar.button("Logout", on_click=logout)

    if st.session_state['user'] is not None:
        functionality = st.selectbox("Select Functionality", ["Code Review", "Test Case Generation"])
        
        if functionality == "Code Review":
            if st.session_state['role'] == 'developer':
                tab1, tab2 = st.tabs(["Submit Code", "Vote on Reviews"])
                with tab1:
                    code_submission_page()
                with tab2:
                    review_voting_page()
            elif st.session_state['role'] == 'team_lead':
                team_lead_approval_page()
        elif functionality == "Test Case Generation":
            test_case_generation_page()
    else:
        st.write("Please log in to access the system.")

if __name__ == "__main__":
    main()