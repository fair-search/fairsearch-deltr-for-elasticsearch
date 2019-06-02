import pandas as pd
import json

from fairsearchdeltr import Deltr
from prepare import init_default_store, load_features
from utils import Logger, elastic_connection, ES_HOST, ES_AUTH, JUDGMENTS_FILE, \
    FEATURE_SET_NAME, MODEL_FILE, MODEL_NAME, QUERIES_FILE, FEATURES_FILE, INDEX_NAME

log_query = {
  "size": 1000,
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "_id": [
            ]
          }
        },
        {
          "sltr": {
            "_name": "logged_featureset",
            "featureset": "",
            "params": {
              "keywords": ""
            }
          }
        }
      ]
    }
  },
  "ext": {
    "ltr_log": {
      "log_specs": {
        "name": "log_entry",
        "named_query": "logged_featureset",
        "missing_as_zero": "true"
      }
    }
  }
}


def log_features(es, query_id: int, query: str, ids: list, feature_set_name: str, index_name: str):
    """
    :param es:                      Elasicsearch client
    :param query:                   Query to train on
    :param ids:                     Document IDs with known judgements for this query
    :param feature_set_name:        What feature set to get the score for
    :param index_name:              What index to search against
    :return:
    """
    log_query['query']['bool']['filter'][0]['terms']['_id'] = ids
    log_query['query']['bool']['filter'][1]['sltr']['params']['keywords'] = query
    log_query['query']['bool']['filter'][1]['sltr']['featureset'] = feature_set_name
    Logger.logger.info("*** POST " + str(query_id))
    Logger.logger.info(json.dumps(log_query, indent=2))
    resp = es.search(index=index_name, body=log_query)
    return resp['hits']['hits']


def collect_train_data(es, queries_file, judgments_file, feature_set_name, index_name, features_file):
    """ CCollects the train data from Elasticsearch
    """
    queries = pd.read_csv(queries_file)
    judgements = pd.read_csv(judgments_file)

    header_id = "query_id,document_id"
    header_feat = None
    header_judgement = "judgement"

    with open(features_file, 'w') as f:
        for q in range(queries.shape[0]):
            q_id  = queries.loc[q]['query_id']
            keywords = queries.loc[q]['keywords']
            ids = judgements.loc[judgements['query_id'] == q_id]['document_id'].tolist()
            hits = log_features(es, q_id, keywords, ids, feature_set_name, index_name)

            for doc in hits:
                doc_id = doc['_id']
                log = doc['fields']['_ltrlog'][0]['log_entry']

                if not header_feat:
                    header_feat = ",".join([a["name"] for a in log])
                    f.write("{0},{1},{2}\n".format(header_id, header_feat, header_judgement))

                values = ",".join([str(a["value"]) for a in log])

                judgement = judgements.loc[judgements['document_id'] == doc_id]['judgement'].iloc[0]

                f.write("{0},{1},{2},{3}\n".format(q_id, doc_id, values, judgement))


def train_model(features_file: str, model_output: str,
                protected_feature_name="1", gamma=1, number_of_iterations=10, learning_rate=0.001,
                lambdaa=0.001, init_var=0.01, standardize=True):
    """
    Trains the DELTR model with the specified parameters
    :param features_file:           The train file with features and judgements
    :param model_output:            The file where the model is going to be stored
    :param protected_feature_name:       The name of the column in the data that contains protected attribute
    :param gamma:                   gamma parameter for the cost calculation in the training phase
                                        (recommended to be around 1)
    :param number_of_iterations     number of iteration in gradient descent (optional)
    :param learning_rate            learning rate in gradient descent (optional)
    :param lambdaa                  regularization constant (optional)
    :param init_var                 range of values for initialization of weights (optional)
    :param standardize              boolean indicating whether the data should be standardized or not (optional)
    :return:
    """

    Logger.logger.info("*** Reading train data ")
    train_data = pd.read_csv(features_file)

    # get the feature names
    feature_names = train_data.columns.tolist()[2:-1]

    # find the index of the protected attribute
    protected_feature = train_data.columns.tolist().index(protected_feature_name) - 2  # minus  for the query and doc id

    # create the Deltr object
    dtr = Deltr(protected_feature, gamma, number_of_iterations, learning_rate, lambdaa, init_var, standardize)

    Logger.logger.info("*** Training...")
    model = dtr.train(train_data)
    Logger.logger.info("*** Done training")

    Logger.logger.info("*** Saving model")
    with(open(model_output, 'w')) as f:
        json.dump(dict(zip(feature_names, model)), f)
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
                "type": "model/linear",
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
    es = elastic_connection(timeout=1000)

    # Load features into Elasticsearch
    # init_default_store()
    # load_features(FEATURE_SET_NAME)

    # Train as ranklib type; DELTR is actually - (9) Linear Regression
    # Logger.logger.info("*** Training DELTR ")

    collect_train_data(es, QUERIES_FILE, JUDGMENTS_FILE, FEATURE_SET_NAME, INDEX_NAME, FEATURES_FILE)
    train_model(features_file=FEATURES_FILE, model_output=MODEL_FILE)
    save_model(script_name="somemodel", feature_set=FEATURE_SET_NAME, model_fname=MODEL_FILE)