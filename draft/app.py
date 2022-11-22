from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import random
import search_helper
import insert

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/insert/', methods = ['GET','POST'])
def insert_post():
    if request.method == 'GET':
        #returns a blank form
        return render_template('insert_post.html')
    else:
        #process the form
        conn = dbi.connect()
        user_id = int(request.form['user_id'])
        title = request.form['title']
        description = request.form['description']
        item_photo = None #feature to be implemented
        item_type = request.form['item_type']
        item_id = insert.add_item(conn, description, item_photo, item_type)
        insert.add_post(conn,user_id,item_id,title)
        search_results = [insert.new_post_details(conn)]
        print(search_results)
        flash('Post created successfully')
        return render_template('search_results.html', results=search_results)

@app.route('/feed/', methods=['GET'])
def feed():
    conn = dbi.connect()
    feed_results = search_helper.feed(conn)
    #print(feed_results)
    post_author = feed_results[0]['name']
    #user_id = feed_results.user_id
    #not working yet
    #post_author = search_helper.get_author(user_id) n
    return render_template('feed.html', posts=feed_results, author = post_author)

@app.route('/post/<post_id>', methods=['GET'])
def post_details(post_id):
    conn = dbi.connect()
    search_results = [search_helper.search_by_postid(conn, post_id)]
    return render_template('search_results.html', results=search_results)

@app.route('/search/', methods = ['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    if request.method == 'POST':
        conn = dbi.connect()
        # get the search/filter term
        search_term = request.form.get('search-term')

        # depending on whether searching or filtering, 
        # use appropriate function to get results
        search_results = []
        if request.form.get('submit-btn') == 'search!':
            search_results = search_helper.search(conn, search_term)
        elif request.form.get('submit-btn') == 'filter!':
            print('want to filter')
            #print('search term ', search_term)
            search_results = search_helper.filter(conn, search_term)
            print('results', search_results)
        if len(search_results) > 0:
            return render_template('search_results.html', results=search_results)
        else: 
            flash('No results found.')
            return redirect( url_for('search') )

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/formecho/', methods=['GET','POST'])
def formecho():
    if request.method == 'GET':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.args)
    elif request.method == 'POST':
        return render_template('form_data.html',
                               method=request.method,
                               form_data=request.form)
    else:
        # maybe PUT?
        return render_template('form_data.html',
                               method=request.method,
                               form_data={})

@app.route('/testform/')
def testform():
    # these forms go to the formecho route
    return render_template('testform.html')


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    # set this local variable to 'wmdb' or your personal or team db
    db_to_use = 'sunshare_db' 
    dbi.use(db_to_use)
    print('will connect to {}'.format(db_to_use))

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
