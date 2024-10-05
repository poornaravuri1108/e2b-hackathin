import requests

def compile_code(code):
    """
    This function sends the provided code to e2b code interpreter for compilation.
    It returns the compilation status.
    """
    try:
        # Make the POST request to the e2b interpreter API
        compile_response = requests.post("https://e2b_code_interpreter/compile", json={"code": code})
        if compile_response.status_code == 200:
            # Parse the response for status and efficiency information
            compile_status = compile_response.json().get("status", "Compilation failed.")
            efficiency = compile_response.json().get("efficiency", "")
            return f"Status: {compile_status}, Efficiency: {efficiency}"
        else:
            return f"Error: {compile_response.text}"
    except Exception as e:
        return f"Error occurred during compilation: {str(e)}"
