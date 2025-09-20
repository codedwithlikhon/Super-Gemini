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
    user_request = "Create a new file named 'diary.txt' and write 'Today was a good day.' into it, then read the file back to confirm the content."

    # 3. Run the agent
    agent.run(user_request)

if __name__ == "__main__":
    main()
