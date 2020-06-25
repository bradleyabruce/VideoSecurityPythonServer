import mysql.connector
from termcolor import colored


def return_connection():
    try:
        connection = mysql.connector.connect(option_files='data.conf')
        # print("Connecting to database - Success")
        return connection
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

