import utils
import psycopg2
import os
from sshtunnel import SSHTunnelForwarder
import dotenv
import commands

# cliCommands = {
#     "CREATE_ACCOUNT": 
#     {
#         "helpText": "Create your new account",
#         "actionFunction": commands.createAccount
#     }, 
#     "LOGIN":
#     {
#         "helpText": "Login to your account",
#         "actionFunction": commands.login
#     },
#     "CREATE_COLLECTION" :
#     {
#         "helpText": "Create a new (empty) Movie Collection",
#         "actionFunction": commands.login
#     },
#     "HELP":
#     {
#         "helpText": "Print this menu again",
#         "actionFunction": commands.help
#     },
#     "QUIT": 
#     {
#         "helpText": "Exit this application",
#         "actionFunction": commands.quit
#     }
# }


def main():
    dotenv.load_dotenv("./credentials.env")
    commands.help()
    # Set x to the user input and ensure it does not ask us to quit
    while (x := getUserInput()) != "QUIT":
        if(x not in commands.cliCommands.keys()):
            print("Please enter a valid input")
        else:
            commands.cliCommands[x]["actionFunction"]()
    # accessDBExample()
    
    
def getUserInput():
    return(input('Please enter a command: '))

def stripInputs(input):
    return(input.split(" ", 1)[0])
 
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