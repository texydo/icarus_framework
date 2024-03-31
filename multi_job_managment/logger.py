import sys

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout  # Save a reference to the original standard output
        self.log = open(filename, "a")  # Open a log file in append mode

    def write(self, message):
        self.terminal.write(message)  # Write the message to the standard output
        self.log.write(message)  # Write the message to the log file

    def flush(self):  # Needed for Python 3 compatibility
        # This flush method is needed for python 3 compatibility.
        # This handles the implicit flush command by file objects.
        pass