from enum import Enum
from collections import Sequence
from termcolor import colored


class Result(Enum):
    PASS = colored("PASS", "green")
    WARN = colored("WARN", "yellow")
    FAIL = colored("FAIL", "red")


class Reporter(Sequence):
    def __init__(self):
        self.results = []

    def __getitem__(self, index):
        return self.results[index]

    def __len__(self):
        return len(self.results)

    def okay(self, message):
        self.results.append((Result.PASS, message))

    def warn(self, message):
        self.results.append((Result.WARN, message))

    def fail(self, message):
        self.results.append((Result.FAIL, message))

    @property
    def is_success(self):
        return not self.fails

    @property
    def fails(self):
        return [x[1] for x in self.results if x[0] == Result.FAIL]

    @property
    def warns(self):
        return [x[1] for x in self.results if x[0] == Result.WARN]
