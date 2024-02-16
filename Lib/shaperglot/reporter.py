from enum import Enum
from collections.abc import Sequence
from dataclasses import dataclass, field

from termcolor import colored

class Result(Enum):
    PASS = colored("PASS", "green")
    WARN = colored("WARN", "yellow")
    FAIL = colored("FAIL", "red")
    SKIP = colored("SKIP", "blue")


@dataclass(repr=False)
class Message():
    result: Result
    check_name: str
    message: str
    result_code: str = "ok"
    context: dict = field(default_factory=dict)

    def __repr__(self):
        return self.result.value + ": " + self.message


class Reporter(Sequence):
    def __init__(self):
        self.results = []

    def __getitem__(self, index):
        return self.results[index]

    def __len__(self):
        return len(self.results)

    def okay(self, **kwargs):
        self.results.append(Message(result=Result.PASS, **kwargs))

    def warn(self, **kwargs):
        self.results.append(Message(result=Result.WARN, **kwargs))

    def fail(self, **kwargs):
        self.results.append(Message(result=Result.FAIL, **kwargs))

    def skip(self, **kwargs):
        self.results.append(Message(result=Result.SKIP, **kwargs))

    @property
    def is_unknown(self):
        return not self.passes and not self.fails

    @property
    def is_success(self):
        return len(self.passes) > 0 and not self.fails

    @property
    def passes(self):
        return [x for x in self.results if x.result == Result.PASS]

    @property
    def fails(self):
        return [x for x in self.results if x.result == Result.FAIL]

    @property
    def warns(self):
        return [x for x in self.results if x.result == Result.WARN]
