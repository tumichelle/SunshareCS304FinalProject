#alpha version
import cs304dbi as dbi

def add_post(conn,user_id,item_id,title):
    '''adds a post given the information in the insert form
    '''
    curs = dbi.cursor(conn)
    curs.execute('''
        insert into post(user_id,item_id,title)
        values (%s,%s,%s)''',
        [user_id,item_id,title])
    conn.commit()

def new_post_details(conn):
    '''
    get details of the post just made
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from post INNER JOIN item USING (item_id) where post_id = last_insert_id()''')
    return curs.fetchone()

def add_item(conn, description, item_photo, item_type):
    '''adds an item given the information in the insert form
    '''
    curs = dbi.cursor(conn)
    curs.execute('''
        insert into item(description,item_photo,item_type)
        values (%s,%s,%s)''',
        [description,item_photo,item_type])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    row = curs.fetchone()
    return row[0] #returns the item_id

def add_comment(conn,user_id,comment,post_id):
    '''
    inserts a comment into the comment table
    '''
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO comment (posted_by, text, post_id)
        values (%s,%s,%s)''', [user_id,comment,post_id])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    row = curs.fetchone()
    return row[0] #returns the comment_id

def new_comment_details(conn):
    '''get details of the comment just posted
    '''
    curs = dbi.dict_cursor(conn)
    #curs.execute('''select * from comment where comment_id = last_insert_id()''')
    curs.execute('''select userpass.username, user.name, comment.text, comment.timestamp from user, comment, userpass where comment.comment_id = last_insert_id() and user.user_id = comment.posted_by and userpass.uid = user.user_id''')
    return curs.fetchall()

def all_comments(conn, post_id):
    '''get details of all the comments for this post
    '''
    curs = dbi.dict_cursor(conn)
    #curs.execute('''select * from comment where post_id = %s''', [post_id])
    curs.execute('''select userpass.username, user.name, comment.text, comment.timestamp from user, comment, userpass where comment.post_id = %s and user.user_id = comment.posted_by and userpass.uid = user.user_id''', [post_id])
    return curs.fetchall()

    '''select userpass.username, user.name, comment.text, comment.timestamp from user, comment, userpass where comment.post_id = 22 and user.user_id = comment.posted_by and userpass.uid = user.user_id'''