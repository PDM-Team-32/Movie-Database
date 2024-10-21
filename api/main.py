import utils
import psycopg2
import os
from sshtunnel import SSHTunnelForwarder
import dotenv
import commands

def main():
    dotenv.load_dotenv("./credentials.env")
    commands.help()
    # Set x to the user input and ensure it does not ask us to quit
    while (x := getUserInput()) != "QUIT":
        if(x not in commands.cliCommands.keys()):
            print("Please enter a valid input")
        else:
            if(commands.cliCommands[x]["isDbAccessCommand"]):
                # Wrap the command in the access DB stuff so we dont have to write it every time
                accessDbWithCommand(commands.cliCommands[x]["actionFunction"])
    # accessDBExample()
    
    
def getUserInput():
    return(input('Please enter a command: '))


def accessDbWithCommand(command):
    try:
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

                command(conn)

    except:
         print("Connection Failed")

def accessDBExample():
    try:
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
    except:
         print("Connection Failed")


if __name__ == "__main__":
    main()