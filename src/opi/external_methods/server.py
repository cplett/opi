import sys
import pickle
import socket
import time

from typing import Any
from multiprocessing.connection import Client

from opi.external_methods.process import Process


class OpiServer:
    """
    Class for running a server from a file using a network socket.
    """

    def __init__(self, serverpath: str, host_id : str = "127.0.0.1", port: int = 9000):
        """
        Initialize server object with default values.

        Attributes
        ----------
        serverpath: str
            Path to the server script
        host_id: str, default: 127.0.0.1 (for local server only)
            IP to bind server to.
            Can be changed, if someone wants, e.g., a network server.
        port: int, default: 9000
            Port for the server
        """
        self.process = Process()  # Process starting the server
        self.serverpath = serverpath
        self._host_id = host_id
        self._port = port

    def set_id_and_port(self, host_id: str, port: int) -> None:
        """
        Change the host_id and port.

        Attributes
        ----------
        host_id: str
            host_id ID.
        port: int
            Port to use.
        """
        self._host_id = host_id
        self._port = port

    def start_server(self, exe: str = sys.executable) -> None:
        """
        Starts the Server from script
        Passes self._host_id and self._port as command-line arguments to the server script.

        Parameters
        ----------
        exe: str, default: sys.executable
            Executable to use for starting the server
        """
        # First check, whether server.port is free
        if self.server_port_in_use():
            print(
                f"Couldn't setup server on port {self._port} as the port is already in use."
            )
            print("Please check whether all previous server were terminated.")
            sys.exit(101) # Exit and return 101 code
        else:
            # Start server by running a python process
            # Therefore, first set up the command line call for the server script
            if not self.process.process_is_running():
                # Build the command list:
                # ["python", server_script] + --host_id ID + --port port + optional args
                cmd = [exe, self.serverpath]
                cmd.append("-b")
                cmd.append(f"{self._host_id}:{self._port}")
                # Start the server
                self.process.start(cmd)
                print(f"Server started with PID {self.process.process}")
            else:
                print("Server is already running.")

            # Wait a little to make sure server is fully initialized
            time.sleep(5)

    def kill_server(self):
        """
        Terminates the server if running
        """
        self.process.stop_process()

    def server_port_in_use(self) -> bool:
        """
        Checks whether self._port is already in use.

        Returns
        ----------
        bool
            True if port is already used.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self._host_id, self._port))
            except OSError:
                return True  # Port is in use
        return False  # Port is free


class CalcServer:
    """
    Class for running an OpiServer and load a calculator via pickle
    """

    def __init__(
        self, serverpath: str, calculator: Any = None, host_id: str = "127.0.0.1", port: int = 9000
    ):
        """
        Initialize server object with default values.

        Attributes
        ----------
        serverpath: str
            Path to the server script
        calculator: Any, default: None
            Anything that can be send to the server via pickle
            Intended here to be calculator
        host_id: str, default: 127.0.0.1 (for local server only)
            IP to bind server to
            Can be changed, if someone wants, e.g., a network server
        port: int, default: 9000
            Port for the server
        """
        # Server values are set one time at the beginning and not changed
        # If a new server should be set up, a new CalcServer instance must be initialized
        self.server = OpiServer(serverpath=serverpath, host_id=host_id, port=port)
        self._calculator = calculator

    @property
    def calculator(self):
        return self._calculator

    @calculator.setter
    def calculator(self, calc):
        self._calculator = calc

    def set_id_and_port(self, host_id: str, port: int) -> None:
        """
        Change the host_id and port if server not running.

        Attributes
        ----------
        host_id: str
            host_id ID.
        port: int
            Port to use.
        """
        if not self.server.server_port_in_use():
            self.server.set_id_and_port(host_id=host_id, port=port)
            print("ID and port successfully set up.")
        else:
            print("ID and port could not be set up.")

    def load_calculator(self) -> None:
        """
        Send the calculator to the server via pickle.
        """
        # Open a connection to server
        address = (self.server._host_id, self.server._port)
        with Client(address, authkey=b'secret') as conn:
            conn.send({"type": "setup_calculator", "calculator": self._calculator})
            response = conn.recv()
            print("Server setup response:", response)

    def start_server(self, exe: str = sys.executable) -> None:
        """
        Start the server.

        Parameters
        ----------
        exe: str, default=sys.executable
            Executable to use for starting the server
        """
        self.server.start_server(exe=exe)

    def kill_server(self) -> None:
        """
        Kill the server.
        """
        self.server.kill_server()
