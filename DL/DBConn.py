import pyodbc
import pandas
import configparser
from termcolor import colored

from Enums.eTransactionType import eTransactionType


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


def single_query(query):
    conn = return_connection()
    cursor = conn.cursor()
    result = None
    try:
        if query.TransactionType == eTransactionType.Query:
            # querying requires the connection instead of the cursor since we use pandas to read the data
            result = (__query_execute(query, conn))
        if query.TransactionType == eTransactionType.Insert:
            result = (__insert_execute(query, cursor))
        if query.TransactionType == eTransactionType.Update:
            result = (__update_execute(query, cursor))
        return result

    except Exception as err:
        # rollback sql transaction
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def __query_execute(query, conn):
    data = pandas.read_sql(sql=query.Sql, con=conn, params=query.Args)
    return data


def __insert_execute(query, cursor):
    cursor.execute(query.Sql, query.Args)
    cursor.execute("SELECT @@IDENTITY AS ID;")
    row = cursor.fetchone()
    cursor.commit()
    return row[0]


def __update_execute(query, cursor):
    cursor.execute(query.Sql, query.Args)
    cursor.commit()
    return cursor.rowcount()
