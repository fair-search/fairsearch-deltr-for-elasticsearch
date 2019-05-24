import json
import elasticsearch.helpers

from utils import Logger, elastic_connection, INDEX_NAME


def reindex(es_connection, analysis_settings=None, mapping_settings=None, movie_dict=None, index=INDEX_NAME):
    if movie_dict is None:
        movie_dict = {}
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

    elasticsearch.helpers.bulk(es, bulk_docs(movie_dict, index))


def bulk_docs(movie_dict, index):
    for movie_id, movie in movie_dict.items():
        if 'release_date' in movie and movie['release_date'] == "":
            del movie['release_date']
        add_cmd = {"_index": index,  # E
                   "_id": movie_id,
                   "_source": movie}
        yield add_cmd
        if 'title' in movie:
            Logger.logger.info("%s added to %s" % (movie['title'].encode('utf-8'), index))


if __name__ == "__main__":
    es = elastic_connection(timeout=30)
    tmdb_movie_dict = json.loads(open('tmdb.json').read())
    reindex(es, movie_dict=tmdb_movie_dict)
