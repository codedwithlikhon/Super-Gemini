import importlib

# Dynamically import the Agent class
agent_module = importlib.import_module("agent-core.agent")
Agent = agent_module.Agent

def main():
    """
    Main function to run the Super-Gemini agent.
    """
    # 1. Instantiate the Agent
    agent = Agent()

    # 2. Define a user request
    user_request = "Create a file named 'plan_test.txt' in the root directory, write a friendly greeting into it, and then list the files in the current directory to confirm it was created."

    # 3. Run the agent
    agent.run(user_request)

if __name__ == "__main__":
    main()
