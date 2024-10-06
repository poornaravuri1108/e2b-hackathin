# E2B Code Interpreter Hackathon

# 🚀 AI-Powered Code Review Tool

This repository contains an **AI-driven code review tool** that empowers developers to write **better code, faster**. Built using the **Fireworks AI** model and the **E2B Code Interpreter**, this tool integrates seamlessly with your development workflow, automatically reviewing code, suggesting improvements, and generating test cases—all with the power of AI. Say goodbye to code vulnerabilities and hello to a more efficient development process! 💻✨

## 🌟 Key Features

1. **Smart Code Review with AI**: Automatically refactor your code for better performance and security while detecting vulnerabilities.
2. **Test Case Generation & Coverage**: Run existing test cases, get AI-suggested tests, and analyze code coverage with visual reports.
3. **Collaborative Code Review**: Share code reviews with your team. When two developers approve, the review goes to the team lead for final approval and merge.
4. **Seamless Team Workflow**: Manage the entire code review process, from submission to approval, in one place.

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/code-review-tool.git
cd code-review-tool
```

### 2. Set Up Your Environment

- **Create a virtual environment** (recommended):
  
  ```bash
  python -m venv venv
  source venv/bin/activate  # On macOS/Linux
  .\venv\Scripts\activate   # On Windows
  ```

- **Install dependencies**:

  ```bash
  pip install -r requirements.txt
  ```

- **Create your `.env` file**:

  Add your Fireworks AI and E2B API keys in a `.env` file:

  ```bash
  FIREWORKS_API_KEY=your_fireworks_api_key
  E2B_API_KEY=your_e2b_api_key
  ```

### 3. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your browser, where you can log in as a developer or team lead to begin using the tool.

---

## 🔧 Core Functionality

### Code Submission & AI Review
Submit your code to be compiled and analyzed by AI. The AI suggests refactored code to eliminate vulnerabilities, improve time complexity, and enhance overall code efficiency.

### Review Voting
Developers can vote on pending reviews. Once two developers approve a review, it is forwarded to the team lead for final approval.

### Team Lead Approval
Team leads get a streamlined view of approved reviews for final validation and can merge them into the main repository.

### Test Case Generation & Coverage Analysis
Upload your code and existing test cases, and let the AI generate additional test cases. You’ll also get a detailed code coverage analysis, displayed with a pie chart for easy understanding.

---

## 🧠 Under the Hood

Our tool integrates **Fireworks AI** and the **E2B Code Interpreter SDK** to provide real-time code interpretation, vulnerability detection, and test case generation. Here's how it works:

1. **Code Interpretation**: Fireworks AI analyzes the submitted code, providing JSON-formatted feedback with refactored code, vulnerability reports, and time complexity analysis.
2. **Execution Environment**: Code execution and analysis occur within the E2B sandbox, ensuring a safe and isolated environment for running and testing the code.
3. **Database Backend**: SQLite is used to store user data, code reviews, and approval statuses, allowing the tool to track and manage reviews throughout the team workflow.

---

## 🛠️ Setup Details

- **Streamlit for UI**: A modern and intuitive interface built with Streamlit for an effortless user experience.
- **SQLite for Storage**: All user data and review information is stored in a local SQLite database for easy management.
- **Fireworks AI & E2B**: Core AI capabilities are powered by the Fireworks API, while E2B provides the execution environment for running tests and analyzing code.

---

## ⚙️ System Requirements

- **Python 3.8+**
- **Fireworks AI API Access**
- **E2B Code Interpreter Access**

---

## 📊 Visualization

Our tool offers detailed visualizations for test coverage. Below is an example of a coverage pie chart generated after running test cases:

![Test Coverage](https://via.placeholder.com/400x300)

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## 🤝 Contributing

Want to improve the tool? Contributions are welcome! Feel free to fork the repo, make your changes, and submit a pull request.

---

## 👥 Team & Support

For any questions or support, feel free to reach out to us at [kaushikq.ravindran@sjsu.edu](mailto:kaushikq.ravindran@sjsu.edu).

---

_Develop smarter, ship faster, and review with confidence!_ 🧑‍💻

Sample Images of code reviewing:
![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/9eb644f4-7aa0-4f81-bd5d-8607f1339d76/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/da0c03cc-80fd-411f-827f-f1dc2561c7c0/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/ba7c98fa-4fa7-4720-978a-695e2c7bf064/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/071904d4-30dc-4ece-8418-b6755d9ad723/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/4b8120d0-3976-44be-b5c8-cbacf48d474b/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/e5e11734-a919-4320-af6d-5bf71a51f555/57338705-fa7b-4b2d-a537-d4b5bd65d7d1/image.png)

