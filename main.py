import importlib

# Since the directory name has a hyphen, we use importlib to import the modules
planner_module = importlib.import_module("agent-core.planner")
executor_module = importlib.import_module("agent-core.executor")

Planner = planner_module.Planner
Executor = executor_module.Executor

def main():
    """
    Main function to run the Super-Gemini agent.
    """
    print("🚀 Starting Super-Gemini Agent...")

    # 1. Instantiate the Planner and Executor
    planner = Planner()
    executor = Executor()

    # 2. Create a dummy user request
    user_request = "Run the hello-world scripts for all supported languages."

    # 3. Create a plan
    plan = planner.create_plan(user_request)

    # 4. Execute the plan
    executor.run_plan(plan)

    print("✅ Super-Gemini Agent finished its run.")

if __name__ == "__main__":
    main()
