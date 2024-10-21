import psycopg2
from sshtunnel import SSHTunnelForwarder
import os


## Use to connect to the database using the .env file
def connect():
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=os.getenv("DB_USER"),
                            ssh_password=os.getenv("PASSWORD"),
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': os.getenv("NAME"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("PASSWORD"),
            'host': os.getenv("HOST"),
            'port': server.local_bind_port
        }
        return(psycopg2.connect(**params))

## Executes all SQL commands in the file at the provided path
#
# @param path The path to the SQL file being executed
def exec_sql_file(conn, path):
    full_path = os.path.join(os.path.dirname(__file__), f'{path}')
    cur = conn.cursor()
    with open(full_path, 'r') as file:
        cur.execute(file.read())
    conn.commit()

## Use this to SELECT the top entry from the DB
#
# @param sql The sql command to be executed as a string. Any args should be given a "%s" and provided in the args
# @param args A tuple which holds the args to be injected into the SQL string. Single args should be written as (arg,)
def exec_get_one(conn, sql, args={}):
    cur = conn.cursor()
    cur.execute(sql, args)
    one = cur.fetchone()
    return one

def exec_commit_many(conn, sql, args):
    cur = conn.cursor()
    result = cur.executemany(sql, args)
    conn.commit()
    return result

## Use this to SELECT all entries from the database which match the select criteria
#
# @param sql The sql command to be executed as a string. Any args should be given a "%s" and provided in the args
# @param args A tuple which holds the args to be injected into the SQL string. Single args should be written as (arg,)
def exec_get_all(conn, sql, args={}):
    cur = conn.cursor()
    cur.execute(sql, args)
    list_of_tuples = cur.fetchall()
    return list_of_tuples

## Use this to INSERT an entry into the database
#
# @param sql The sql command to be executed as a string. Any args should be given a "%s" and provided in the args
# @param args A tuple which holds the args to be injected into the SQL string. Single args should be written as (arg,)
def exec_commit(conn, sql, args={}):
    cur = conn.cursor()
    result = cur.execute(sql, args)
    conn.commit()
    return result

## Returns ID of whatever was committed
#
# @param sql The sql command to be executed as a string. Any args should be given a "%s" and provided in the args
# @param args A tuple which holds the args to be injected into the SQL string. Single args should be written as (arg,)
def exec_commit_with_id(conn, sql, args={}):
    cur = conn.cursor()
    result = cur.execute(sql, args)
    #To get any returning items, must do a fetchall
    result = cur.fetchall()
    conn.commit()
    return result

