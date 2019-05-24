import json
import requests

from utils import Logger, ES_AUTH, ES_HOST, FEATURE_SET_FILE, FEATURE_SET_NAME
from urllib.parse import urljoin


def load_features(feature_set_file: str, feature_set_name: str):
    """
    Obtain all found features from the filesystem and store them into elasticsearch using the provided name of the
    feature set.
    :param feature_set_file:            the file path where the feature JSON is stored
    :param feature_set_name:            name of the feature set to use
    """
    feature_set = json.loads(open(feature_set_file).read())
    path = "_ltr/_featureset/%s" % feature_set_name
    full_path = urljoin(ES_HOST, path)

    Logger.logger.info("POST %s" % full_path)
    Logger.logger.info(json.dumps(feature_set, indent=2))

    head = {'Content-Type': 'application/json'}
    resp = requests.post(full_path, data=json.dumps(feature_set), headers=head, auth=ES_AUTH)

    Logger.logger.info("%s" % resp.status_code)
    Logger.logger.info("%s" % resp.text)


def init_default_store():
    """
    Initialize the default feature store.
    """
    path = urljoin(ES_HOST, '_ltr')

    Logger.logger.info("Trying to create %s" % path)
    Logger.logger.info("PUT %s" % path)

    resp = requests.put(path, auth=ES_AUTH)

    Logger.logger.info("%s" % resp.status_code)


if __name__ == "__main__":
    from time import sleep

    init_default_store()
    sleep(1)
    load_features(FEATURE_SET_FILE, FEATURE_SET_NAME)