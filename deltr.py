import argparse
import sys

from index import create_document_list, reindex
from prepare import load_features, init_default_store
from search import ltr_query
from train import save_model, train_model, collect_train_data
from utils import Logger, elastic_connection, FEATURE_SET_FILE, JUDGMENTS_FILE, QUERIES_FILE, \
    FEATURE_SET_NAME, MODEL_FILE, INDEX_NAME, DOCUMENT_DIR, MODEL_NAME, FEATURES_FILE, TRAIN_LOG_FILE


def index(index_name, document_dir):
    """
    Index the data
    :param index_name:          Name of the created index
    :param document_dir:        Path to the directory containing the JSONs to be uploaded. Each JSON :must: have an "id".
    :return:
    """
    es = elastic_connection(timeout=30)
    reindex(es, document_list=create_document_list(document_dir), index=index_name)


def prepare(feature_set_file, feature_set_name):
    """
    Upload the feature set
    :param feature_set_file:        The file path to the feature set JSON definition
    :param feature_set_name:        The name of the feature set
    :return:
    """
    init_default_store()
    load_features(feature_set_file, feature_set_name)


def train(feature_set_name: str, model_name: str, queries_file: str, judgments_file: str, index_name:str,
          features_file: str, model_output: str,
          protected_feature_name="1", gamma=1, number_of_iterations=3000, learning_rate=0.001,
          lambdaa=0.001, init_var=0.01, standardize=False, log=None):
    """
    Train and upload model with specified parameters
    """
    es = elastic_connection(timeout=1000)
    collect_train_data(es, queries_file, judgments_file, feature_set_name, index_name, features_file)
    train_model(features_file, model_output, protected_feature_name, gamma,
                number_of_iterations, learning_rate, lambdaa, init_var, standardize, log)

    save_model(model_name, feature_set_name, model_output)


def search(index_name, query, model, verbose):
    """
    Peforms a search request on Elasticseach using LTR and a specified (DELTR) model
    :param index_name:      The index to search on
    :param query:           The query to search by
    :param model:           The model to search with
    :param verbose:         Whether or not the output should contain the weights
    :return:
    """
    es = elastic_connection(timeout=1000)
    results = es.search(index=index_name, body=ltr_query(query, model))
    for result in results['hits']['hits']:
        message = result['_source']['id']
        if verbose:
            features = result['fields']['_ltrlog'][0]['log_entry']
            message += ' ' + ' '.join(['{0}:{1}'.format(ll['name'], ll['value']) for ll in features])
        Logger.logger.info(message)


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
                        help='The name of the index to create, train a model or run a query on.')
    parser.add_argument('--document-dir', required=False, default=DOCUMENT_DIR,
                        help='The directory with documents to index.')

    # add train arguments
    parser.add_argument('--model', required=False, default=MODEL_NAME,
                        help='The name of the model.')  # this is used in the search phase as well
    parser.add_argument('--model-file', required=False, default=MODEL_FILE,
                        help='The file path where the model will be stored.')
    parser.add_argument('--features-log-file', required=False, default=FEATURES_FILE,
                        help='The file path where the features will be logged.')
    parser.add_argument('--queries', required=False, default=QUERIES_FILE,
                        help='The file path with the queries.')
    parser.add_argument('--judgements', required=False, default=JUDGMENTS_FILE,
                        help='The file path with the train judgements.')

    parser.add_argument('--log', required=False, default=TRAIN_LOG_FILE,
                        help='The name of the file to store the train log to.')

    # deltr arguments
    parser.add_argument('--protected-feature', required=False, default="1",
                        help='Name of the feature that contains protected attribute.')
    parser.add_argument('--gamma', required=False, type=float, default=1,
                        help='Gamma parameter for the cost calculation in the training phase.')
    parser.add_argument('--number-of-iterations', required=False, type=int, default=10,
                        help='Number of iteration in gradient descent.')
    parser.add_argument('--learning-rate', required=False, type=float, default=0.001,
                        help='Learning rate in gradient descent.')
    parser.add_argument('--lambdaa', required=False, type=float, default=0.001,
                        help='Regularization constant.')
    parser.add_argument('--init-var', required=False, type=float, default=0.01,
                        help='Range of values for initialization of weights.')
    parser.add_argument('--standardize', required=False, type=bool, default=True,
                        help='Boolean indicating whether the data should be standardized or not.')

    # add search arguments
    parser.add_argument('-q', '--query', required=False, default="Test",
                        help='The keywords to run the query on.')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Show verbose output in search')


    # parse the arguments
    args = None
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(-1)

    # run a command based on the arguments
    if args.prepare:
        prepare(args.feature_set_file, args.feature_set_name)
    elif args.index:
        index(args.index_name, args.document_dir)
    elif args.train:
        train(args.feature_set_name, args.model, args.queries,
              args.judgements, args.index_name, args.features_log_file,
              args.model_file,
              args.protected_feature, args.gamma, args.number_of_iterations, args.learning_rate,
              args.lambdaa, args.init_var, args.standardize, args.log)
    elif args.search:
        verbose = True if args.verbose else False
        search(args.index_name, args.query, args.model, verbose)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
