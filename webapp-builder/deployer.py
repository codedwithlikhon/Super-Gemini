class Deployer:
    """
    Deploys web applications to local or cloud environments.
    """
    def deploy(self, project_path: str, target: str):
        """
        Deploys the project.
        """
        print(f"Deploying project at {project_path} to {target}")
