import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nicha12345",
        database="artistverse"
    )
    return connection


def close_connection(connection):
    connection.close()
