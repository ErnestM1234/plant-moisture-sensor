import sys

# Log levels as constants instead of Enum
LOG_LEVEL_NONE = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_WARN = 2
LOG_LEVEL_ERROR = 3

class Log:
    # ANSI color codes for terminal output
    COLORS = {
        'RED': '\033[91m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'RESET': '\033[0m'
    }

    def __init__(self, level=LOG_LEVEL_INFO, output=sys.stdout):
        self.level = level
        self.output = output

    def set_level(self, level):
        """Set the minimum log level that will be displayed."""
        self.level = level

    def info(self, message):
        """Log an info message if the current level allows it."""
        if self.level <= LOG_LEVEL_INFO:
            self._log(f"{self.COLORS['BLUE']}[INFO]{self.COLORS['RESET']} {message}")

    def warn(self, message):
        """Log a warning message if the current level allows it."""
        if self.level <= LOG_LEVEL_WARN:
            self._log(f"{self.COLORS['YELLOW']}[WARN]{self.COLORS['RESET']} {message}")

    def error(self, message):
        """Log an error message if the current level allows it."""
        if self.level <= LOG_LEVEL_ERROR:
            self._log(f"{self.COLORS['RED']}[ERROR]{self.COLORS['RESET']} {message}")

    def _log(self, message):
        """Internal method to handle the actual logging."""
        print(message, file=self.output)

# Create a default logger instance
log = Log()

if __name__ == "__main__":
    # Example usage of the logger
    log.info("This is an info message")
    log.warn("This is a warning message")
    log.error("This is an error message")
    
    # Disable info messages
    log.set_level(LOG_LEVEL_WARN)
    log.info("This info won't show")
    log.warn("This warning will show")
    log.error("This error will show")
    
    # Only show errors
    log.set_level(LOG_LEVEL_ERROR)
    log.info("This info won't show")
    log.warn("This warning won't show")
    log.error("This error will show")
    
    # Disable all logging
    log.set_level(LOG_LEVEL_NONE)
    log.info("Nothing will show")
    log.warn("Nothing will show")
    log.error("Nothing will show")

