import utils
from tabulate import tabulate
import datetime

def createAccount(conn):
    print("Account Creation")


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


def startMovie(conn):
    userId = input("Provide a user ID (this is temporary until we create a login and track current userId): ")
    movieId = input("Enter the ID of your movie: ")

    sql = """SELECT title FROM movie WHERE movie.id = %s"""
    movie = utils.exec_get_one(conn, sql, (movieId,))

    if movie:
        currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
        sql = """INSERT INTO userWatchesMovie (movieId, userId, startTime) VALUES (%s, %s, %s)"""
        utils.exec_commit(conn, sql, (movieId, userId, currentDatetime))
    else:
        print("You cannot view a movie that does not exist.")


def endMovie(conn):
    userId = input("Provide a user ID (this is temporary until we create a login and track current userId): ")
    movieId = input("Enter the ID of your movie: ")

    sql = """SELECT startTime FROM userWatchesMovie AS uwm WHERE uwm.userId = %s AND uwm.movieId = %s"""
    movie = utils.exec_get_one(conn, sql, (userId, movieId))

    if movie:
        currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
        sql = """UPDATE userWatchesMovie AS uwm SET endTime = %s WHERE uwm.movieId = %s AND uwm.userId = %s"""
        utils.exec_commit(conn, sql, (currentDatetime, movieId, userId))
    else:
        print("You have not begun viewing this movie.")


def rateMovie(conn):
    userId = input("Provide a user ID (this is temporary until we create a login and track current userId): ")
    movieId = input("Enter the ID of the movie to rate: ")

    sql = """SELECT title FROM movie WHERE movie.id = %s"""
    movie = utils.exec_get_one(conn, sql, (movieId,))

    if movie:
        rating = input("Enter a star rating from 1 to 5: ")
        if int(rating) < 1 or int(rating) > 5:
            print("Invalid rating.")
        else:
            sql = """INSERT INTO userRatesMovie (movieId, userId, starRating) VALUES (%s, %s, %s)"""
            utils.exec_commit(conn, sql, (movieId, userId, rating))
    else:
        print("You cannot rate a movie that does not exist.")


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
    "START_MOVIE" :
    {
        "helpText": "Begin viewing a movie",
        "actionFunction": startMovie,
        "isDbAccessCommand": True
    },
    "END_MOVIE" :
    {
        "helpText": "Finish viewing a movie",
        "actionFunction": endMovie,
        "isDbAccessCommand": True
    },
    "RATE_MOVIE" :
    {
        "helpText": "Give a movie a star rating (1-5)",
        "actionFunction": rateMovie,
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