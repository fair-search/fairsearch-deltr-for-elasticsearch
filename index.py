import json
import elasticsearch.helpers

from os import listdir
from os.path import isfile, join

from utils import Logger, elastic_connection, INDEX_NAME, DOCUMENT_DIR


def create_document_list(document_dir=DOCUMENT_DIR):
    """ returns a list of JSON files in the directory """

    for f in listdir(document_dir):
        if isfile(join(document_dir, f)) and f.endswith(".json"):
            try:
                with open(join(document_dir, f)) as f_json:
                    yield json.load(f_json)
            except Exception as e:
                Logger.logger.info("Failed to parse %s due to %s" % (f, str(e)))
                continue


def reindex(es_connection, analysis_settings=None, mapping_settings=None, document_list=None, index=INDEX_NAME):
    if document_list is None:
        document_list = {}
    if mapping_settings is None:
        mapping_settings = {}
    if analysis_settings is None:
        analysis_settings = {}

    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "index": {
                "analysis": analysis_settings,
            }}}

    if mapping_settings:
        settings['mappings'] = mapping_settings  # C

    es_connection.indices.delete(index, ignore=[400, 404])
    es_connection.indices.create(index, body=settings)

    elasticsearch.helpers.bulk(es, bulk_docs(document_list, index))


def bulk_docs(document_list, index):
    """ bulk index the documents """
    for document in document_list:
        add_cmd = {"_index": index,  # E
                   "_id": document.get("id", None),
                   "_type": "_doc",
                   "_source": document}
        yield add_cmd
        if 'id' in document:
            Logger.logger.info("%s added to %s" % (document['id'].encode('utf-8'), index))


if __name__ == "__main__":
    es = elastic_connection(timeout=30)
    reindex(es, document_list=create_document_list(DOCUMENT_DIR))
