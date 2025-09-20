import importlib

# Dynamically import planner, executor, and memory_manager
planner_module = importlib.import_module("agent-core.planner")
executor_module = importlib.import_module("agent-core.executor")
memory_manager_module = importlib.import_module("agent-core.memory_manager")

Planner = planner_module.Planner
Executor = executor_module.Executor
MemoryManager = memory_manager_module.MemoryManager

class Agent:
    """
    The central agent that orchestrates the planner, executor, and memory.
    """
    def __init__(self):
        print("Initializing agent...")
        self.planner = Planner()
        self.executor = Executor()
        self.memory = MemoryManager()
        print("Agent initialized successfully.")

    def run(self, user_request: str):
        """
        Runs the main agentic loop.
        """
        print("\n🚀 Starting new agent run...")

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
