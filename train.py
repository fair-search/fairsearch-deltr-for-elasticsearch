import pandas as pd

from fairsearchdeltr import Deltr
from prepare import init_default_store, load_features
from utils import Logger, elastic_connection, ES_HOST, ES_AUTH, JUDGMENTS_FILE_FEATURES, \
    FEATURE_SET_NAME, MODEL_FILE, MODEL_NAME


def train_model(judgments_with_features_file: str, model_output: str,
                protected_feature=0, gamma=1, number_of_iterations=10, learning_rate=0.001,
                lambdaa=0.001, init_var=0.01, standardize=True):
    """
    Trains the DELTR model with the specified parameters
    :param judgments_with_features_file:        The train judgement file
    :param model_output:                        The file where the model is going to be stored
    :param protected_feature:       index of column in data that contains protected attribute
    :param gamma:                   gamma parameter for the cost calculation in the training phase
                                        (recommended to be around 1)
    :param number_of_iterations     number of iteration in gradient descent (optional)
    :param learning_rate            learning rate in gradient descent (optional)
    :param lambdaa                  regularization constant (optional)
    :param init_var                 range of values for initialization of weights (optional)
    :param standardize              boolean indicating whether the data should be standardized or not (optional)
    :return:
    """

    train_data = pd.read_csv(judgments_with_features_file)
    Logger.logger.info("*** Read train data ")

    # create the Deltr object
    dtr = Deltr(protected_feature, gamma, number_of_iterations, learning_rate, lambdaa, init_var, standardize)

    Logger.logger.info("*** Training...")
    model = dtr.train(train_data)
    Logger.logger.info("*** Done training")

    Logger.logger.info("*** Saving model")
    with(open(model_output, 'w')) as f:
        f.write("## Linear Regression # DELTR\n")
        f.write("## Lamda = %s\n" % dtr._lambda)
        f.write("0:%s" % model[-1])
        for i,w in enumerate(model[:-1]):
            f.write(" %s:%s" % (i+1, w))
    Logger.logger.info("*** Done saving model")


def save_model(script_name, feature_set, model_fname):
    """
    Save the DELTR model in Elasticsearch
    """
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

        Logger.logger.info("*** Uploading model")
        Logger.logger.info("POST %s" % full_path)

        head = {'Content-Type': 'application/json'}
        resp = requests.post(full_path, data=json.dumps(model_payload), headers=head, auth=ES_AUTH)

        Logger.logger.info(resp.status_code)
        Logger.logger.error(resp.text)


if __name__ == "__main__":
    # es = elastic_connection(timeout=1000)

    # Load features into Elasticsearch
    # init_default_store()
    # load_features(FEATURE_SET_NAME)

    # Train as ranklib type; DELTR is actually - (9) Linear Regression
    Logger.logger.info("*** Training DELTR ")

    train_model(judgments_with_features_file=JUDGMENTS_FILE_FEATURES, model_output=MODEL_FILE)
    # save_model(script_name=MODEL_NAME, feature_set=FEATURE_SET_NAME, model_fname=MODEL_FILE)