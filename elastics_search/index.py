import json
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, DocType, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import analyzer, token_filter, char_filter
from elastic_search.search_helper import runtime_str2int, list2str


# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Establish elasticsearch
es = Elasticsearch()

# Define analyzers
stop = token_filter(name_or_instance='stop', type='stop', stopwords='_english_')  # filter to remove stopwords
punct = char_filter(name_or_instance='punc', type='mapping', mappings=[", => ' '"])  # change ',' to space

text_analyzer = analyzer(name_or_instance='custom',
                       tokenizer='standard',
                       char_filter=['html_strip'],
                       filter=['lowercase', stop, "porter_stem"])  # for text field without phrase
quote_analyzer = analyzer(name_or_instance='custom',
                          tokenizer='standard',
                          filter=['lowercase', 'porter_stem'])  # for text field with phrases
name_analyzer = analyzer(name_or_instance='custom',
                           char_filter=[punct],
                           tokenizer='whitespace',
                           filter=['lowercase'])
# --- Add more analyzers here ---


# Define document mapping
# You can use existed analyzers or use ones you define yourself as above
# class Movie(DocType):
#     title = Text(analyzer=quote_analyzer, search_analyzer=text_analyzer, search_quote_analyzer=quote_analyzer, boost=2.)
#     # set a boost for query term on title field
#     text = Text(analyzer=quote_analyzer, search_analyzer=text_analyzer,  search_quote_analyzer=quote_analyzer)
#     starring = Text(analyzer=name_analyzer)
#     director = Text(analyzer=name_analyzer)
#     language = Text(analyzer='standard')
#     country = Text(analyzer="standard")
#     categories = Text(analyzer='standard')
#     location = Text(analyzer="standard")
#     time = Text(analyzer='keyword')
#     runtime = Integer()
#
#     # --- Add more fields here ---
#
#     class Meta:
#         index = 'sample_film_index'
#         doc_type = 'movie'
#
#     def save(self, *args, **kwargs):
#         return super(Movie, self).save(*args, **kwargs)


class Song(DocType):
    text = Text(analyzer='standard')
    title = Text(analyzer='standard')
    description = Text(analyzer='standard')
    type = Text(analyzer='standard')
    song_name = Text(analyzer='standard')
    album_name = Text(analyzer='standard')
    artist = Text(analyzer="standard")
    category = Text(analyzer='standard')
    image_link = Text(analyzer="standard")
    charts = Text(analyzer="standard")
    rank = Text(analyzer="standard")

    # --- Add more fields here ---

    class Meta:
        index = 'song_index'
        doc_type = 'song'

    def save(self, *args, **kwargs):
        return super(Song, self).save(*args, **kwargs)
# Populate the index
# def buildIndex():
#     film_index = Index('sample_film_index')
#     if film_index.exists():
#         film_index.delete()  # Overwrite any previous version
#     film_index.doc_type(Movie)  # Set doc_type to Movie
#     film_index.create()
#
#     # Open the json film corpus
#     with open('films_corpus.json') as data_file:
#         movies = json.load(data_file)
#         size = len(movies)
#
#     # Action series for bulk loading
#     actions = [
#         {
#             "_index": "sample_film_index",
#             "_type": "movie",
#             "_id": mid,
#             "title": movies[str(mid)]['title'],
#             "text": movies[str(mid)]['text'],
#             "starring": list2str(movies[str(mid)]['starring']),
#             "runtime": runtime_str2int(movies[str(mid)]['runtime']),
#             "language": list2str(movies[str(mid)]['language']),
#             "country": list2str(movies[str(mid)]['country']),
#             "director": list2str(movies[str(mid)]['director']),
#             "location": movies[str(mid)]['location'],
#             "time": movies[str(mid)]['time'],
#             "categories": movies[str(mid)]['categories'],
#         }
#         for mid in range(1, size+1)
#     ]
#
#     helpers.bulk(es, actions)


def buildIndex():
    song_index = Index('song_index')
    if song_index.exists():
        song_index.delete()  # Overwrite any previous version
    song_index.doc_type(Song)  # Set doc_type to Movie
    song_index.create()

    # Open the json film corpus
    with open('./data/data_v3.json') as data_file:
        songs = json.load(data_file)
        size = len(songs)

    # Action series for bulk loading
    actions = [
        {
            "_index": "song_index",
            "_type": "song",
            "_id": mid,
            "title": songs[str(mid)]['title'],
            "description": songs[str(mid)]['description'],
            "type": songs[str(mid)]['type'],
            "song_name": songs[str(mid)]['song_name'],
            "album_name": (songs[str(mid)]['album_name']),
            "artist": (songs[str(mid)]['artist']),
            "rank": (songs[str(mid)]['rank']),
            "charts": songs[str(mid)]['charts'],
            "image_link": songs[str(mid)]['image_link'],
            "category": list2str(songs[str(mid)]['category']),
        }
        for mid in range(1, size + 1)
    ]

    helpers.bulk(es, actions)


def main():
    start_time = time.time()
    buildIndex()
    print("=== Built song index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()   