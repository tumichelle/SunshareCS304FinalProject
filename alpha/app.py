# alpha version
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import sys, os, random
import imghdr
import search_helper
import insert
import cs304login

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

#main page on startup
@app.route('/')
def index():
    return render_template('main.html')

#Shows example feed for visiting without an account
@app.route('/example_feed/', methods = ['POST'])
def example_feed():
    conn = dbi.connect()
    zipcode = request.form['zipcode']
    filtered = search_helper.filter_zip(conn, zipcode)
    if len(filtered) == 0:
        flash('There are no posts in your area')
        return render_template('main.html')
    return render_template('example_feed.html', posts = filtered)

#page to sign in with existing account
@app.route('/login_page/')
def login_page():
    return render_template('login_page.html')

#join and create a new account
@app.route('/signup_page/')
def signup_page():
    return render_template('signup_page.html')

@app.route('/pic/<item_id>')
def pic(item_id):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from picfile where item_id = %s''',
        [item_id])
    if numrows == 0:
        flash('No picture for {}'.format(item_id))
        return redirect(url_for('index'))
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])

#Insert form that takes in the post info and creates a new post and a new item
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
        item_type = request.form['item_type']
        item_photo = request.files['item_photo'] #feature to be implemented
        item_id = insert.add_item(conn, description, item_photo, item_type)
        insert.add_post(conn,user_id,item_id,title)
        search_results = [insert.new_post_details(conn)]
        print(search_results)
        flash('Post created successfully')

        user_filename = item_photo.filename
        ext = user_filename.split('.')[-1]
        filename = secure_filename('{}.{}'.format(item_id,ext))
        pathname = os.path.join(app.config['UPLOADS'],filename)
        item_photo.save(pathname)
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute(
            '''
            insert into picfile(item_id, filename) values (%s, %s)
            on duplicate key update filename = %s
            ''', [item_id, filename, filename]
        )
        conn.commit()
        flash('file upload successful')
        return render_template('search_results.html', src=url_for('pic',item_id=item_id), results=search_results)

#Displays the feed consisting of all of the existing posts
@app.route('/feed/', methods=['GET'])
def feed():
    conn = dbi.connect()
    feed_results = search_helper.feed(conn)
    post_author = feed_results[0]['name']
    return render_template('feed.html', posts=feed_results, author = post_author)

#Displays all of the post details given the post_id
@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post_details(post_id):
    conn = dbi.connect()
    post = [search_helper.search_by_postid(conn, post_id)][0]
    comments = insert.all_comments(conn, post_id)
    print(comments)
    #post viewing
    if request.method == 'GET':
        print('get')
        return render_template('post.html', post=post, comments=comments)
    #writing a comment
    if request.method == 'POST':
        print('post')
        user_id = int(request.form['user_id'])
        comment = request.form['comment']
        insert.add_comment(conn,user_id,comment,post_id)
        #writing the first comment
        if len(comments) == 0:
            comments = insert.new_comment_details(conn)
        else:
            comments += insert.new_comment_details(conn)
        flash('Comment submitted')
        return render_template('post.html', post=post, comments=comments)

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
            search_results = search_helper.filter(conn, search_term)
            print('results', search_results)
        if len(search_results) > 0:
            return render_template('search_results.html', results=search_results)
        else: 
            flash('No results found.')
            return redirect( url_for('search'))

@app.route('/join/', methods=["POST"])
def join():
    '''route for creating a new user. redirects to home page.'''
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('index'))
        hashed = passwd1
        print(passwd1, type(passwd1))
        conn = dbi.connect()
        curs = dbi.cursor(conn)
        try:
            curs.execute('''INSERT INTO userpass(uid,username,hashed)
                            VALUES(null,%s,%s)''',
                        [username, hashed])
            conn.commit()
        except Exception as err:
            flash('That username is taken: {}'.format(repr(err)))
            return redirect(url_for('index'))
        curs.execute('select last_insert_id()')
        row = curs.fetchone()
        uid = row[0]
        flash('FYI, you were issued UID {}'.format(uid))
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        session['visits'] = 1
        return redirect( url_for('user', username=username) )
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

@app.route('/login/', methods=["POST"])
def login():
    '''route for if an already created user is logging in.'''
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = dbi.connect()
        curs = dbi.dict_cursor(conn)
        curs.execute('''SELECT uid,hashed
                      FROM userpass
                      WHERE username = %s''',
                     [username])
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['hashed']
        if hashed == passwd:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('user', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

@app.route('/user/<username>')
def user(username):
    '''@TODO figure out what this function does'''
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            uid = session['uid']
            session['visits'] = 1+int(session['visits'])
            return redirect(url_for('index'))
            # return render_template('greet.html',
            #                        page_title='My App: Welcome {}'.format(username),
            #                        name=username,
            #                        uid=uid,
            #                        visits=session['visits'])

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/logout/', methods = ["POST"])
def logout():
    '''logout route.'''
    try:
        if 'username' in session:

            username = session['username']
            session.pop('username')
            session.pop('uid')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.before_first_request
def init_db():
    dbi.cache_cnf()
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