import os
import pandas as pd

from fairsearchdeltr import Deltr
from prepare import init_default_store, load_features
from utils import Logger, elastic_connection, ES_HOST, ES_AUTH, JUDGMENTS_FILE_FEATURES, FEATURE_SET_NAME, MODEL_FILE


def train_model(judgments_with_features_file, model_output):
    """
    Trains the DELTR model with the specified parameters
    :param judgments_with_features_file:        The train judgement file
    :param model_output:                        The file where the model is going to be stored
    :return:
    """

    train_data = pd.read_csv(judgments_with_features_file)
    Logger.logger.info("*** read train data ")

    # setup the DELTR object
    protected_feature = 0  # column number of the protected attribute (index after query and document id)
    gamma = 1  # value of the gamma parameter
    number_of_iteraions = 10  # number of iterations the training should run
    standardize = True  # let's apply standardization to the features

    # create the Deltr object
    dtr = Deltr(protected_feature, gamma, number_of_iteraions, standardize=standardize)

    Logger.logger.info("*** training...")
    model = dtr.train(train_data)
    Logger.logger.info("*** done training")

    Logger.logger.info("*** saving model")
    with(open(model_output, 'w')) as f:
        f.write("## Linear Regression # DELTR\n")
        f.write("## Lamda = %s\n" % dtr._lambda)
        f.write("0:%s" % model[-1])
        for i,w in enumerate(model[:-1]):
            f.write(" %s:%s" % (i+1, w))
    Logger.logger.info("*** done saving model")


def save_model(script_name, feature_set, model_fname):
    """
    Save the DELTR model in Elasticsearch
    """
    """  """
    import requests
    import json
    from urllib.parse import urljoin

    model_payload = {
        "model": {
            "name": script_name,
            "model": {
                "type": "model/ranklib",
                "definition": {
                }
            }
        }
    }

    with open(model_fname) as modelFile:
        model_content = modelFile.read()
        path = "_ltr/_featureset/%s/_createmodel" % feature_set
        full_path = urljoin(ES_HOST, path)
        model_payload['model']['model']['definition'] = model_content
        Logger.logger.info("POST %s" % full_path)
        head = {'Content-Type': 'application/json'}
        resp = requests.post(full_path, data=json.dumps(model_payload), headers=head, auth=ES_AUTH)
        Logger.logger.info(resp.status_code)
        if resp.status_code >= 300:
            Logger.logger.error(resp.text)


if __name__ == "__main__":
    # es = elastic_connection(timeout=1000)

    # Load features into Elasticsearch
    # init_default_store()
    # load_features(FEATURE_SET_NAME)

    # Train as ranklib type; DELTR is actually - (9) Linear Regression
    Logger.logger.info("*** Training DELTR ")

    # train_model(judgments_with_features_file=JUDGMENTS_FILE_FEATURES, model_output=MODEL_FILE)
    save_model(script_name="deltr_vanilla", feature_set=FEATURE_SET_NAME, model_fname=MODEL_FILE)