import json
import os

class MemoryManager:
    """
    Connects to the memory/ folder for preferences & vector store.
    """
    def __init__(self, memory_path="memory"):
        self.preferences_file = f"{memory_path}/preferences.json"
        self.vector_store_file = f"{memory_path}/vector_store.json"

    def get_preferences(self):
        """
        Reads user preferences from preferences.json.
        """
        try:
            with open(self.preferences_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Preferences file not found at {self.preferences_file}")
            return {}

    def get_from_vector_store(self, query: str):
        """
        Retrieves data from the vector store.
        (This is a dummy implementation)
        """
        print(f"Searching vector store for: '{query}'")
        # In a real implementation, this would involve embedding the query
        # and performing a similarity search in the vector store.
        return [{"text": "dummy result from vector store"}]

    def update_preferences(self, new_prefs: dict):
        """
        Updates user preferences in preferences.json.
        """
        os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
        current_prefs = self.get_preferences()
        current_prefs.update(new_prefs)
        with open(self.preferences_file, 'w') as f:
            json.dump(current_prefs, f, indent=4)
        print("Preferences updated successfully.")
