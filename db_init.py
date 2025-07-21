import mysql.connector
import os
import dotenv

load_dotenv('dbdocker.env')
db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
cursor = db.cursor()

cursor.execute("DROP DATABASE IF EXISTS carrom")
db.commit()
cursor.execute("CREATE DATABASE IF NOT EXISTS carrom")
db.commit()
cursor.execute("USE carrom")
db.commit()
cursor.execute("CREATE TABLE IF NOT EXISTS matches (player1 VARCHAR(60) NOT NULL, player2 VARCHAR(60) NOT NULL, score1 INT NOT NULL, score2 INT NOT NULL, PRIMARY KEY (player1, player2))")
db.commit()
cursor.close()
db.close()