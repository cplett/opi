import sys
import pickle
import socket
import time

from opi.external_methods.process import Process


class OpiServer:
    """
    Class for running a server from a file via socket.
    """

    def __init__(self, serverpath: str, host_id="127.0.0.1", port=9000):
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

    def start_server(self) -> None:
        """
        Starts the Server from script
        Provides _host_id and _port via command line arguments
        """
        # First check, whether server.port is free
        if self.server_port_in_use():
            print(
                f"Couldn't setup server on port {self._port} as the port is already in use."
            )
            print("Please check whether all previous server were terminated.")
        else:
            # Start server by running a python process
            # Therefore, first set up the command line call for the server script
            if self.process.process is None or self.process.poll() is not None:
                # Build the command list:
                # ["python", server_script] + --host_id ID + --port port + optional args
                cmd = [sys.executable, self.serverpath]
                cmd.append("--host")
                cmd.append(str(self._host_id))
                cmd.append("--port")
                cmd.append(str(self._port))
                # Start the server
                self.process.start(cmd)
                print(f"Server started with PID {self.process.process}")
            else:
                print("Server is already running.")

            # Wait a little to make sure server is fully initialized
            time.sleep(5)

    def kill_server(self):
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
        self, serverpath: str, calculator=None, host_id="127.0.0.1", port=9000
    ):
        """
        Initialize server object with default values.

        Attributes
        ----------
        serverpath: str
            Path to the server script
        calculator: obj, default: None
            A calculator that could be send to the server
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

    def load_calculator(self) -> None:
        """
        Send the calculator to the server via pickle.
        """
        # Open a connection to server
        with socket.create_connection(
            (self.server._host_id, self.server._port)
        ) as sock:
            # Create a virtual file for communication
            wfile = sock.makefile("wb")
            # Send the calculator via pickle
            pickle.dump(
                {"type": "setup_calculator", "calculator": self._calculator}, wfile
            )
            wfile.flush()
            # Get a response
            rfile = sock.makefile("rb")
            response = pickle.load(rfile)
            print("Server setup response:", response)

    def start_server(self) -> None:
        """
        Start the server.
        """
        self.server.start_server()

    def kill_server(self) -> None:
        """
        Kill the server.
        """
        self.server.kill_server()
