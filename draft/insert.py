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

