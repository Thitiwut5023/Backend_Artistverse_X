import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Run34047",
        database="artistverse"
    )
    return connection


def close_connection(connection):
    connection.close()
