import subprocess
import importlib

# Dynamically import the ubuntu_manager
ubuntu_manager_module = importlib.import_module("agent-core.ubuntu_manager")
ubuntu_manager = ubuntu_manager_module

class Executor:
    """
    Executes scripts in bash, Python, or Node.js, and commands inside the Ubuntu environment.
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
        Executes a plan from the Planner by dispatching tasks based on their action type.
        """
        print("Executing plan...")
        if not plan:
            print("Plan is empty. Nothing to execute.")
            return

        for task in plan:
            action = task.get("action")
            params = task.get("params", {})

            print(f"--- Executing action: {action} ---")

            if action == "execute_script":
                self.execute_script(params.get("script"))
            elif action == "execute_in_ubuntu":
                ubuntu_manager.execute_in_ubuntu(params.get("command"))
            elif "." in action:
                # This is a placeholder for tool execution, e.g., "fs.write"
                tool_name, tool_action = action.split('.', 1)
                print(f"INFO: Would execute tool '{tool_name}' (action: {tool_action}) with params: {params}")
            else:
                print(f"⚠️ Unknown action type: {action}")

        print("--- Plan execution finished. ---")
