import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nueva123",
    database="game_tracker"
)

if conexion.is_connected():
    print("me conecte")

conexion.close()
