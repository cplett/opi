import subprocess


class Process:
    """
    Class that runs a process, monitors it and terminates it.
    """

    def __init__(self):
        """
        Init Process object
        """
        # Variable for storing the process
        self.process: subprocess.Popen | None = None

    def start(self, cmd: list[str], pipe: bool=False) -> None:
        """
        Starts a subprocess

        Attributes
        ----------
        cmd: str
            List of arguments to be executed
        pipe: bool, default: False
            Determines whether to hold the channel open for piping input in or not.

        Raises
        ------
        FileNotFoundError: If a file included in the cmd is not found.
        OSError: If the executable is not found or fails to execute.
        ValueError: If an invalid parameter is passed to Popen.
        subprocess.SubprocessError: For other errors related to subprocess management.
        """
        if not self.process_is_running():
            # Start the server, optionally leave pipe open via stdin
            pipe_kwargs = {}
            if pipe:
                pipe_kwargs["stdin"] = subprocess.PIPE
            try:
                self.process = subprocess.Popen(cmd, **pipe_kwargs)
                print(f"Process started with PID {self.process.pid}")
            except FileNotFoundError as e:
                print("Command not found:", e)
            except ValueError as e:
                print("Invalid arguments:", e)
            except subprocess.SubprocessError as e:
                print("Subprocess error:", e)
            except OSError as e:
                print("OS error:", e)
        else:
            print("Process is already running.")

    def stop_process(self) -> None:
        """
        Kills the process if its running.
        """
        if self.process_is_running():
            print(f"Stopping process with PID {self.process.pid}")
            # Softkill
            self.process.terminate()
            try:
                self.process.wait(timeout=30)
                self.process = None
            except subprocess.TimeoutExpired:
            # Hard kill
                self.process.kill()
        self.process = None

    def process_is_running(self) -> bool:
        """
        Returns true if the process is running and false if not.

        Returns
        -------
        bool
            True if process is running, otherwise false
        """
        return self.process and self.process.poll() is None
