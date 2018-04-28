from flask import *
from elastic_search.index import Song
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
tmp_rank = ""
gresults = {}


@app.route("/")
def search():
    return render_template('page_query.html')


@app.route("/results", defaults={'page': 1}, methods=['GET','POST'])
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
    global tmp_rank
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
        rank_query = request.form['rank']

        # update global variable template date
        tmp_title = title_query
        tmp_artist = artist_query
        tmp_description = description_query
        tmp_charts = charts_query
        tmp_type = type_query
        tmp_album_name = album_name_query
        tmp_song_name = song_name_query
        tmp_category = category_name_query
        tmp_rank = rank_query
    else:
        title_query = tmp_title
        artist_query = tmp_artist
        description_query = tmp_description
        charts_query = tmp_charts
        type_query = tmp_type
        album_name_query = tmp_album_name
        song_name_query = tmp_song_name
        category_name_query = tmp_category
        rank_query = tmp_rank
    
    # store query values to display in search box while browsing
    shows = dict()
    shows['title'] = title_query
    shows['artist'] = artist_query
    shows['description'] = description_query
    shows['charts'] = charts_query
    shows['type'] = type_query
    shows['album_name'] = album_name_query
    shows['song_name'] = song_name_query
    shows['category'] = category_name_query
    shows['rank'] = rank_query

    # --------------------------- search queries --------------------------------
    s = Song.search()
    
    # search for runtime
    # q = Q('range', runtime={'gte': mintime, 'lte': maxtime})
    # s = search.query(q)
    
    # search for matching text query
    # if len(text_query) > 0:
    #     # try to match all terms in the query
    #     quote = Q('query_string', query=text_query, type='most_fields', fields=['title', 'text'], default_operator='AND', minimum_should_match=1)
    #     s = s.query(quote)
    #
    # # search for matching starring
    # if len(star_query) > 0:
    #     q = Q('fuzzy', starring={'value': star_query, 'transpositions': True})
    #     # people cannot remember clearly about the names of starrings
    #     s = s.query(q)
    #
    # # search for matching director
    # if len(direct_query) > 0:
    #     q = Q('match', director={'query': direct_query, 'operator': 'and'})
    #     s = s.query(q)
    #
    # # search for matching language
    # if len(lang_query) > 0:
    #     q = Q('match', language=lang_query)
    #     s = s.query(q)
    #
    # # search for matching country
    # if len(country_query) > 0:
    #     q = Q('match', country=country_query)
    #     s = s.query(q)
    #
    # # search for matching location
    # if len(locat_query) > 0:
    #     q = Q('match', location=locat_query)
    #     s = s.query(q)
    #
    # # search for matching categories
    # if len(cat_query) > 0:
    #     q = Q('match', categories={"query": cat_query, "cutoff_frequency": 0.01})
    #     s = s.query(q)
    #
    # # search for matching time
    # if len(time_query) > 0:
    #     # we want the query to be exactly the same with the term in the index
    #     q = Q('term', time=time_query)
    #     s = s.query(q)

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
        s = s.query('match', category=category_name_query)
    if len(rank_query) > 0:
        s = s.query('match', rank=rank_query)

    # --------------------------- search queries (end) --------------------------------

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
    start = 0 + (page-1)*10
    end = 10 + (page-1)*10
    
    # execute search
    response = s[start:end].execute()
    warning = None

    # if response.hits.total < 1:
    #     # in some cases, this will happen when system cannot match all the terms in the text fields
    #     # so we restart the search process and make the query disjunctive for text field
    #
    #     # --------------------------- search queries --------------------------------
    #     search = Movie.search()
    #
    #     # search for runtime
    #     q = Q('range', runtime={'gte': mintime, 'lte': maxtime})
    #     s = search.query(q)
    #
    #     # search for matching text query
    #     if len(text_query) > 0:
    #         quote2 = Q('query_string', query=text_query, fields=['title', 'text'], type='most_fields', default_operator='OR', minimum_should_match=1)
    #         s = s.query(quote2)
    #
    #         # search for matching starring
    #     if len(star_query) > 0:
    #         q = Q('fuzzy', starring={'value': star_query, 'transpositions': True})
    #         # people cannot remember clearly about the names of starrings
    #         s = s.query(q)
    #
    #     # search for matching director
    #     if len(direct_query) > 0:
    #         q = Q('match', director={'query': direct_query, 'operator': 'and'})
    #         s = s.query(q)
    #
    #     # search for matching language
    #     if len(lang_query) > 0:
    #         q = Q('match', language=lang_query)
    #         s = s.query(q)
    #
    #     # search for matching country
    #     if len(country_query) > 0:
    #         q = Q('match', country=country_query)
    #         s = s.query(q)
    #
    #     # search for matching location
    #     if len(locat_query) > 0:
    #         q = Q('match', location=locat_query)
    #         s = s.query(q)
    #
    #     # search for matching categories
    #     if len(cat_query) > 0:
    #         q = Q('match', categories={"query": cat_query, "cutoff_frequency": 0.01})
    #         s = s.query(q)
    #
    #     # search for matching time
    #     if len(time_query) > 0:
    #         q = Q('term', time=time_query)
    #         s = s.query(q)
    #     # --------------------------- search queries (end) --------------------------------
    #
    #     # highlight
    #     s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    #     s = s.highlight('text', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('starring', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('director', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('time', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('language', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('location', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('categories', fragment_size=999999999, number_of_fragments=1)
    #     s = s.highlight('country', fragment_size=999999999, number_of_fragments=1)
    #
    #     warning = 'cannot find all the terms!'
    #     response = s[start:end].execute()

    # insert data into response
    resultList = {}
    # for hit in response.hits:
    #     result = dict()
    #     result['score'] = hit.meta.score
    #
    #     if 'highlight' in hit.meta:
    #         # highlight specific fields
    #         if 'title' in hit.meta.highlight:
    #             result['title'] = hit.meta.highlight.title[0]
    #         else:
    #             result['title'] = hit.title
    #
    #         if 'text' in hit.meta.highlight:
    #             result['text'] = hit.meta.highlight.text[0]
    #         else:
    #             result['text'] = hit.text
    #         if 'starring' in hit.meta.highlight:
    #             result['starring'] = hit.meta.highlight.starring[0]
    #         else:
    #             result['starring'] = hit.starring
    #         if 'director' in hit.meta.highlight:
    #             result['director'] = hit.meta.highlight.director[0]
    #         else:
    #             result['director'] = hit.director
    #         if 'time' in hit.meta.highlight:
    #             result['time'] = hit.meta.highlight.time[0]
    #         else:
    #             result['time'] = hit.country
    #         if 'country' in hit.meta.highlight:
    #             result['country'] = hit.meta.highlight.country[0]
    #         else:
    #             result['country'] = hit.country
    #         if 'language' in hit.meta.highlight:
    #             result['language'] = hit.meta.highlight.language[0]
    #         else:
    #             result['language'] = hit.language
    #         if 'location' in hit.meta.highlight:
    #             result['location'] = hit.meta.highlight.location[0]
    #         else:
    #             result['location'] = hit.location
    #         if 'categories' in hit.meta.highlight:
    #             result['categories'] = hit.meta.highlight.categories[0]
    #         else:
    #             result['categories'] = hit.categories
    #     else:
    #         result['title'] = hit.title
    #         result['text'] = hit.text
    #         result['starring'] = hit.starring
    #         result['director'] = hit.director
    #         result['time'] = hit.time
    #         result['country'] = hit.country
    #         result['language'] = hit.language
    #         result['location'] = hit.location
    #         result['categories'] = hit.categories
    #
    #     resultList[hit.meta.id] = result

    for hit in response.hits:
        result = dict()
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
        return render_template('page_SERP.html', results=resultList, res_num=result_num, page_num=page, queries=shows, warning=warning)
    else:
        warning = None
        message = []
        message.append('cannot find term!')
        # if len(text_query) > 0:
        #     message.append('Unknown search term: '+text_query)
        # if len(star_query) > 0:
        #     message.append('Cannot find star: '+star_query)
        # if len(lang_query) > 0:
        #     message.append('Cannot find language: '+lang_query)
        # if len(locat_query) > 0:
        #     message.append('Cannot find location: '+locat_query)
        # if len(direct_query) > 0:
        #     message.append('Cannot find director: '+direct_query)
        # if len(country_query) > 0:
        #     message.append('Cannot find country: '+country_query)
        # if len(time_query) > 0:
        #     message.append('Cannot find time: '+time_query)
        # if len(cat_query) > 0:
        #     message.append('Cannot find category: '+cat_query)
        # if len(maxtime_query) > 0 or len(mintime_query) > 0:
        #     message.append('runtime doesn\'t match')
        return render_template('page_SERP.html', results=message, res_num=result_num, page_num=page, queries=shows, warning=warning)


@app.route("/more", defaults={'page': 1}, methods=['GET','POST'])
@app.route("/more/<page>", methods=['GET','POST'])
def more_like_this(page):
    global tmp_title
    global tmp_artist
    global tmp_description
    global tmp_charts
    global tmp_type
    global tmp_album_name
    global tmp_song_name
    global tmp_category
    global tmp_rank
    global gresults

    if type(page) is not int:
        page = int(page.encode('utf-8'))
    if request.method == 'POST':
        category_name_query = request.form['more']
        tmp_category = category_name_query
    else:
        category_name_query = tmp_category
    title_query = ''
    artist_query = ''
    description_query = ''
    charts_query = ''
    type_query = ''
    album_name_query = ''
    song_name_query = ''
    rank_query = ''

    # store query values to display in search box while browsing
    shows = dict()
    shows['title'] = title_query
    shows['artist'] = artist_query
    shows['description'] = description_query
    shows['charts'] = charts_query
    shows['type'] = type_query
    shows['album_name'] = album_name_query
    shows['song_name'] = song_name_query
    shows['category'] = category_name_query
    shows['rank'] = rank_query
    global gresults

    # --------------------------- search queries --------------------------------
    s = Song.search()

    if len(category_name_query) > 0:
        s = s.query('match', category=category_name_query)

    # --------------------------- search queries (end) --------------------------------

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
    warning = None

    resultList = {}

    for hit in response.hits:
        result = dict()
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
        print(len(resultList))
        return render_template('page_more_like_this.html', results=resultList, res_num=result_num, page_num=page, queries=shows,
                               warning=warning)
    else:
        warning = None
        message = []
        message.append('cannot find term!')
        return render_template('page_more_like_this.html', results=message, res_num=result_num, page_num=page, queries=shows,
                               warning=warning)


@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    song = gresults[res]
    song_title = song['title']
    for term in song:
        if type(song[term]) is AttrList:
            s = "\n"
            for item in song[term]:
                s += item.strip() + "\n"
            song[term] = s
    song1 = Song.get(id=res, index='song_index')
    song_dic = song1.to_dict()
    song['category'] = song_dic['category']
    return render_template('page_targetArticle.html', song=song, title=song_title)


if __name__ == "__main__":
    # app.run()
    app.run(debug=True, port=65013)
