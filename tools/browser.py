class Browser:
    """
    A tool for browsing the web.
    """
    def search(self, query: str) -> str:
        print(f"Searching for: {query}")
        return f"Search results for '{query}'"

    def fetch_url(self, url: str) -> str:
        print(f"Fetching content from: {url}")
        return f"Content of {url}"
