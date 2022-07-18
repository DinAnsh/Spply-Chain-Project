import pyodbc

def get_db():
    connect_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-RAAKMV6U\SQLEXPRESS;DATABASE=Supply_Chain_Db;trusted_connection=yes;'
    con = pyodbc.connect(connect_str)
    con.autocommit = False
    cur = con.cursor()
    return cur, con

def save_db(connection):
    connection.commit()
    return "Connection is commited!"


def close_db(connection):
    connection.close()
    return "Conection is closed!"
'''
cursor, connection = get_db()

try:
    cur.execute("")
except pyodbc.DatabaseError as err:
    conn.rollback()
else:
    save_db(connection)'''