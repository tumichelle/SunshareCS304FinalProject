#beta version
import cs304dbi as dbi
import datetime, time

def add_post(conn,user_id,num_items,title):
    '''adds a post given the information in the insert form'''
    curs = dbi.cursor(conn)
    curs.execute('''
        insert into post(user_id,num_items,title)
        values (%s,%s,%s)''',
        [user_id,num_items,title])
    conn.commit()

def delete_post(conn,post_id):
    '''deletes a post given the post_id'''
    curs = dbi.cursor(conn)
    curs.execute('''
        delete from post where post_id = %s''',
        [post_id])
    conn.commit()

def delete_items(conn,post_id):
    '''deletes items given the post_id'''
    curs = dbi.cursor(conn)
    curs.execute('''
        delete from item where post_id = %s''',
        [post_id])
    conn.commit()

def new_post_id(conn):
    '''get post_id of the post just made'''
    curs = dbi.cursor(conn)
    curs.execute('''select last_insert_id() from post''')
    return curs.fetchone() #returns the id of the new post

def add_item(conn, post_id, description, item_photo, item_type):
    '''adds an item given the information in the insert form'''
    curs = dbi.cursor(conn)
    curs.execute('''
        insert into item(post_id, description,item_photo,item_type)
        values (%s, %s,%s,%s)''',
        [post_id, description,item_photo,item_type])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    row = curs.fetchone()
    return row[0] #returns the item_id

def add_comment(conn,user_id,comment,post_id):
    '''inserts a comment into the comment table'''
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO comment (posted_by, text, post_id)
        values (%s,%s,%s)''', [user_id,comment,post_id])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    row = curs.fetchone()
    return row[0] #returns the comment_id

def new_comment_details(conn):
    '''get details of the comment just posted'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select userpass.username, user.name, 
    comment.text, comment.timestamp 
    from user, comment, userpass 
    where comment.comment_id = last_insert_id() 
    and user.user_id = comment.posted_by 
    and userpass.uid = user.user_id''')
    return curs.fetchall() #returns all the new comment details

def all_comments(conn, post_id):
    '''get details of all the comments for this post'''
    curs = dbi.dict_cursor(conn)
    #curs.execute('''select * from comment where post_id = %s''', [post_id])
    curs.execute('''select userpass.username, user.name, comment.text, 
    comment.timestamp from user, comment, userpass 
    where comment.post_id = %s and user.user_id = comment.posted_by 
    and userpass.uid = user.user_id''', [post_id])
    return curs.fetchall() #return all the comments on a post


def add_message(conn,sender_id,receiver_id,message):
    '''inserts a message into the message table'''
    # Retrieve current timestamp
    t = time.time()
    ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO messages 
        (sender_id,receiver_id,conversation_text,conversation_timestamp)
        values (%s,%s,%s,%s)''', [sender_id,receiver_id,message,ts])
    conn.commit()
    curs.execute('''select last_insert_id()''')
    row = curs.fetchone()
    return row[0] #returns the message_id

def new_message_details(conn):
    '''get details of the message just sent'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from messages 
    where message_id = last_insert_id()''')
    return curs.fetchall() #returns details of message

def all_messages(conn, sender_id, receiver_id):
    '''get details of all the messages with user_id'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    select * from messages 
    where sender_id = %s and receiver_id = %s
    or receiver_id = %s and sender_id = %s
    ''', 
    [sender_id,receiver_id,sender_id,receiver_id])
    return curs.fetchall() #gets all the messages between two users

