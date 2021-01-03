import pyodbc
import configparser
from termcolor import colored


def get_data_config():
    cf = configparser.ConfigParser()
    cf.read('data.conf')
    host = cf.get("SQLServer", "host")
    database = cf.get("SQLServer", "database")
    user = cf.get("SQLServer", "user")
    password = cf.get("SQLServer", "password")
    return host, database, user, password


def return_connection():
    try:
        config = get_data_config()
        conn_info = 'DRIVER={SQL Server}; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s'% (config[0], config[1], config[2], config[3])
        mssql_conn = pyodbc.connect(conn_info)
        return mssql_conn
    except Exception as e:
        print("Connecting to database - " + colored("Failure", "red"))
        return None


def query_return(query):
    conn = return_connection()
    cursor = conn.cursor(buffered=True, dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()


def query_update(query, is_insert):
    conn = return_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        if cursor.rowcount > 0:
            if is_insert:
                return cursor.lastrowid
            else:
                return cursor.rowcount
        else:
            return 0
    except Exception as e:
        print(e)
        return 0
    finally:
        cursor.close()
        conn.close()

