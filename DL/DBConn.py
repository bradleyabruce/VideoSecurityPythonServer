import mysql.connector
import pandas
from termcolor import colored
from Enums.eTransactionType import eTransactionType
from Objects.Exceptions import DatabaseConnectionException

# One thing to note is that the parameter marker in sql statements for MySQL is: '%s'
# This is opposed to the parameter marker from sqlite which was '?'


def return_connection():
    try:
        connection = mysql.connector.connect(option_files='data.conf')
        return connection
    except Exception as e:
        print("Connecting to database - " + colored("Failure", "red"))
        raise DatabaseConnectionException


def single_query(query):
    conn = return_connection()
    # conn.row_factory = dict_factory
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        if query.TransactionType == eTransactionType.Query:
            result = (__query_execute(query, cursor))
        if query.TransactionType == eTransactionType.Insert:
            result = (__insert_execute(query, cursor))
        if query.TransactionType == eTransactionType.Update:
            result = (__update_execute(query, cursor))

        # commit sql transaction
        conn.commit()
        return result

    except Exception as err:
        conn.rollback()
        raise DatabaseConnectionException
    finally:
        cursor.close()
        conn.close()


def __query_execute(query, cursor):
    cursor.execute(query.Sql, query.Args)
    return cursor.fetchall()


def __insert_execute(query, cursor):
    cursor.execute(query.Sql, query.Args)
    return cursor.lastrowid


def __update_execute(query, cursor):
    cursor.execute(query.Sql, query.Args)
    return cursor.rowcount


# This is used to help us read query results more easily
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
