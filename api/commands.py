

def createAccount():
    print("Account Creation")

def login():
    print("Login")

def help():
    print("*** COMMAND LINE INTERFACE MENU ***")
    for key in cliCommands:
        print(key + ": " + cliCommands[key]["helpText"])

def createMovieCollection():
    print("Create Movie Collection")

def quit():
    raise Exception("The QUIT command has no related function, something is wrong")


# This must be at the bottom of this file so that the functions are declared before assignment.
cliCommands = {
    "CREATE_ACCOUNT": 
    {
        "helpText": "Create your new account",
        "actionFunction": createAccount
    }, 
    "LOGIN":
    {
        "helpText": "Login to your account",
        "actionFunction": login
    },
    "CREATE_COLLECTION" :
    {
        "helpText": "Create a new (empty) Movie Collection",
        "actionFunction": createMovieCollection
    },
    "HELP":
    {
        "helpText": "Print this menu again",
        "actionFunction": help
    },
    "QUIT": 
    {
        "helpText": "Exit this application",
        "actionFunction": quit
    }
}