import os
import json
import google.generativeai as genai

class Planner:
    """
    The Planner is responsible for creating a step-by-step plan to fulfill a user request.
    It uses the Gemini Pro LLM to break down the request into a structured list of actions.
    """
    def __init__(self):
        # --- GEMINI API CONFIGURATION ---
        # IMPORTANT: Replace "YOUR_API_KEY" with your actual Google AI Studio API key.
        # For security, it's recommended to load this from an environment variable.
        self.api_key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY")

        if self.api_key == "YOUR_API_KEY":
            print("⚠️ WARNING: Gemini API key is not set. Planner will use a dummy response.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

        # This is the system prompt that instructs the LLM on how to behave.
        self.system_prompt = self._construct_system_prompt()

    def _construct_system_prompt(self):
        """
        Creates the detailed system prompt that guides the LLM's planning process.
        """
        # This is a simplified list of tools. A real implementation would have more detail.
        available_tools = """
        - `execute_script`: Executes a shell, Python, or Node.js script.
          - `params`: {"script": "<path_to_script>"}
        - `execute_in_ubuntu`: Executes a shell command inside the Ubuntu environment.
          - `params`: {"command": "<shell_command>"}
        - `fs.write`: Writes content to a file.
          - `params`: {"path": "<file_path>", "content": "<file_content>"}
        - `fs.read`: Reads the content of a file.
          - `params`: {"path": "<file_path>"}
        - `fs.list`: Lists files in a directory.
          - `params`: {"path": "<directory_path>"}
        """

        return f"""
You are an expert planning agent. Your task is to take a user request and break it down into a precise, step-by-step plan in JSON format.

The user's request will be provided to you. You must generate a plan that consists of a list of actions. Each action must have an "action" name and a "params" dictionary.

Based on the user's request, you must decide which tool to use and what parameters to provide. Here are the tools available to you:
{available_tools}

RULES:
- Your response MUST be a valid JSON object.
- The JSON object must contain a single key, "plan".
- The value of "plan" must be a list of action objects.
- Each action object must have an "action" key and a "params" key.
- The "action" key must be one of the tools listed above (e.g., "fs.write").
- The "params" key must be a dictionary containing the parameters for that action.
- Think step-by-step to create the most logical plan to achieve the user's goal.

Example Request: "Create a python script that prints 'hello' and then run it."
Example Response:
```json
{{
  "plan": [
    {{
      "action": "fs.write",
      "params": {{
        "path": "hello.py",
        "content": "print('hello')"
      }}
    }},
    {{
      "action": "execute_script",
      "params": {{
        "script": "hello.py"
      }}
    }}
  ]
}}
```
"""

    def create_plan(self, user_request: str) -> list:
        """
        Generates a plan using the Gemini LLM.
        If the API key is not set, it returns a dummy plan for testing.
        """
        if not self.model:
            # Return a dummy plan if the API key is not configured
            print("INFO: Using dummy plan because Gemini API key is not set.")
            return json.loads("""
            {
              "plan": [
                {
                  "action": "fs.write",
                  "params": {
                    "path": "test.txt",
                    "content": "This is a dummy plan from the planner."
                  }
                },
                {
                  "action": "execute_in_ubuntu",
                  "params": {
                    "command": "echo 'Hello from the dummy plan!'"
                  }
                }
              ]
            }
            """)["plan"]

        full_prompt = f"{self.system_prompt}\nUser Request: \"{user_request}\""

        print("Generating plan with Gemini Pro...")
        try:
            response = self.model.generate_content(full_prompt)
            # The response text might be wrapped in ```json ... ```, so we need to extract it.
            json_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            plan_data = json.loads(json_text)
            return plan_data.get("plan", [])
        except Exception as e:
            print(f"Error generating or parsing plan: {e}")
            return []
