import utils
import psycopg2
import os
from sshtunnel import SSHTunnelForwarder
import dotenv

def main():
    dotenv.load_dotenv("./credentials.env")
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
        conn = psycopg2.connect(**params)
        print("Database connection established")

        sql = """SELECT * FROM GENRE"""
        print(utils.exec_get_all(conn, sql))

        conn.close()
    
    

if __name__ == "__main__":
    main()