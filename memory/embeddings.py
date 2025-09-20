class EmbeddingGenerator:
    """
    Generates embeddings for text to be stored in the vector store.
    """
    def generate(self, text: str) -> list:
        """
        Generates an embedding for the given text.
        """
        print(f"Generating embedding for: {text[:30]}...")
        # Placeholder for a real embedding model call
        return [0.1, 0.2, 0.3]
