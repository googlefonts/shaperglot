from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from termcolor import colored


class Result(Enum):
    PASS = colored("PASS", "green")
    WARN = colored("WARN", "yellow")
    FAIL = colored("FAIL", "red")
    SKIP = colored("SKIP", "blue")


@dataclass(repr=False)
class Message:
    result: Result
    check_name: str
    message: str
    result_code: str = "ok"
    context: dict = field(default_factory=dict)
    fixes: list = field(default_factory=list)

    def __repr__(self) -> str:
        return self.result.value + ": " + self.message

    def __hash__(self) -> int:
        hsh = hash(self.check_name + self.message + self.result.value)
        return hsh

    def __eq__(self, other) -> bool:
        return self.check_name == other.check_name and self.message == other.message


class Reporter(Sequence):
    def __init__(self) -> None:
        self.results = {}

    def __getitem__(self, index):
        return list(self.results.keys())[index]

    def __len__(self) -> int:
        return len(self.results.keys())

    def okay(self, **kwargs) -> None:
        self.results[Message(result=Result.PASS, **kwargs)] = 1

    def warn(self, **kwargs) -> None:
        self.results[Message(result=Result.WARN, **kwargs)] = 1

    def fail(self, **kwargs) -> None:
        self.results[Message(result=Result.FAIL, **kwargs)] = 1

    def skip(self, **kwargs) -> None:
        self.results[Message(result=Result.SKIP, **kwargs)] = 1

    @property
    def is_unknown(self) -> bool:
        return not self.passes and not self.fails

    @property
    def is_success(self) -> bool:
        return len(self.passes) > 0 and not self.fails

    def is_nearly_success(self, nearly: int) -> bool:
        return not self.is_success and self.count_fixes <= nearly

    @property
    def passes(self) -> list:
        return [x for x in self.results if x.result == Result.PASS]

    @property
    def fails(self) -> list:
        return [x for x in self.results if x.result == Result.FAIL]

    @property
    def warns(self) -> list:
        return [x for x in self.results if x.result == Result.WARN]

    def unique_fixes(self) -> Dict[str, list[str]]:
        fixes = defaultdict(list)
        for result in self.results:
            for fix in result.fixes:
                fixtype = fix["type"]
                fixthing = fix["thing"]
                if fixthing not in fixes[fixtype]:
                    fixes[fixtype].append(fixthing)
        return fixes

    @property
    def count_fixes(self) -> int:
        """Return the number of fixes required to pass all checks"""
        fixes = self.unique_fixes()
        return sum(len(stuff) for stuff in fixes.values())
