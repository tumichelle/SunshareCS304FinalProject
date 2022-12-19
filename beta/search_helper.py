import cs304dbi as dbi

'''
NOTES:

- search keys that are passed should be pre processed, perhaps only searching one thing at a time? the function i've written will only search 
- don't need to check for validation of category because will just be check box?
- how to get it to search by multiple zip codes, I think i found a way to do this but do we want that?

Filtering/sorting
Add filter options to search page: type, zip code 
Searching
Add search bar
Searches in title of posts and item description
'''

'''
Searchs in title of posts and item description.
Returns ___ of what matches
@TODO figure out post id/item id
'''
def search(conn, search_key):
    search_key = '%'+search_key+'%'
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN item USING (item_id) WHERE title LIKE %s or description LIKE %s '''
    curs.execute(sql, [search_key,search_key])
    matches = curs.fetchall()
    #print(type(matches))
    return matches

'''
Returns post information given a post_id
'''
def search_by_postid(conn, post_id):
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT * FROM post INNER JOIN item USING (item_id) WHERE post_id = %s '''
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
    sql = '''SELECT * FROM post INNER JOIN item USING (item_id) INNER JOIN user USING (user_id) ORDER BY timestamp DESC'''
    curs.execute(sql) 
    matches = curs.fetchall()
    return matches

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
    sql = '''SELECT * FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s ''' 
    curs.execute(sql, [category]) 
    filtered = curs.fetchall()
    return filtered

'''
Returns all posts that are in matching category. If there are multiple categories
'other', 'seeds', 'supplies', 'tools'
'''
def filter_type(conn, categories):
    curs = dbi.dict_cursor(conn)
    
    if len(categories) == 1:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s''' 
    if len(categories) == 2:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s''' 
    if len(categories) == 3:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s OR item.item_type = %s''' 
    if len(categories) == 4:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s OR item.item_type = %s OR item.item_type = %s''' 
    

    curs.execute(sql, categories) 
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
    # result = search(conn, 'drill')
    # print('result',result)
    # result2 = search(conn, 'charger')
    # print('result',result2)

    filter_result = filter(conn, 'seeds')
    print('result', filter_result)

    