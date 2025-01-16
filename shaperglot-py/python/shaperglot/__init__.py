from pkg_resources import DistributionNotFound, get_distribution

from shaperglot._shaperglot import (
    Check,
    Checker,
    CheckResult,
    Language,
    Languages,
    Problem,
    Reporter,
)

try:
    __version__ = get_distribution('shaperglot').version
except DistributionNotFound:
    __version__ = '(local)'
