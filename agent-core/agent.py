import importlib

# Dynamically import planner, executor, and memory_manager
planner_module = importlib.import_module("agent-core.planner")
executor_module = importlib.import_module("agent-core.executor")
memory_manager_module = importlib.import_module("agent-core.memory_manager")
ubuntu_manager_module = importlib.import_module("agent-core.ubuntu_manager")

Planner = planner_module.Planner
Executor = executor_module.Executor
MemoryManager = memory_manager_module.MemoryManager
ubuntu_manager = ubuntu_manager_module

class Agent:
    """
    The central agent that orchestrates the planner, executor, and memory.
    """
    def __init__(self):
        print("Initializing agent...")
        self.planner = Planner()
        self.executor = Executor()
        self.memory = MemoryManager()
        self.ubuntu_installed = ubuntu_manager.is_ubuntu_installed()

        if self.ubuntu_installed:
            print("✅ Ubuntu environment detected.")
        else:
            print("⚠️ Ubuntu environment not found. Some features may be unavailable.")

        print("Agent initialized successfully.")

    def _start_model_runner_if_needed(self):
        """
        Checks for the Ubuntu environment and starts the local model runner inside it.
        """
        if not self.ubuntu_installed:
            return

        print("🚀 Preparing to start local model runner...")

        # NOTE: In a real scenario, we would check if the process is already running.
        # For now, we start it on every agent run for demonstration.

        # 1. Install dependencies from requirements.txt inside Ubuntu
        print("Installing model runner dependencies in Ubuntu...")
        # Assuming tools directory is accessible from the root of the project
        # The paths need to be relative to where the agent is run from.
        # For simplicity, we assume 'tools/requirements.txt' is a valid path.
        ubuntu_manager.execute_in_ubuntu("pip3 install -r tools/requirements.txt")

        # 2. Start the model runner as a background process
        print("Starting model runner as a background process...")
        log_file = "/tmp/model_runner.log"
        command = f"nohup python3 tools/model_runner.py > {log_file} 2>&1 &"
        ubuntu_manager.execute_in_ubuntu(command)
        print(f"✅ Model runner started. See logs in Ubuntu at: {log_file}")

    def run(self, user_request: str):
        """
        Runs the main agentic loop.
        """
        print("\n🚀 Starting new agent run...")

        # Start the local model runner if the environment is available
        self._start_model_runner_if_needed()

        # 1. Load preferences
        preferences = self.memory.get_preferences()
        print(f"Loaded preferences: {preferences}")

        # 2. Create a plan
        plan = self.planner.create_plan(user_request)

        # 3. Execute the plan
        self.executor.run_plan(plan)

        # 4. Log the outcome (for now, just a message)
        print("\n📊 Run outcome: Success (dummy log)")

        # 5. Update memory with the result
        self.memory.update_preferences({"last_run_status": "success", "last_task": user_request})

        print("✅ Agent run finished.")
