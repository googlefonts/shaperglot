from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution('shaperglot').version
except DistributionNotFound:
    __version__ = '(local)'
