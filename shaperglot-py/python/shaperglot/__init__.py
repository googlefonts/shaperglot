from pkg_resources import DistributionNotFound, get_distribution
from shaperglot._shaperglot import Checker, Languages, Reporter  # , Result

try:
    __version__ = get_distribution('shaperglot').version
except DistributionNotFound:
    __version__ = '(local)'
