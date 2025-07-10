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
        self.process = None

    def start(self, cmd: list[str], pipe=False) -> None:
        """
        Starts any process

        Attributes
        ----------
        cmd: str
            List of arguments to be executed
        pipe: bool, default: False
            Determines whether to hold the channel open for piping input in or not.
        """
        if self.process is None or self.process.poll() is not None:
            # Start the server, optionally leave pipe open via stdin
            pipe_kwargs = {}
            if pipe:
                pipe_kwargs["stdin"] = subprocess.PIPE
            self.process = subprocess.Popen(cmd, **pipe_kwargs)
            print(f"Process started with PID {self.process.pid}")
        else:
            print("Process is already running.")

    def stop_process(self) -> None:
        """
        Kills the process if its running.
        """
        if self.process and self.process.poll() is None:
            print(f"Stopping process with PID {self.process.pid}")
            self.process.terminate()
            self.process.wait()
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
