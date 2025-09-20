class EmulatorControl:
    """
    A tool for controlling an Android emulator or VM.
    """
    def launch_app(self, app_id: str):
        print(f"Launching app: {app_id}")

    def tap(self, x: int, y: int):
        print(f"Tapping at ({x}, {y})")
