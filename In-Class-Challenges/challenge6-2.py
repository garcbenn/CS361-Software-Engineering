
import sys
import datetime


class Logger:
    def event(self, s):
        print(s)

    def warning(self, s):
        print(s, file=sys.stderr)


class TimeLogger:
    def isotime(self):
        return datetime.datetime.now().isoformat()

    def event(self, s):
        print(f"{self.isotime()}: {s}")

    def warning(self, s):
        print(f"{self.isotime()}: WARNING: {s}")


class Divider:
    def __init__(self, logger):
        self.logger = logger

    def divide(self, a, b):
        if b == 0:
            self.logger.warning("division by zero")
            return None

        self.logger.event(f"dividing {a} by {b}")
        return a / b


# Create two Divider objects with different loggers
d1 = Divider(Logger())
d2 = Divider(TimeLogger())

# Test Divider using the original Logger
print("Testing Logger:")
d1.divide(1, 2)
d1.divide(10, 5)
d1.divide(99, 0)

# Test Divider using TimeLogger
print("\nTesting TimeLogger:")
d2.divide(1, 2)
d2.divide(10, 5)
d2.divide(99, 0)
