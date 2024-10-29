import utils
from tabulate import tabulate


def createAccount(conn):
    print("Account Creation")


def login(conn):
    print("Login")


def help():
    print("*** COMMAND LINE INTERFACE MENU ***")
    for key in cliCommands:
        print(key + ": " + cliCommands[key]["helpText"])

def movieSearch(conn):
    searchArray = []
    movieTitle = (input("(OPTIONAL) Provide a movie title to search for: "))
    if movieTitle != "":
        searchArray.append(movieTitle)
    startDate = (input("(OPTIONAL) Provide the lower bounds for the date YYYY:MM:DD: "))
    if startDate != "":
        searchArray.append(startDate)
    endDate = (input("(OPTIONAL) Provide the upper bounds for the date YYYY:MM:DD: "))
    if endDate != "":
        searchArray.append(endDate)
    stageName = (input("(OPTIONAL) Provide the stage name of a cast member from the movie: "))
    if stageName != "":
        searchArray.append(stageName)
    studio = (input("(OPTIONAL) Provide the name of the studio which produced the movie: "))
    if studio != "":
        searchArray.append(studio)
    genre = (input("(OPTIONAL) Provide the genre of the movie: "))
    if genre != "":
        searchArray.append(genre)
    sql = f"""
            SELECT
                DISTINCT (m.id),
                m.title,
                m.length,
                m.mpaa_rating,
                mp.releasedate,
                array(SELECT rp.name
                    FROM movieplatform AS mp
                    INNER JOIN releaseplatform AS rp ON mp.platformid = rp.id
                    WHERE(m.id = mp.movieid)) AS platform,
                array(SELECT cm.stagename
                    FROM castmember AS cm
                    INNER JOIN castacts AS ca ON ca.castid = cm.id
                    WHERE(m.id = ca.movieid)) AS actors,
                array(SELECT cm.stagename
                    FROM castmember AS cm
                    INNER JOIN castdirects AS cd ON cd.castid = cm.id
                    WHERE(m.id = cd.movieid)) AS directors
            FROM movie AS m
            INNER JOIN movieplatform AS mp
                ON (mp.movieid = m.id)
            INNER JOIN releaseplatform AS rp
                ON (rp.id = mp.platformid)
            INNER JOIN castacts AS ca
                ON (ca.movieid = m.id)
            INNER JOIN castdirects AS cd
                ON (cd.movieid = m.id)
            INNER JOIN castmember AS cm
                ON (cd.castid = cm.id OR ca.castid = cm.id)
            INNER JOIN moviegenre AS mg
                ON (mg.movieid = m.id)
            INNER JOIN genre as g
                ON (g.id = mg.genreid)
            WHERE( m.id = m.id
                    {"AND m.title = %s" if movieTitle != "" else ""}
                    {"AND mp.releasedate > TO_DATE(%s, 'YYYY:MM:DD')" if startDate != "" else ""}
                    {"AND mp.releasedate < TO_DATE(%s, 'YYYY:MM:DD')" if endDate != "" else ""}
                    {"AND cm.stagename = %s" if stageName != "" else ""}
                    {"AND rp.name = %s" if studio != "" else ""}
                    {"AND g.name = %s" if genre != "" else ""}
                    
                    );"""
    output = utils.exec_get_all(conn, sql, tuple(searchArray))
    formatted = formatMovieSearchOutput(output)
    print(tabulate(formatted, headers=["ID", "Title", "Length", "Rating", "Release Date", "Platform", "Actors", "Directors"], tablefmt='grid'))


def formatMovieSearchOutput(input):
    output = list(input)
    for x in range(len(output)):
        output[x] = list(output[x])
        output[x][5] = formatArrayToTallString(output[x][5])
        output[x][6] = formatArrayToTallString(output[x][6])
        output[x][7] = formatArrayToTallString(output[x][7])
    return output
        

def formatArrayToTallString(array):
    outString = ""
    for x in array:
        outString += x + "\n"
    return outString

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
    "MOVIE_SEARCH":
    {
        "helpText": "Search for movie with given criteria",
        "actionFunction": movieSearch,
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