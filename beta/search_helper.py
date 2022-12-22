import cs304dbi as dbi


'''
Searchs in title of posts and item description.
Returns ___ of what matches
@TODO figure out post id/item id
'''
def search(conn, search_key):
    search_key = '%'+search_key+'%'
    curs = dbi.dict_cursor(conn)
    #sql = '''SELECT * FROM post WHERE title LIKE %s or description LIKE %s '''
    #sql = '''select distinct * from post, item where (item.description LIKE %s or post.title LIKE %s) and item.post_id = post.post_id'''
    #sql = '''select distinct * from post INNER JOIN item using (post_id) where item.description LIKE %s or post.title LIKE %s'''
    sql = '''select * FROM item JOIN post on item.post_id = post.post_id JOIN user on post.user_id = user.user_id where item.description LIKE %s or post.title LIKE %s'''
    curs.execute(sql, [search_key, search_key])
    matches = curs.fetchall()
    #print(type(matches))
    return matches

    

'''
Returns post information given a post_id
'''
def search_by_postid(conn, post_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post WHERE post_id = %s '''
    curs.execute(sql, [post_id])
    match = curs.fetchone()
    return match

'''
Returns message information with user_id
'''
def search_by_userid(conn, user_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) WHERE user_id = %s '''
    curs.execute(sql, [user_id])
    match = curs.fetchone()
    return match

'''
Returns all post information
'''
def feed(conn):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) ORDER BY timestamp DESC'''
    curs.execute(sql) 
    matches = curs.fetchall()
    return matches

'''
Returns all post information
'''
def my_posts(conn, user_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) where user_id = %s ORDER BY timestamp DESC'''
    curs.execute(sql, [user_id]) 
    matches = curs.fetchall()
    return matches

'''
Returns all items for one post
'''
def get_items(conn, post_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM item WHERE post_id = %s'''
    curs.execute(sql, [post_id])
    items = curs.fetchall()
    return items

'''
Returns all your message logs
'''
def all_messages(conn, user_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM messages WHERE sender_id = %s or receiver_id = %s GROUP BY receiver_id ORDER BY receiver_id, conversation_timestamp ASC'''
    curs.execute(sql, [user_id, user_id])
    matches = curs.fetchall()
    return matches

def filter(conn, category):
    curs = dbi.dict_cursor(conn)
    #category  = '"'+category+'"'
    print(category)
    sql = '''SELECT * FROM post WHERE item.item_type = %s ''' 
    sql = '''select * FROM item JOIN post on item.post_id = post.post_id JOIN user on post.user_id = user.user_id where item.item_type LIKE %s'''
    curs.execute(sql, [category]) 
    filtered = curs.fetchall()
    return filtered


'''
This only allow to search by one zip. 
'''
def filter_zip(conn, zipcode):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN user USING (user_id) WHERE user.zip_code = %s'''
    curs.execute(sql, [zipcode])
    filtered = curs.fetchall()
    return filtered

if __name__ == '__main__':
    dbi.conf('sunshare_db')  # only once
    conn = dbi.connect() # as often as necessary
    search_result = filter(conn, 'seeds')
    print('result', search_result)

    