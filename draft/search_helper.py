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

#catherine's uid for addedby @TODO
uid = 1234

'''
Searchs in title of posts and item description.
Returns ___ of what matches
@TODO figure out post id/item id
'''
def search(conn, search_key):
    curs = dbi.cursor(conn)
    sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE title LIKE %s or description LIKE %s'''
    curs.execute(sql, [search_key, search_key])
    matches = curs.fetchall()
    return matches

'''
Returns all posts that are in matching category. If there are multiple categories
'other', 'seeds', 'supplies', 'tools'
'''
def filter_type(conn, categories):
    curs = dbi.cursor(conn)
    
    if len(categories) == 1:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s''' 
    if len(categories) == 2:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s''' 
    if len(categories) == 3:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s OR item.item_type = %s''' 
    if len(categories) == 4:
        sql = '''SELECT post_id FROM post INNER JOIN item USING (item_id) WHERE item.item_type = %s OR item.item_type = %s OR item.item_type = %s OR item.item_type = %s''' 
    

    filtered = curs.execute(sql, categories) 
    return filtered


'''
This only allow to search by one zip. 
'''
def filter_zip(conn, zipcode):
    curs = dbi.cursor(conn)

    sql = '''SELECT post_id FROM post INNER JOIN user USING (user_id) WHERE user.zip_code = %s'''
    filtered = curs.execute(sql, [zipcode])
    
    return filtered