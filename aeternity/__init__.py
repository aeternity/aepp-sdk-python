import pkg_resources

__node_compatibility__ = (">=2.3.0", "<4.0.0")


def _version():
    try:
        return pkg_resources.get_distribution('aepp-sdk').version
    except pkg_resources.DistributionNotFound:
        return 'snapshot'
