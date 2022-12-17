'''
***adapted from Scott Anderson cs304login.py module***
'''

import cs304dbi as dbi
import pymysql
import bcrypt

def insert_userpass(conn, username, password):
    '''inserts given username & password into the userpass table.  Returns
three values: the uid, whether there was a duplicate key error, and
either false or an exception object.
    '''
    hashed = bcrypt.hashpw(password.encode('utf-8'),
                           bcrypt.gensalt())
    curs = dbi.cursor(conn)
    try: 
        curs.execute('''INSERT INTO userpass(username, hashed) VALUES(%s, %s)''',
                     [username, hashed.decode('utf-8')])
        conn.commit()
        curs.execute('select last_insert_id()')
        row = curs.fetchone()
        return (row[0], False, False)
    except pymysql.err.IntegrityError as err:
        details = err.args
        print('error',details)
        if details[0] == pymysql.constants.ER.DUP_ENTRY:
            print('duplicate key for username {}'.format(username))
            return (False, True, False)
        else:
            print('some other error!')
            return (False, False, err)

def insert_user(conn, fullname, uid, zipcode, email):
    '''
    inserts new user information into the user table.  Returns true if 
    the action was successful, otherwise returns False.
    '''
    curs = dbi.cursor(conn)
    try: 
        curs.execute('''INSERT INTO user(user_id, email, name, zip_code) VALUES(%s, %s, %s, %s)''',
                     [uid, email, fullname, zipcode])
        conn.commit()
        return True
    except Exception as err:
        return False

def login_user(conn, username, password):
    '''tries to log the user in given username & password. Returns True if
success and returns the uid as the second value on success. Otherwise, False, False.'''
    curs = dbi.cursor(conn)
    curs.execute('''SELECT uid, hashed FROM userpass WHERE username = %s''',
                 [username])
    row = curs.fetchone()
    if row is None:
        # no such user
        return (False, False)
    uid, hashed = row
    hashed2_bytes = bcrypt.hashpw(password.encode('utf-8'),
                                  hashed.encode('utf-8'))
    hashed2 = hashed2_bytes.decode('utf-8')
    if hashed == hashed2:
        return (True, uid)
    else:
        # password incorrect
        return (False, False)

def get_user_info(conn, uid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT email, name, zip_code FROM user WHERE user_id = %s''',
                 [uid])
    userinfo = curs.fetchone()
    return userinfo['name'], userinfo['email'], userinfo['zip_code']

def check_logged_in():
    '''returns true if someone is logged in'''
    if 'username' in session:
        return True
    else:
        return False


def delete_user(conn, username):
    '''deletes from userpass. '''
    curs = dbi.cursor(conn)
    curs.execute('''DELETE FROM userpass WHERE username = %s''',
                 [username])
    conn.commit()

if __name__ == '__main__':
    conn = dbi.connect()
    delete_user(conn, 'fred')
    delete_user(conn, 'george')

    for username in ['fred', 'george', 'fred']:
        print(username, insert_user(conn, username, 'secret'))
        print(username, login_user(conn, username, 'secret'))