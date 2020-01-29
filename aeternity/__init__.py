import pkg_resources
import logging

__node_compatibility__ = (">=5.0.0", "<=6.0.0")
__compiler_compatibility__ = (">=4.1.0", "<5.0.0")

# initialize logging
logging.basicConfig(level=logging.ERROR)


def _version():
    try:
        return pkg_resources.get_distribution('aepp-sdk').version
    except pkg_resources.DistributionNotFound:
        return 'snapshot'
