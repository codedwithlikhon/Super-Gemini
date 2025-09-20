class ScaffoldGenerator:
    """
    Generates boilerplate for web applications.
    """
    def __init__(self, templates_path: str = "templates"):
        self.templates_path = templates_path

    def generate(self, project_name: str, framework: str):
        """
        Generates a new project scaffold.
        """
        print(f"Generating {framework} project named {project_name}")
