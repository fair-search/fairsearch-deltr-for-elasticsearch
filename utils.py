import logging.config
import configparser
import elasticsearch

from requests.auth import HTTPBasicAuth

config = configparser.ConfigParser()
config.read('setup.cfg')

config_set = 'default'

# constants
ES_HOST = config[config_set]['ESHost']
if 'ESUser' in config[config_set]:
    auth = (config[config_set]['ESUser'], config[config_set]['ESPassword'])
    ES_AUTH = HTTPBasicAuth(*auth)
else:
    auth = None
    ES_AUTH = None

FEATURE_SET_NAME = config[config_set]['FeatureSetName']
FEATURE_SET_FILE = config[config_set]['FeatureSetNameFile']
JUDGMENTS_FILE_FEATURES = config[config_set]['JudgmentsFileWithFeature']
INDEX_NAME = config[config_set]['IndexName']
MODEL_FILE = config[config_set]['ModelFile']


def elastic_connection(url=None, timeout=1000, http_auth=auth):
    if url is None:
        url = ES_HOST
    return elasticsearch.Elasticsearch(url, timeout=timeout, http_auth=http_auth)


# logging related
def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Logger:
    def __init__(self):
        # logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('__name__')
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
