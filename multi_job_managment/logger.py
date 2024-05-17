import sys

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout  # Save a reference to the original standard output
        self.log = open(filename, "a")  # Open a log file in append mode

    def write(self, message):
        self.terminal.write(message)  # Write the message to the standard output
        self.log.write(message)  # Write the message to the log file
        self.flush()  # Ensure that each message is immediately flushed

    def flush(self):
        # Flush both the terminal and log file to ensure all messages are fully written out
        self.terminal.flush()
        self.log.flush()
