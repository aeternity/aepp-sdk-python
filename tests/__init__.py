import logging
# for tempdir


logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("aeternity").setLevel(logging.DEBUG)
logging.root.setLevel(logging.DEBUG)


# default values for tests
TEST_TTL = 50
