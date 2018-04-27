import json
import re
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, DocType, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer
from elasticsearch_dsl.query import MultiMatch, Match

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Establish elasticsearch
es = Elasticsearch()

# Define analyzers
my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase', 'stop'])


# --- Add more analyzers here ---

# Define document mapping
# You can use existed analyzers or use ones you define yourself as above
class Song(DocType):
    title = Text(analyzer='standard')
    artist = Text(analyzer='standard')
    description = Text(analyzer='standard')
    charts = Text(analyzer='standard')
    type = Text(analyzer='standard')
    image_link = Text()
    album_name = Text(analyzer='standard')
    song_name = Text(analyzer='standard')
    category = Text(analyzer='standard')
    rank = Integer()

    # --- Add more fields here ---

    class Meta:
        index = 'song_index'
        doc_type = 'song'

    def save(self, *args, **kwargs):
        return super(Song, self).save(*args, **kwargs)


# Populate the index
def buildIndex():
    song_index = Index('song_index')
    if song_index.exists():
        song_index.delete()  # Overwrite any previous version
    song_index.doc_type(Song)  # Set doc_type to Movie
    song_index.create()

    # Open the json film corpus
    with open('data_v2.json') as data_file:
        songs = json.load(data_file)
        size = len(songs)

    # Action series for bulk loading
    actions = [
        {
            "_index": "song_index",
            "_type": "song",
            "_id": mid,
            "title": songs[str(mid)]['title'],
            "artist": songs[str(mid)]['artist'],
            "description": songs[str(mid)]['description'],
            "charts": songs[str(mid)]['charts'],
            "type": songs[str(mid)]['type'],
            "image_link": songs[str(mid)]['image_link'],
            "album_name": songs[str(mid)]['album_name'],
            "song_name": songs[str(mid)]['song_name'],
            "category": songs[str(mid)]['category'],
            "rank": songs[str(mid)]['rank']  # movies[str(mid)]['runtime'] # You would like to convert runtime to integer (in minutes)
            # --- Add more fields here ---
        }
        for mid in range(1, size + 1)
    ]

    helpers.bulk(es, actions)


def main():
    start_time = time.time()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()