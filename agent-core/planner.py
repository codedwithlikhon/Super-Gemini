import os

class Planner:
    """
    Interprets user requests and breaks them down into executable tasks.
    """
    def create_plan(self, user_request: str) -> list:
        """
        Creates a plan from a user request.
        For now, it returns a dummy plan.
        """
        print(f"Received user request: '{user_request}'")
        print("Creating a plan...")

        plan = []
        if "hello-world" in user_request:
            test_scripts_dir = "test_scripts"
            scripts = os.listdir(test_scripts_dir)
            for script in scripts:
                if script.startswith("hello."):
                    plan.append({"action": "execute_script", "script": os.path.join(test_scripts_dir, script)})

        print("Plan created successfully.")
        return plan
