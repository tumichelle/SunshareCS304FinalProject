# alpha version
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)


import cs304dbi as dbi
# import cs304dbi_sqlite3 as dbi

import sys, os, random
import imghdr
import search_helper
import insert
import cs304login
import login_helper

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# For file upload
app.config['UPLOADS'] = 'uploads' # save file uploads to 'uploads' folder
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

#main page on startup
@app.route('/')
def index():
    if 'username' in session:
        return render_template('main_logged_in.html')
    else:
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

#message page
@app.route('/all_messages/', methods=['GET'])
def all_messages():
    conn = dbi.connect()
    user_id = session.get('uid') 
    all_messages = search_helper.all_messages(conn, user_id)
    print("all messages: ", all_messages)
    return render_template('all_messages.html', messages=all_messages, user_id=user_id)

#Displays all of the message details given a sender id and receiver id 
@app.route('/message/<sender_id>/<receiver_id>', methods=['GET','POST'])
def message_details(sender_id, receiver_id):
    conn = dbi.connect()

    # Retrieve messages b/t sender and receiver
    messages = list(insert.all_messages(conn, sender_id, receiver_id))

    print("messages: ", messages)
    print("args: ", request.args)

    if request.method == 'GET':
        print('get')
        return render_template('message.html', messages=messages, sender_id=sender_id, receiver_id=receiver_id)
    if request.method == 'POST':
        print('POSTING HERE')
        print(messages)

        # Add message to DB
        message = request.form['message']
        insert.add_message(conn, sender_id, receiver_id, message)
        messages += insert.new_message_details(conn)

        print("messages:")
        print(messages)
        flash('Message sent successfully')

        return render_template('message.html', messages=messages, sender_id=sender_id, receiver_id=receiver_id)

#display photo of an item
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
        #do not allow user to view post page if not logged in
        if 'username' not in session:
            flash('Log in or create an account to post.')
            return redirect(url_for('index'))
        #returns a blank form if a user is logged in
        return render_template('insert_post.html')
    else:
        #process the form
        conn = dbi.connect()
        #user_id = int(request.form['user_id'])
        title = request.form['title']
        description = request.form['description']
        item_type = request.form['item_type']
        item_photo = request.files['item_photo']
        item_id = insert.add_item(conn, description, item_photo, item_type)
        #get user id from the session
        if 'username' in session:
            user_id = session['uid']
        else:
            flash('Log in or create an account to post.')
            return redirect(url_for('index'))
        insert.add_post(conn,user_id,item_id,title)
        search_results = [insert.new_post_details(conn)]
        print(search_results)
        flash('Post created successfully')

        #name, save, and insert item_photo into the picfile table
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
    if 'username' not in session:
        flash('Log in or create an account to view the full feed.')
        return redirect(url_for('index'))
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
        # Retrieve ID of viewer
        user_id = session.get('uid') 
        
        print("sender: ", user_id)
        print("receiver: ", post['user_id'])

        return render_template('post.html', post=post, comments=comments, sender_id=user_id)
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

        return render_template('post.html', post=post, comments=comments, sender_id=user_id)

'''
displays the search/filter page on GET
searches/filters and displays results if found on POST
'''
@app.route('/search/', methods = ['GET', 'POST'])
def search():
    if request.method == 'GET':
        #do not allow user to view if not logged in
        if 'username' not in session:
            flash('Log in or create an account to search posts.')
            return redirect(url_for('index'))
        #if user is logged in, show them the search page
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

@app.route('/profile/')
def profile():
    try: 
        if 'username' in session:
            username = session['username']
            fullname = session['fullname']
            email = session['email']
            zipcode = session['zipcode']
            return render_template('profile.html', username=username, fullname=fullname, email=email, zipcode=zipcode,)
        else:
            flash('you\'re not logged in, can\'t view profile.')
            return redirect(url_for('index'))
    except Exception as err:
        flash('error in displaying profile '+str(err))
        return redirect( url_for('index') )


'''route for creating a new user. redirects to home page.'''
@app.route('/join/', methods=["POST"])
def join():
    try:
        #getting form info
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        fullname = request.form['fullname']
        email = request.form['email']
        zipcode = request.form['zipcode']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('index'))
        #hashed = passwd1
        #print(passwd1, type(passwd1))
        #make  connection to connect to insert into userpass table
        conn = dbi.connect()
        uid, keyErr, exceptionObject = login_helper.insert_userpass(conn, username, passwd1)
        if keyErr:
            flash('That username is taken: {}'.format(repr(keyErr)))
            return redirect(url_for('index'))
        elif exceptionObject:
            flash('An error occurred: {}'.format(repr(exceptionObject)))
            return redirect(url_for('index'))
        #make second connection to connect to insert into user table
        conn2 = dbi.connect()
        user_success = login_helper.insert_user(conn2, fullname, uid, zipcode, email)
        if not user_success:
            flash('error in inserting into user table.')
            return redirect(url_for('index'))
        # curs = dbi.cursor(conn)
        # try:
        #     curs.execute('''INSERT INTO userpass(uid,username,hashed)
        #                     VALUES(null,%s,%s)''',
        #                 [username, hashed])
        #     conn.commit()
        # except Exception as err:
        #     flash('That username is taken: {}'.format(repr(err)))
        #     return redirect(url_for('index'))
        # curs.execute('select last_insert_id()')
        # row = curs.fetchone()
        # uid = row[0]
        # flash('FYI, you were issued UID {}'.format(uid))

        flash('successfully logged in as '+ username)
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        session['fullname'] = fullname
        session['email'] =  email
        session['zipcode'] = zipcode
        #session['visits'] = 1
        return redirect( url_for('profile') )
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

'''
handler for when login form is filled out
'''
@app.route('/login/', methods=["POST"])
def login():
    try:
        #get form data
        username = request.form['username']
        passwd = request.form['password']
        conn = dbi.connect()
        success, uid = login_helper.login_user(conn, username, passwd)
        if success:
            flash('successfully logged in as '+ username)
            session['username'] = username
            session['uid'] = uid
            session['logged_in'] = True
            #get the other users information!!
            conn2 = dbi.connect()
            fullname, email, zipcode = login_helper.get_user_info(conn2, uid)
            session['fullname'] = fullname
            session['email'] =  email
            session['zipcode'] = zipcode
            #session['visits'] = 1
            return redirect( url_for('profile') )
        else: 
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))

        # curs = dbi.dict_cursor(conn)
        # curs.execute('''SELECT uid,hashed
        #               FROM userpass
        #               WHERE username = %s''',
        #              [username])
        # row = curs.fetchone()
        # if row is None:
        #     # Same response as wrong password,
        #     # so no information about what went wrong
        #     flash('login incorrect. Try again or join')
        #     return redirect( url_for('index'))
        # hashed = row['hashed']
        # #making sure it is a valid user with password 
        # if hashed == passwd:
        #     flash('successfully logged in as '+username)
        #     session['username'] = username
        #     session['uid'] = row['uid']
        #     session['logged_in'] = True
        #     #session['visits'] = 1
        #     return redirect( url_for('user', username=username) )
        # else:
        #     flash('login incorrect. Try again or join')
        #     return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

'''
handler for routing back to home page after logging in
'''
# @app.route('/user/<username>')
# def user(username):
#     try:
#         if 'username' in session:
#             username = session['username']
#             uid = session['uid']
#             #session['visits'] = 1+int(session['visits'])
#             return redirect(url_for('index'))

#         else:
#             flash('you are not logged in. Please login or join')
#             return redirect( url_for('index') )
#     except Exception as err:
#         flash('some kind of error '+str(err))
#         return redirect( url_for('index') )

'''
logout handler. button to log out not on app at the moment, 
adding in beta.
'''
@app.route('/logout/', methods = ["POST"])
def logout():
    try:
        if 'username' in session:
            username = session['username']
            #remove all user info from session
            session.pop('username')
            session.pop('uid')
            session.pop('logged_in')
            session.pop('fullname') 
            session.pop('email')
            session.pop('zipcode')
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