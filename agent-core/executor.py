import subprocess

class Executor:
    """
    Executes scripts in bash, Python, or Node.js.
    """
    def execute_script(self, script_path: str):
        """
        Executes a script based on its file extension.
        """
        print(f"Executing script: {script_path}")

        try:
            if script_path.endswith(".sh"):
                result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
            elif script_path.endswith(".py"):
                result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            elif script_path.endswith(".js"):
                result = subprocess.run(["node", script_path], capture_output=True, text=True, check=True)
            else:
                print(f"Unsupported script type: {script_path}")
                return

            print(f"Output of {script_path}:")
            print(result.stdout)

        except FileNotFoundError:
            print(f"Error: The runtime for the script '{script_path}' was not found.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script_path}:")
            print(e.stderr)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def run_plan(self, plan: list):
        """
        Executes a plan from the Planner.
        """
        print("Executing plan...")
        for task in plan:
            if task["action"] == "execute_script":
                self.execute_script(task["script"])
        print("Plan execution finished.")
