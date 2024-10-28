import utils
from tabulate import tabulate
import datetime
import re


# TODO char limits on everything?
def createAccount(conn):
    print("Account Creation:")

    ########## collect user info from cmd line ########## 
    while (True):
        username = input("\tProvide a Username: ")
        userCheckQuery = "SELECT username FROM users WHERE username = %s"
        results = utils.exec_get_one(conn, userCheckQuery, (username,))[0]
        if (results):
            print("*** That username is taken! ***")
            continue
        else:
            break

    
    # email checking 
    email = input("\tProvide an email address: ")
    while (not re.match(r"^\S+@\S+\.\S+$", email)):
        print("***" + email + " is not a valid email address ***")
        email = input("\tProvide a valid email address: ")
    

    """
    password checking
    length [8, 64]
    contains a lowercase letter
    contains a capital letter
    contains a number
    contains a symbol
    does not contain a space
    TODO hash in phase 3    
    """
    passwordHelp()
    password = str(input("\tProvide a Password: "))
    while (not (
           (len(password) >= 8) and (len(password) <= 64) and 
           bool(re.search("[a-z]", password)) and
           bool(re.search("[A-Z]", password)) and
           bool(re.search("[!@#$%^&*()_+\-=\[\]'\\\|,.<>\/?]", password)) and
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


def login(conn):
    ########## Queries ##########
    userQuery = "SELECT username FROM users"
    idPasswordQuery = "SELECT id, password FROM users where username = %s"
    
    print("*** Note: To login, you must first create an account ***\n*** To exit the login command, enter 'exit' ***")

    ########## Username ##########
    validUser = False
    while (not validUser):
        # grab user name
        username = input("\tEnter your username: ")
        if (username.lower() == "exit"):
            return

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
            print("*** Not an existing username ***\n*** Note: To login, you must first create an account ***")

    ##### Password #####
    packedIdPassword = utils.exec_get_all(conn, idPasswordQuery, (username,))
    id = packedIdPassword[0][0]
    expectedPassword = packedIdPassword[0][1]

    # for debugging, uncomment if you want to feel like a hacker
    #print("\texpected password: " + expectedPassword) 
    
    password = ""
    while (not (password == expectedPassword)):
        password = input("\t(" + username + ") Enter your password: ")
        if (password.lower() == "exit"): # note: exit is not a valid password (see createAccount())
            return
    
    ###### Update lastaccessdate ######
    datePrompt = "UPDATE users SET lastaccessdate = %s WHERE id = %s"
    currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
    utils.exec_commit(conn, datePrompt, (currentDatetime, id))
    
    print("Welcome back " + username)
    utils.sessionToken = int(id)
        
# TODO this needs to become a connected function to store sessionToken in DB
def logout():
    if (utils.sessionToken > 0):
        utils.sessionToken = -1
        print("*** You have logged out. Use LOGIN to login again ***")
    else:
        print("*** You need to LOGIN before you can LOGOUT ***")

"""
Idea here is a user will search for another user, and follow, unfollow, 
or see their movie collections or who their following etc (whatever we want)
"""
def userSearch(conn):
    searchedUsername = input("\tPlease input a username to search: ")

    # search for the userId
    searchQuery = "SELECT id FROM users WHERE username = %s"
    searchedUserId = utils.exec_get_all(conn, searchQuery, (searchedUsername,))[0][0]

    # if the user exists we continue
    if (searchedUserId):
        print("\tSuccessfully found " + searchedUsername)
        
        # search for the userID and determine following state
        followingQuery = """SELECT followeduserid FROM userfollowinguser WHERE
                            followinguserid = %s and followeduserid = %s"""
        followingId = utils.exec_get_all(conn, followingQuery, (utils.sessionToken, searchedUserId))
        if (followingId):
            followingString = "following"
            actionString = "unfollow"
        else:
            followingString = "not following"
            actionString = "follow"
        print("\tYou are " + followingString + " " + searchedUsername)

        # get a valid input
        while (True):
            action = input("\tWould you like to " + actionString + "? (y/n): ")
            if (action.lower() not in ("y", "n")):
                print("\tPlease enter (y)es (n)o")
                continue
            else:
                break
        
        # if they want to change the following state
        if (action.lower() == "y"):
            if (followingId): # here we want to unfollow
                actionSQL = """DELETE FROM userfollowinguser WHERE 
                            followeduserid = %s and followinguserid = %s"""
            else: # here we want to follow
                actionSQL = """INSERT INTO userfollowinguser 
                            (followeduserid, followinguserid) VALUES (%s, %s)"""
            utils.exec_commit(conn, actionSQL, (searchedUserId, utils.sessionToken))
        else:
            pass
    else:
        print("\tSorry, " + searchedUsername + "is not a member of MovieDB")


def help():
    print("*** COMMAND LINE INTERFACE MENU ***")
    for key in cliCommands:
        print(key + ": " + cliCommands[key]["helpText"])


def viewCollections(conn):
    userId = utils.sessionToken
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
    userId = utils.sessionToken
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
    "LOGOUT":
    {
        "helpText": "Logout of your account",
        "actionFunction": logout,
        "isDbAccessCommand" : False
    },
    "SEARCH":
    {
        "helpText": "Search for other users",
        "actionFunction": userSearch,
        "isDbAccessCommand" : True
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
    print("contain a symbol (!@#$%^&*()_+\-=\[\]'\\\|,.<>\/?)")
    print("contain no spaces")
    print("*******************************************************")