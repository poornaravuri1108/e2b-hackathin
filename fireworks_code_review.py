import requests

def review_code(code):
    """
    This function sends the provided code to Fireworks AI for review.
    It returns a dictionary containing the suggested code, vulnerabilities, time complexity, etc.
    """
    try:
        # Make the POST request to Fireworks AI for code review
        review_response = requests.post("https://fireworks_ai_api/submit_code", json={"code": code})
        
        if review_response.status_code == 200:
            # Parse the response for the necessary data
            data = review_response.json()
            return {
                "suggested_code": data.get("suggested_code", ""),
                "vulnerabilities": data.get("vulnerabilities", ""),
                "time_complexity": data.get("time_complexity", ""),
                "suggested_vulnerabilities": data.get("suggested_vulnerabilities", ""),
                "suggested_time_complexity": data.get("suggested_time_complexity", "")
            }
        else:
            return {
                "suggested_code": "",
                "vulnerabilities": "Error fetching vulnerabilities.",
                "time_complexity": "Error fetching time complexity.",
                "suggested_vulnerabilities": "",
                "suggested_time_complexity": ""
            }
    except Exception as e:
        return {
            "suggested_code": "",
            "vulnerabilities": f"Error occurred: {str(e)}",
            "time_complexity": f"Error occurred: {str(e)}",
            "suggested_vulnerabilities": "",
            "suggested_time_complexity": ""
        }
