import re
from flask import *
from index import Song
from pprint import pprint
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList

app = Flask(__name__)

# Initialize global variables for rendering page
tmp_title = ""
tmp_artist = ""
tmp_description = ""
tmp_charts = ""
tmp_type = ""
tmp_album_name = ""
tmp_song_name = ""
tmp_category = ""
tmp_min_rank = ""
tmp_max_rank = ""
tmp_more_input = ""
gresults = {}
similar_gresults = {}


@app.route("/")
def search():
    return render_template('page_query.html')


@app.route("/results", defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/results/<page>", methods=['GET', 'POST'])
def results(page):
    global tmp_title
    global tmp_artist
    global tmp_description
    global tmp_charts
    global tmp_type
    global tmp_album_name
    global tmp_song_name
    global tmp_category
    global tmp_min_rank
    global tmp_max_rank
    global gresults

    if type(page) is not int:
        page = int(page.encode('utf-8'))
        # if the method of request is post, store query in local global variables
    # if the method of request is get, extract query contents from global variables
    if request.method == 'POST':
        title_query = request.form['title']
        artist_query = request.form['artist']
        description_query = request.form['description']
        charts_query = request.form['charts']
        type_query = request.form['type']
        album_name_query = request.form['album_name']
        song_name_query = request.form['song_name']
        category_name_query = request.form['category']
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
        tmp_type = type_query
        tmp_album_name = album_name_query
        tmp_song_name = song_name_query
        tmp_category = category_name_query
        tmp_min_rank = mintime
        tmp_max_rank = maxtime
    else:
        title_query = tmp_title
        artist_query = tmp_artist
        description_query = tmp_description
        charts_query = tmp_charts
        type_query = tmp_type
        album_name_query = tmp_album_name
        song_name_query = tmp_song_name
        category_name_query = tmp_category
        mintime = tmp_min_rank
        if tmp_min_rank > 0:
            mintime_query = tmp_min_rank
        else:
            mintime_query = ""
        maxtime = tmp_max_rank
        if tmp_max_rank < 99999:
            maxtime_query = tmp_max_rank
        else:
            maxtime_query = ""

    # store query values to display in search box while browsing
    shows = {}
    shows['title'] = title_query
    shows['artist'] = artist_query
    shows['description'] = description_query
    shows['charts'] = charts_query
    shows['type'] = type_query
    shows['album_name'] = album_name_query
    shows['song_name'] = song_name_query
    shows['category'] = category_name_query
    shows['maxtime'] = maxtime_query
    shows['mintime'] = mintime_query

    # search
    search = Song.search()

    # search for tuntime
    s = search.query('range', rank={'gte': mintime, 'lte': maxtime})

    # search for matching text query
    # if len(text_query) > 0:
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
    if len(type_query) > 0:
        s = s.query('match', type=type_query)
    if len(album_name_query) > 0:
        s = s.query('match', album_name=album_name_query)
    if len(song_name_query) > 0:
        s = s.query('match', song_name=song_name_query)
    if len(category_name_query) > 0:
        s = s.query('match', category_name_query=category_name_query)

    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('artist', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('description', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('charts', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('type', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('album_name', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('song_name', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('category', fragment_size=999999999, number_of_fragments=1)

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

            if 'type' in hit.meta.highlight:
                result['type'] = hit.meta.highlight.type[0]
            else:
                result['type'] = hit.type

            if 'album_name' in hit.meta.highlight:
                result['album_name'] = hit.meta.highlight.album_name[0]
            else:
                result['album_name'] = hit.album_name

            if 'song_name' in hit.meta.highlight:
                result['song_name'] = hit.meta.highlight.song_name[0]
            else:
                result['song_name'] = hit.song_name

            if 'category' in hit.meta.highlight:
                result['category'] = hit.meta.highlight.category[0]
            else:
                result['category'] = hit.category

        else:
            result['title'] = hit.title
            result['artist'] = hit.artist
            result['description'] = hit.description
            result['charts'] = hit.charts
            result['type'] = hit.type
            result['album_name'] = hit.album_name
            result['song_name'] = hit.song_name
            result['category'] = hit.category
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


@app.route("/results/more", defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/results/more/<page>", methods=['GET', 'POST'])
def results_more(page):
    global tmp_more_input

    if type(page) is not int:
        page = int(page.encode('utf-8'))

    if request.method == 'POST':
        more_input_query = request.form['more'].split("_/_")[0]
        more_id = request.form['more'].split("_/_")[1]
        tmp_more_input = more_input_query
        print more_input_query
        print more_id
        print type(more_id)
    else:
        more_input_query = tmp_more_input

    shows = {}
    shows['title'] = ''
    shows['artist'] = ''
    shows['description'] = ''
    shows['charts'] = ''
    shows['type'] = ''
    shows['album_name_query'] = ''
    shows['song_name_query'] = ''
    shows['category'] = ''
    shows['maxtime'] = ''
    shows['mintime'] = ''

    s_more = Song.search()

    s_more = s_more.query('more_like_this', fields=['description'],
                like={
                    "_index": "song_index",
                    "_type": "song",
                    "_id": more_id}
                )

    start = 0 + (page - 1) * 10
    end = 10 + (page - 1) * 10

    response = s_more[start:end].execute()

    resultList = {}
    for hit in response.hits:
        result = {}
        result['score'] = hit.meta.score
        result['title'] = hit.title
        result['artist'] = hit.artist
        result['description'] = hit.description
        result['charts'] = hit.charts
        result['type'] = hit.type
        result['album_name'] = hit.album_name
        result['song_name'] = hit.song_name
        result['category'] = hit.category
        resultList[hit.meta.id] = result

    gresults = resultList

    result_num = response.hits.total

    if result_num > 0:
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows)
    else:
        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows)


@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    print res
    print res.encode('utf-8')
    songf = gresults[res.encode('utf-8')]
    songftitle = songf['title']
    for term in songf:
        if type(songf[term]) is AttrList:
            s = "\n"
            for item in songf[term]:
                s += item + ",\n "
            songf[term] = s
    song = Song.get(id=res, index='song_index')
    songfdic = song.to_dict()
    songf['rank'] = str(songfdic['rank']) + " min"
    return render_template('page_targetArticle.html', songf=songf, title=songftitle)

@app.route("/similar_documents/<res>", methods=['GET'])
def similar_documents(res):
    global similar_gresults
    songf = similar_gresults[res.encode('utf-8')]
    songftitle = songf['title']
    for term in songf:
        if type(songf[term]) is AttrList:
            s = "\n"
            for item in songf[term]:
                s += item + ",\n "
            songf[term] = s
    song = Song.get(id=res, index='song_index')
    songfdic = song.to_dict()
    songf['rank'] = str(songfdic['rank']) + " min"
    return render_template('page_targetArticle.html', songf=songf, title=songftitle)


if __name__ == "__main__":
    app.run()
