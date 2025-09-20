import requests

class ApiCaller:
    """
    A tool for making API requests.
    """
    def get(self, url: str, params: dict = None) -> dict:
        print(f"Making GET request to: {url}")
        response = requests.get(url, params=params)
        return response.json()

    def post(self, url: str, data: dict = None) -> dict:
        print(f"Making POST request to: {url}")
        response = requests.post(url, json=data)
        return response.json()
