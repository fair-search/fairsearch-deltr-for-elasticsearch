import sys
import argparse

from utils import Logger, elastic_connection, FEATURE_SET_FILE, JUDGMENTS_FILE_FEATURES, \
    FEATURE_SET_NAME, MODEL_FILE, INDEX_NAME, ES_AUTH, ES_HOST, DOCUMENT_DIR, MODEL_NAME
from prepare import load_features, init_default_store
from train import save_model, train_model
from search import ltr_query


def index(index_name, document_dir):
    pass


def prepare(feature_set_file, feature_set_name):
    init_default_store()
    load_features(feature_set_file, feature_set_name)


def train(feature_set_name:str, model_name:str,
          judgments_with_features_file: str, model_output: str,
          protected_feature=0, gamma=1, number_of_iterations=3000, learning_rate=0.001,
          lambdaa=0.001, init_var=0.01, standardize=False):
    """
    Train and upload model with specified parameters
    """
    train_model(judgments_with_features_file, model_output, protected_feature, gamma,
                number_of_iterations, learning_rate, lambdaa, init_var, standardize)

    save_model(model_name, feature_set_name, model_output)


def search(index_name, query, model):
    """
    Peforms a search request on Elasticseach using LTR and a specified (DELTR) model
    :param index_name:       The index to search on
    :param query:       The query to search by
    :param model:       The model to search with
    :return:
    """
    es = elastic_connection(timeout=1000)
    results = es.search(index=index_name, body=ltr_query(query, model))
    for result in results['hits']['hits']:
        Logger.logger.info(result['_source']['id'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read command line arguments for DELTR LTR integration.')

    # add main commands
    parser.add_argument('--prepare', action='store_true',
                        help='Command to upload the feature set.')
    parser.add_argument('--index', action='store_true',
                        help='Command to index the data.')
    parser.add_argument('--train', action='store_true',
                        help='Command to train the model')
    parser.add_argument('--search', action='store_true',
                        help='Command to make a search query.')


    # add prepare arguments
    parser.add_argument('--feature-set-file', required=False, default=FEATURE_SET_FILE,
                        help='The features file path.')
    parser.add_argument('--feature-set-name', required=False, default=FEATURE_SET_NAME,
                        help='The features set name.')  # this is used in the train phase as well

    # add index arguments
    parser.add_argument('--index-name', required=False, default=INDEX_NAME,
                        help='The name of the index to create or run a query on.')
    parser.add_argument('--doc-dir', required=False, default=DOCUMENT_DIR,
                        help='The directory with documents to index.')

    # add train arguments
    parser.add_argument('--model', required=False, default=MODEL_NAME,
                        help='The name of the model.')  # this is used in the search phase as well
    parser.add_argument('--model-file', required=False, default=MODEL_FILE,
                        help='The file path where the model will be stored.')
    parser.add_argument('--judgements', required=False, default=JUDGMENTS_FILE_FEATURES,
                        help='The file path with the train judgements.')
    # deltr arguments
    parser.add_argument('--protected-feature', required=False, default=0,
                        help='Index of column in data that contains protected attribute.')
    parser.add_argument('--gamma', required=False, default=1,
                        help='Gamma parameter for the cost calculation in the training phase.')
    parser.add_argument('--number-of-iterations', required=False, default=10,
                        help='Number of iteration in gradient descent.')
    parser.add_argument('--learning-rate', required=False, default=0.001,
                        help='Learning rate in gradient descent.')
    parser.add_argument('--lambdaa', required=False, default=0.001,
                        help='Regularization constant.')
    parser.add_argument('--init-var', required=False, default=0.01,
                        help='Range of values for initialization of weights.')
    parser.add_argument('--standardize', required=False, default=True,
                        help='Boolean indicating whether the data should be standardized or not.')

    # add search arguments
    parser.add_argument('-q', '--query', required=False, default="Test",
                        help='The keywords to run the query on.')

    args = None
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(-1)

    if args.prepare:
        prepare(args.feature_set_file, args.feature_set_name)
    elif args.index:
        index(None, None)
    elif args.train:
        train(args.feature_set_name, args.model,
          args.judgements, args.model_file,
          args.protected_feature, args.gamma, args.number_of_iterations, args.learning_rate,
          args.lambdaa, args.init_var, args.standardize)
    elif args.search:
        search(args.index_name, args.query, args.model)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)