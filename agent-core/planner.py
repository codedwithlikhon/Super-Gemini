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

        # Dummy plan for now
        plan = [
            {"action": "execute_script", "script": "test_scripts/hello.sh"},
            {"action": "execute_in_ubuntu", "command": "echo 'Hello from inside Ubuntu!'"},
        ]

        print("Plan created successfully.")
        return plan
