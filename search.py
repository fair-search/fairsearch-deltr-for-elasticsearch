from utils import Logger, elastic_connection, INDEX_NAME, MODEL_NAME

baseQuery = {
    "query": {
        "multi_match": {
            "query": "w3c",
        }
    },
    "rescore": {
        "query": {
            "rescore_query": {
                "sltr": {
                    "params": {
                        "keywords": ""
                    },
                    "model": "",
                }
            }
        },
    },
    "ext": {
        "ltr_log": {
            "log_specs": {
                "name": "log_entry",
                "rescore_index": 0,
                "missing_as_zero": True
            }
        }
    }
}


def ltr_query(keywords, model_name):
    import json
    baseQuery['rescore']['query']['rescore_query']['sltr']['model'] = model_name
    baseQuery['query']['multi_match']['query'] = keywords
    baseQuery['rescore']['query']['rescore_query']['sltr']['params']['keywords'] = keywords
    Logger.logger.info("%s" % json.dumps(baseQuery))
    return baseQuery


if __name__ == "__main__":
    from sys import argv

    es = elastic_connection(timeout=1000)
    model = MODEL_NAME
    if len(argv) > 2:
        model = argv[2]
    results = es.search(index=INDEX_NAME, body=ltr_query(argv[1], model))
    for result in results['hits']['hits']:
        Logger.logger.info(result['_source']['name'])
