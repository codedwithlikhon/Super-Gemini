import importlib

# Dynamically import the Agent class
agent_module = importlib.import_module("agent-core.agent")
Agent = agent_module.Agent

def main():
    """
    Main function to run the Super-Gemini agent.
    """
    agent = Agent()
    user_request = "Run the hello-world scripts for all supported languages."
    agent.run(user_request)

if __name__ == "__main__":
    main()
