class CommandError(Exception):
    """
    Raised when there is a command error.
    """

    def __init__(
        self, command: str, status_code: int, stdout: str, stderr: str
    ) -> None:
        self.status_code = status_code
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        super().__init__(command, status_code, stdout, stderr)
