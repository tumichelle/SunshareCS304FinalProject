import cs304dbi as dbi

def search(conn, search_key):
    '''search for posts based on search_key.
    returns information from user, post, and item tables
    of any matches '''
    search_key = '%'+search_key+'%'
    curs = dbi.dict_cursor(conn)
    sql = '''select * FROM item JOIN post on item.post_id = post.post_id 
    JOIN user on post.user_id = user.user_id 
    where item.description LIKE %s or post.title LIKE %s'''
    curs.execute(sql, [search_key, search_key])
    matches = curs.fetchall()
    return matches

def search_by_postid(conn, post_id):
    '''Returns post information given a post_id'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post WHERE post_id = %s '''
    curs.execute(sql, [post_id])
    match = curs.fetchone()
    return match

def search_by_userid(conn, user_id):
    '''Returns message information with user_id'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) 
    WHERE user_id = %s '''
    curs.execute(sql, [user_id])
    match = curs.fetchone()
    return match

def feed(conn):
    '''Returns all post information'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) 
    ORDER BY timestamp DESC'''
    curs.execute(sql) 
    matches = curs.fetchall()
    return matches

def my_posts(conn, user_id):
    '''Returns all post information for one user'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) 
    where user_id = %s ORDER BY timestamp DESC'''
    curs.execute(sql, [user_id]) 
    matches = curs.fetchall()
    return matches

def get_items(conn, post_id):
    '''Returns all items for one post'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM item WHERE post_id = %s'''
    curs.execute(sql, [post_id])
    items = curs.fetchall()
    return items

def all_messages(conn, user_id):
    '''Returns all your message logs'''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM messages WHERE sender_id = %s or receiver_id = %s 
    GROUP BY receiver_id ORDER BY receiver_id, conversation_timestamp ASC'''
    curs.execute(sql, [user_id, user_id])
    matches = curs.fetchall()
    return matches

def filter(conn, category):
    curs = dbi.dict_cursor(conn)
    sql = '''select * FROM item JOIN post on item.post_id = post.post_id 
    JOIN user on post.user_id = user.user_id where item.item_type LIKE %s'''
    curs.execute(sql, [category]) 
    filtered = curs.fetchall()
    return filtered

def filter_zip(conn, zipcode):
    '''    This only allow to search by one zip. '''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) 
    WHERE user.zip_code = %s'''
    curs.execute(sql, [zipcode])
    filtered = curs.fetchall()
    return filtered

if __name__ == '__main__':
    dbi.conf('sunshare_db')  # only once
    conn = dbi.connect() # as often as necessary
    search_result = filter(conn, 'seeds')
    print('result', search_result)

    