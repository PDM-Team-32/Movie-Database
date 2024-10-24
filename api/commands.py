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
            bool(re.search("[a-z]", password)) and
            bool(re.search("[A-Z]", password)) and
            bool(re.search("[!@#$%^&*()_+\-=\[\];':\"\\|,.<>\/?]", password)) and
            bool((not re.search(" ", password))))):
        print("*** That was not a valid password ***")
        passwordHelp()
        password = str(input("\tProvide a Password: "))

    fName = input("\tProvide a First Name: ")
    lName = input("\tProvide a Last Name: ")

    ########## get info from system ##########
    currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

    ########## insert the user ##########
    sql = """INSERT INTO users 
            (firstname, lastname, email, username, password, creationdate, lastaccessdate) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)"""
    utils.exec_commit(conn, sql, (fName, lName, email, username, password, currentDatetime, currentDatetime))
    print("Welcome to MovieDB, please use the LOGIN command to access your account")



# TODO store current user id (id can be -1 if no ones logged in)
def login(conn):
    # general idea, ask for user, ask for password and if theres a match then login
    # else, loop until correct password (attempt limit?), ctrl e to exit?
    
    ########## Queries ##########
    userQuery = "SELECT username FROM users"
    idPasswordQuery = "SELECT id, password FROM users where username = %s"
    
    print("*** Note: To login, you must first create an account ***\n*** To exit the login command, enter 'exit' ***")

    ########## Username ##########
    validUser = False
    while (not validUser):
        # grab user name
        username = input("\tEnter your username: ")

        # get the users (hard to read)
        allUsers = utils.exec_get_all(conn, userQuery)

        # make the user list easy to read
        i = 0
        allUsersList = []
        for user in allUsers:
            allUsersList.append(user[0])
            i += 1

        # for debugging
        #print(allUsersList)
        #print(username)

        # check user
        if (username in allUsersList):
            validUser = True
        else:
            print("*** Not a valid username ***\n*** Note: To login, you must first create an account ***")

    ##### Password #####
    packedIdPassword = utils.exec_get_all(conn, idPasswordQuery, (username,))
    id = packedIdPassword[0][0]
    expectedPassword = packedIdPassword[0][1]

    # for debugging, uncomment if you want to feel like a hacker
    #print("\texpected password: " + expectedPassword) 
    
    password = ""
    while (not (password == expectedPassword)):
        password = input("\tEnter your password: ")
        if (password == "exit"): # note: exit is not a valid password (see createAccount())
            return 0
    
    ###### Update lastaccessdate ######
    datePrompt = "UPDATE users SET lastaccessdate = %s WHERE id = %s"
    currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
    utils.exec_commit(conn, datePrompt, (currentDatetime, id))
    
    print("Welcome back " + username)
        


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

def passwordHelp():
    print("**************** Password Requirements ****************")
    print("8 to 64 characters long")
    print("contain a lowercase letter")
    print("contain a capital letter")
    print("contain a number")
    print("contain a symbol (!@#$%^&*()_+\-=\[\];':\"\\|,.<>\/?)")
    print("contain no spaces")
    print("*******************************************************")