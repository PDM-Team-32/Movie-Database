import utils
from tabulate import tabulate
import datetime
import re

# TODO char limits on everything?
def createAccount(conn):
    print("Account Creation:")

    ########## collect user info from cmd line ########## 
    username = input("\tProvide a Username: ")
    
    # email checking 
    email = input("\tProvide an email address: ")
    while (not re.match(r"^\S+@\S+\.\S+$", email)):
        print("***" + email + " is not a valid email address ***")
        email = input("\tProvide a valid email address: ")
    
    # password checking
    # length [8, 64]
    # contains a lowercase letter
    # contains a capital letter
    # contains a number
    # contains a symbol
    # does not contain a space
    # TODO hash in phase 3
    passwordHelp()
    password = str(input("\tProvide a Password: "))
    while (not (
            (len(password) >= 8) and (len(password) <= 64) and 
            re.search("[a-z]", password) and
            re.search("[A-Z]", password) and
            re.search("[!@#$%^&*()_+\-=\[\];':\"\\|,.<>\/?]", password) and
            (not re.search(" ", password)))):
        print("*** That was not a valid password ***")
        passwordHelp()
        password = str(input("\tProvide a Password: "))

    # TODO TODO TODO TODO TODO TODO REMOVE LATER (does python have ifdefs or an equivalent (i miss compiled langauges))
    password = "123456"

    fName = input("\tProvide a First Name: ")
    lName = input("\tProvide a Last Name: ")

    ########## get info from system ##########
    current_datetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

    ########## insert the user ##########
    sql = """INSERT INTO users 
            (firstname, lastname, email, username, password, creationdate, lastaccessdate) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)"""
    utils.exec_commit(conn, sql, (fName, lName, email, username, password, current_datetime, current_datetime))

    # TODO name of service?
    print("Welcome to NAME, please use the LOGIN command to access your account")

def passwordHelp():
    print("**************** Password Requirements ****************")
    print("8 to 64 characters long")
    print("contain a lowercase letter")
    print("contain a capital letter")
    print("contain a number")
    print("contain a symbol (!@#$%^&*()_+\-=\[\];':\"\\|,.<>\/?)")
    print("contain no spaces")
    print("******************************************************")

def login(conn):
    print("Login")


def help():
    print("*** COMMAND LINE INTERFACE MENU ***")
    for key in cliCommands:
        print(key + ": " + cliCommands[key]["helpText"])


def viewCollections(conn):
    userId = input("Provide a user ID (this is temporary until we create a login and track current userId): ")
    sql = """SELECT
                umc.name,
                COUNT(m.title),
                TO_CHAR(SUM(length)*'1 minute'::interval, 'HH24:MI')
            FROM movieCollection AS mc
            INNER JOIN userMovieCollection AS umc
            ON (umc.id = mc.collectionid)
            INNER JOIN movie AS m
            ON (m.id = mc.movieid)
            WHERE mc.collectionId IN (
                                    SELECT id
                                    FROM userMovieCollection
                                    WHERE userId = 1)
            GROUP BY umc.name;"""
    movies = utils.exec_get_all(conn, sql, (userId,))
    print(tabulate(movies, headers=["Name", "Movie Count", "Collection Length"], tablefmt='orgtbl'))


def createMovieCollection(conn):
    userId = input("Provide a user ID (this is temporary until we create a login and track current userId): ")
    collectionName = input("Name your new collection: ")
    sql = """INSERT INTO userMovieCollection (userId, name) VALUES (%s, %s)"""
    utils.exec_commit(conn, sql, (userId, collectionName))


def quit():
    raise Exception("The QUIT command has no related function, something is wrong")


# This must be at the bottom of this file so that the functions are declared before assignment.
cliCommands = {
    "CREATE_ACCOUNT": 
    {
        "helpText": "Create your new account",
        "actionFunction": createAccount,
        "isDbAccessCommand": True
    }, 
    "LOGIN":
    {
        "helpText": "Login to your account",
        "actionFunction": login,
        "isDbAccessCommand": True
    },
    "CREATE_COLLECTION" :
    {
        "helpText": "Create a new (empty) Movie Collection",
        "actionFunction": createMovieCollection,
        "isDbAccessCommand": True
    },
    "VIEW_COLLECTION" :
    {
        "helpText": "Look at your collections and see their stats",
        "actionFunction": viewCollections,
        "isDbAccessCommand": True
    },
    "HELP":
    {
        "helpText": "Print this menu again",
        "actionFunction": help,
        "isDbAccessCommand": False
    },
    "QUIT": 
    {
        "helpText": "Exit this application",
        "actionFunction": quit,
        "isDbAccessCommand": False
    }
}