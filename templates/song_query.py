import re
import song_index
from flask import *
from song_index import Song
from pprint import pprint
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList

app = Flask(__name__)

# Initialize global variables for rendering page
# tmp_text = ""
# tmp_title = ""
# tmp_star = ""
# tmp_min = ""
# tmp_max = ""
# gresults = {}

tmp_title = ""
tmp_artist = ""
tmp_description = ""
tmp_charts = ""
tmp_min_year = ""
tmp_max_year = ""
gresults = {}


@app.route("/")
def search():
    return render_template('page_query.html')


@app.route("/results", defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/results/<page>", methods=['GET', 'POST'])
def results(page):
    # global tmp_text
    # global tmp_title
    # global tmp_star
    # global tmp_min
    # global tmp_max
    # global gresults

    global tmp_title
    global tmp_artist
    global tmp_description
    global tmp_charts
    global tmp_min_year
    global tmp_max_year
    global gresults

    if type(page) is not int:
        page = int(page.encode('utf-8'))
        # if the method of request is post, store query in local global variables
    # if the method of request is get, extract query contents from global variables
    if request.method == 'POST':
        title_query = request.form['title']
        artist_query = request.form['artist']
        description_query = request.form['query']
        charts_query = request.form['charts']
        mintime_query = request.form['mintime']
        if len(mintime_query) is 0:
            mintime = 0
        else:
            mintime = int(mintime_query)
        maxtime_query = request.form['maxtime']
        if len(maxtime_query) is 0:
            maxtime = 99999
        else:
            maxtime = int(maxtime_query)

        # update global variable template date
        tmp_title = title_query
        tmp_artist = artist_query
        tmp_description = description_query
        tmp_charts = charts_query
        tmp_min_year = mintime
        tmp_max_year = maxtime
    else:
        title_query = tmp_title
        artist_query = tmp_artist
        description_query = tmp_description
        charts_query = tmp_charts
        mintime = tmp_min
        if tmp_min_year > 0:
            mintime_query = tmp_min_year
        else:
            mintime_query = ""
        maxtime = tmp_max_year
        if tmp_max_year < 99999:
            maxtime_query = tmp_max_year
        else:
            maxtime_query = ""

    # store query values to display in search box while browsing
    shows = {}
    shows['title'] = title_query
    shows['artist'] = artist_query
    shows['description'] = description_query
    shows['charts'] = charts_query
    shows['maxtime'] = maxtime_query
    shows['mintime'] = mintime_query

    # search
    search = Song.search()

    # search for tuntime
    s = search.query('range', runtime={'gte': mintime, 'lte': maxtime})

    # search for matching text query
    # if len(description_query) > 0:
    #     s = s.query('multi_match', query=text_query, type='cross_fields', fields=['title', 'text'], operator='and')

    # search for matching stars
    # You should support multiple values (list)
    if len(title_query) > 0:
        s = s.query('match', title=title_query)

    if len(artist_query) > 0:
        s = s.query('match', artist=artist_query)

    if len(description_query) > 0:
        s = s.query('match', description=description_query)

    if len(charts_query) > 0:
        s = s.query('match', charts=charts_query)

    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('artist', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('description', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('charts', fragment_size=999999999, number_of_fragments=1)

    # extract data for current page
    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

    # execute search
    response = s[start:end].execute()

    # insert data into response
    resultList = {}
    for hit in response.hits:
        result = {}
        result['score'] = hit.meta.score

        if 'highlight' in hit.meta:
            if 'title' in hit.meta.highlight:
                result['title'] = hit.meta.highlight.title[0]
            else:
                result['title'] = hit.title

            if 'artist' in hit.meta.highlight:
                result['artist'] = hit.meta.highlight.artist[0]
            else:
                result['artist'] = hit.artist

            if 'description' in hit.meta.highlight:
                result['description'] = hit.meta.highlight.description[0]
            else:
                result['description'] = hit.description

            if 'charts' in hit.meta.highlight:
                result['charts'] = hit.meta.highlight.charts[0]
            else:
                result['charts'] = hit.charts

        else:
            result['title'] = hit.title
            result['artist'] = hit.artist
            result['description'] = hit.description
            result['charts'] = hit.charts
        resultList[hit.meta.id] = result

    gresults = resultList

    # get the number of results
    result_num = response.hits.total

    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows)
    else:
        message = []
        if len(title_query) > 0:
            message.append('Cannot find title: ' + title_query)
        if len(artist_query) > 0:
            message.append('Cannot find artist: ' + artist_query)
        if len(description_query) > 0:
            message.append('Cannot find description term: ' + description_query)
        if len(charts_query) > 0:
            message.append('Cannot find charts: ' + charts_query)

        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows)


@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    song = gresults[res.encode('utf-8')]
    songtitle = song['title']
    for term in song:
        if type(song[term]) is AttrList:
            s = "\n"
            for item in song[term]:
                s += item + ",\n "
            song[term] = s
    song = Song.get(id=res, index='song_index')
    songdic = song.to_dict()
    song['runtime'] = str(songdic['runtime']) + " min"
    return render_template('page_targetArticle.html', song=song, title=songtitle)


if __name__ == "__main__":
    app.run()
