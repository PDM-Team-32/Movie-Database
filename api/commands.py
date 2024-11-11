import utils
from tabulate import tabulate
import datetime
import re

# TODO char limits on everything
# TODO attempt limit on while true loops
def createAccount(conn):
    print("Account Creation:")

    ###### Get an unused username ######
    while (True):
        username = input("\tProvide a Username: ")
        userCheckQuery = "SELECT username FROM users WHERE username = %s"
        results = utils.exec_get_one(conn, userCheckQuery, (username,))
        if (results):
            print("*** That username is taken! ***")
        else:
            break
    
    ###### Get an email address ######
    email = input("\tProvide an email address: ")
    while (not re.match(r"^\S+@\S+\.\S+$", email)):
        print("***" + email + " is not a valid email address ***")
        email = input("\tProvide a valid email address: ")
    
    ###### Get a valid password (see regex or passwordHelp) ######
    # TODO hash + salt in phase 3    
    passwordHelp()
    password = str(input("\tProvide a Password: "))
    while (not (
           (len(password) >= 8) and (len(password) <= 64) and 
           bool(re.search("[a-z]", password)) and
           bool(re.search("[A-Z]", password)) and
           bool(re.search(r"[!@#\$%\^&\*\(\)_\+\-\=\[\]\'\\\|,\.<>\?/]", password)) and
           bool((not re.search(" ", password))))):
        print("*** That was not a valid password ***")
        passwordHelp()
        password = str(input("\tProvide a Password: "))

    ###### Get remaining info (we don't really care abt this stuff) ######
    fName = input("\tProvide a First Name: ")
    lName = input("\tProvide a Last Name: ")
    currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

    ###### Insert the user into the DB ######
    sql = """INSERT INTO users 
            (firstname, lastname, email, username, password, creationdate, lastaccessdate) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)"""
    utils.exec_commit(conn, sql, (fName, lName, email, username, password, currentDatetime, currentDatetime))
    print("Welcome to MovieDB, please use the LOGIN command to access your account")


def login(conn):
    idPasswordQuery = "SELECT id, password FROM users where username = %s"
    id = ""
    expectedPassword = ""

    print("*** Note: To login, you must first create an account ***\n*** To exit the login command, enter 'exit' ***")

    ###### Ensure the account exists ######
    while (True):
        username = input("\tEnter your username: ")
        if (username.lower() == "exit"):
            return
        
        packedIdPassword = utils.exec_get_all(conn, idPasswordQuery, (username,))
        if (packedIdPassword): # unpack if we got a user
            id = packedIdPassword[0][0]
            expectedPassword = packedIdPassword[0][1]

        # Check user existing
        if (id):
            break
        else:
            print("*** Not an existing username ***\n*** Note: To login, you must first create an account ***")

    # for debugging, uncomment if you want to feel like a hacker
    # print("\texpected password: " + expectedPassword) 
    
    password = ""
    while (not (password == expectedPassword)):
        password = input("\t(" + username + ") Enter your password: ")
        if (password.lower() == "exit"): # note: exit is not a valid password (see createAccount())
            return
    
    ###### Update lastaccessdate ######
    datePrompt = "UPDATE users SET lastaccessdate = %s WHERE id = %s"
    currentDatetime = "'" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
    utils.exec_commit(conn, datePrompt, (currentDatetime, id))
    
    ###### User is now logged in ######
    print("Welcome back " + username)
    utils.sessionToken = int(id) # TODO change to DB sessionToken 
        
# TODO this needs to become a connected function to store sessionToken in DB
def logout():
    if (utils.sessionToken > 0):
        utils.sessionToken = -1
        print("*** You have logged out. Use LOGIN to login again ***")
    else:
        print("*** You need to LOGIN before you can LOGOUT ***")


# Idea here is a user will search for another user, and take respective following action
# We can also see others collections here, if we want to
def userSearch(conn):
    searchedEmail = input("\tPlease input an email to search: ")

    # search for the userId
    searchQuery = "SELECT id FROM users WHERE email = %s"
    searchedUserId = utils.exec_get_all(conn, searchQuery, (searchedEmail,))
    if (searchedUserId):
        searchedUserId = searchedUserId[0][0]

    # if the user exists we continue
    if (searchedUserId):
        print("\tSuccessfully found " + searchedEmail)
        
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
        print("\tYou are " + followingString + " " + searchedEmail)

        # get a valid input
        while (True):
            action = input("\tWould you like to " + actionString + "? (y/n): ")
            if (action.lower() not in ("y", "n")):
                print("\tPlease enter (y)es (n)o")
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
            # put future options here
            pass
    else:
        print("\tSorry, " + searchedEmail + " is not a member of MovieDB")


def help():
    print("*** COMMAND LINE INTERFACE MENU ***")
    for key in cliCommands:
        print(key + ": " + cliCommands[key]["helpText"])

def movieSearch(conn):
    searchArray = []
    sortByArray = []
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
    sorting = (input("(OPTIONAL) Select sort option [M]ovie name, [S]tudio, [G]enre, [R]elease Year (DEFAULT Movie Name): "))
    sortByArray.append(sorting)
    order = (input("(OPTIONAL) In [A]scending or [D]ecending order? (DEFAULT Ascending): "))
    sortByArray.append(order)
    orderByString = (makeOrderByString(sortByArray))
    
    sql = f"""
            SELECT
                DISTINCT (m.id),
                m.title,
                m.length,
                m.mpaa_rating,
                mp.releasedate,
                array(SELECT g.name
                    FROM genre AS g
                    INNER JOIN moviegenre AS mg On g.id = mg.genreid
                    WHERE mg.movieid = m.id) AS genres,
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
                    WHERE(m.id = cd.movieid)) AS directors,
                s.name
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
            INNER JOIN moviestudio as ms
                ON (ms.movieid = m.id)
            INNER JOIN studio as s
                ON (s.id = ms.studioid)
            WHERE( m.id = m.id
                    {"AND m.title = %s" if movieTitle != "" else ""}
                    {"AND mp.releasedate > TO_DATE(%s, 'YYYY:MM:DD')" if startDate != "" else ""}
                    {"AND mp.releasedate < TO_DATE(%s, 'YYYY:MM:DD')" if endDate != "" else ""}
                    {"AND cm.stagename = %s" if stageName != "" else ""}
                    {"AND rp.name = %s" if studio != "" else ""}
                    {"AND g.name = %s" if genre != "" else ""}
                    )
            ORDER BY {orderByString}"""
    output = utils.exec_get_all(conn, sql, tuple(searchArray))
    if (output): # if there are no results and we get a blank array, tabulate crashes
        formatted = formatMovieSearchOutput(conn, output)
        print(tabulate(formatted, headers=["ID", "Title", "Length", "Rating", "Release Date", "Genre", "Platform", "Actors", "Directors", "Studio", "Star Rating"], tablefmt='grid', maxcolwidths=[None, 13]))
    else:
        print("No results found")

def getMovieUserRating(conn, movieId):
    sql = """
    SELECT AVG(urm.starrating)::int
    FROM userratesmovie AS urm
    INNER JOIN movie as m
        ON(m.id = urm.movieid)
    WHERE m.id = %s"""
    output = utils.exec_get_one(conn, sql, (movieId,))[0]
    if output == None:
        output = "No ratings"
    return output

def makeOrderByString(array):
    if array[0] in orderByCommands["Selection"].keys():
        selection = orderByCommands["Selection"][array[0]]
    else:
        print("Invalid sort selection will default to movie name")
        selection = orderByCommands["Selection"]["M"]
    if array[1] in orderByCommands["Qualifier"].keys():
        qualifier = orderByCommands["Qualifier"][array[1]]
    else:
        print("Invalid sort selection will default to movie name")
        qualifier = orderByCommands["Selection"]["A"]
    return(selection + " " + qualifier)

def watchCollection(conn):
    collectionName = (input("Give the name of the collection you want to watch: "))
    sql = """SELECT
                CURRENT_TIMESTAMP::timestamp AS currentTime,
                umc.id,
                m.id,
                m.length
            FROM movieCollection AS mc
            INNER JOIN userMovieCollection AS umc
            ON (umc.id = mc.collectionid)
            INNER JOIN movie AS m
            ON (m.id = mc.movieid)
            WHERE umc.name = %s AND umc.userid = %s"""
    movies = utils.exec_get_all(conn, sql, (collectionName, utils.sessionToken))
    startTime = movies[0][0]
    endTime = movies[0][0]
    for movie in movies:
        time_change = datetime.timedelta(minutes=movie[3]) 
        endTime = startTime + time_change
        sql = """INSERT INTO userWatchesMovie (movieId, userId, startTime, endTime) VALUES (%s, %s, %s, %s)"""
        utils.exec_commit(conn, sql, (movie[2], utils.sessionToken, startTime, endTime))
        startTime = endTime



def formatMovieSearchOutput(conn, input):
    output = list(input)
    for x in range(0, len(output)):
        # id = output[x][0] # get the id 
        # output[x] = list(output[x][1:]) # kill the id for outputting
        #output[x][4] = formatArrayToTallString(output[x][4])
        output[x][5] = formatArrayToTallString(output[x][5])
        output[x][6] = formatArrayToTallString(output[x][6])
        output[x][7] = formatArrayToTallString(output[x][7])
        output[x][8] = formatArrayToTallString(output[x][8])
        output[x].append(getMovieUserRating(conn, id))
    return output
        

def formatArrayToTallString(array):
    outString = ""
    for x in array:
        outString += x + "\n"
    return outString

def collectionCount(conn):
    userId = utils.sessionToken
    sql = """SELECT
                COUNT(umc.name)
            FROM userMovieCollection AS umc
            WHERE  userId = %s;"""
    count = utils.exec_get_one(conn, sql, (userId,))
    print("You have " + str(count[0]) + " collections!")


def viewCollections(conn):
    userId = utils.sessionToken
    sql = """SELECT
                umc.name,
                COUNT(m.title),
                TO_CHAR(SUM(length)*'1 minute'::interval, 'HH24:MI')
            FROM userMovieCollection AS umc
            LEFT JOIN movieCollection AS mc
                ON (umc.id = mc.collectionid)
            LEFT JOIN movie AS m
                        ON (m.id = mc.movieid)
            WHERE  userId = %s
            GROUP BY umc.name
            ORDER BY umc.name; """
    movies = list(utils.exec_get_all(conn, sql, (userId,)))
    for x in range(len(movies)):
        if movies[x][2] == None:
            movies[x] = [movies[x][0], movies[x][1], "00:00"]
    print(tabulate(movies, headers=["Name", "Movie Count", "Collection Length"], tablefmt='orgtbl'))

def createMovieCollection(conn):
    userId = utils.sessionToken
    collectionName = input("Name your new collection: ")
    collectionCheckQuery = "SELECT Id FROM UserMovieCollection WHERE UserId = %s and name = %s"
    results = utils.exec_get_one(conn, collectionCheckQuery, (userId, collectionName,))
    if results:
        print("*** You already have a collection named that ***")
        return
    sql = """INSERT INTO userMovieCollection (userId, name) VALUES (%s, %s)"""
    utils.exec_commit(conn, sql, (userId, collectionName))


def getTopTenMovies(conn):
    userId = utils.sessionToken
    sql = """SELECT
                m.title,
                urm.starrating
            FROM movie AS m
                INNER JOIN userRatesMovie AS urm
            ON(urm.movieid = m.id)
            WHERE  urm.userId = %s
            ORDER BY urm.starrating DESC
            LIMIT 10;"""
    movies = utils.exec_get_all(conn, sql, (userId,))
    print(tabulate(movies, headers=["Title", "Rating"], tablefmt='grid'))

def getTopTwentyMoviesAmongFollowers(conn):
    userId = utils.sessionToken
    sql = """SELECT
                m.title,
                COUNT(uwm.movieid) AS views
            FROM movie AS m
            INNER JOIN userwatchesmovie AS uwm
                ON(uwm.movieid = m.id)
            WHERE (uwm.userId IN (SELECT followinguserid FROM userfollowinguser WHERE followeduserid = %s ))
            GROUP BY m.title
            ORDER BY views DESC, m.title ASC
            LIMIT 20;"""
    movies = utils.exec_get_all(conn, sql, (userId,))
    print(tabulate(movies, headers=["Title", "Rating"], tablefmt='grid'))


def recommendedMovies(conn):
    userId = utils.sessionToken
    sql = """SELECT
                m.title,
                COUNT(uwm.movieid) AS views
            FROM movie AS m
            INNER JOIN userwatchesmovie AS uwm
                ON(uwm.movieid = m.id)
            WHERE (uwm.endtime > current_date - interval '90' day)
            GROUP BY m.title
            ORDER BY views DESC
            LIMIT 20;"""
    movies = utils.exec_get_all(conn, sql, (userId,))
    print(tabulate(movies, headers=["Title", "Views"], tablefmt='orgtbl'))


def topNewReleases(conn):
    userId = utils.sessionToken
    sql = """SELECT
                m.title,
                COUNT(uwm.movieid) AS views
            FROM movie AS m
            INNER JOIN userwatchesmovie AS uwm
                ON(uwm.movieid = m.id)
            INNER JOIN movieplatform AS mp
                ON(mp.movieid = m.id)
            WHERE (mp.releasedate > current_date - interval '30' day)
            GROUP BY m.title
            ORDER BY views DESC, m.title ASC
            LIMIT 5;"""
    movies = utils.exec_get_all(conn, sql, (userId,))
    print(tabulate(movies, headers=["Title", "Views"], tablefmt='orgtbl'))

def startMovie(conn):
    userId = utils.sessionToken
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
    userId = utils.sessionToken
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
    userId = utils.sessionToken
    movieId = input("Enter the ID of the movie to rate: ")

    sql = """SELECT title
            FROM movie AS m
            WHERE m.id = %s AND m.id IN (SELECT movieid
                                        FROM userwatchesmovie
                                        WHERE  userid = %s AND movieid NOT IN (SELECT movieid
                                                                            FROM userratesmovie
                                                                            WHERE userid = %s))"""
    movie = utils.exec_get_one(conn, sql, (movieId, utils.sessionToken, utils.sessionToken))

    if movie:
        rating = input("Enter a star rating from 1 to 5: ")
        if int(rating) < 1 or int(rating) > 5:
            print("Invalid rating.")
        else:
            sql = """INSERT INTO userRatesMovie (movieId, userId, starRating) VALUES (%s, %s, %s)"""
            utils.exec_commit(conn, sql, (movieId, userId, rating))
    else:
        print("You cannot rate a movie that does not exist or that you have already rated.")

def changeCollectionName(conn):
    userId = utils.sessionToken
    collectionName = input("Select the collection you want to rename: ")
    collectionCheckQuery = "SELECT Id FROM UserMovieCollection WHERE UserId = %s and name = %s"
    collectionId = utils.exec_get_one(conn, collectionCheckQuery, (userId, collectionName,))
    if collectionId:
        collectionName = input("Enter new name: ")
        sql = """SELECT id FROM usermoviecollection WHERE name = %s"""
        duplicateNames = utils.exec_get_one(conn, sql, (collectionName,))
        if duplicateNames == None:
            collectionUpdate = "UPDATE UserMovieCollection SET Name = %s WHERE Id = %s"
            utils.exec_commit(conn, collectionUpdate, (collectionName, collectionId))
        else:
            print("Collection name already exists please try a different name")
    else:
        print("*** Collection not found or is not yours ***")
    
    
def addMovieToCollection(conn):
    userId = utils.sessionToken
    print("*** Type QUIT to stop ***")
    while (True):
        collectionName = input("Name of collection: ")
        if collectionName.casefold() == "QUIT".casefold():
            return       
        collectionCheckQuery = "SELECT Name FROM UserMovieCollection WHERE name = %s"
        results = utils.exec_get_one(conn, collectionCheckQuery, (collectionName,))
        if (results):
            accesCheckQuery = "SELECT Id FROM UserMovieCollection WHERE UserId = %s and name = %s"
            collectionId = utils.exec_get_one(conn, accesCheckQuery, (userId, collectionName,))
            if(collectionId):
                break
            else:
                print("*** You Do Not Own That Collection ***")
        else:
            print("*** Collection not found ***")
    while (True):
        print("*** Type QUIT to stop ***")
        movieTitle = input("Title of movie: ")
        if movieTitle.casefold() == "QUIT".casefold():
            return       
        movieCheckQuery = "SELECT id FROM Movie WHERE Title = %s"
        movieId = utils.exec_get_all(conn, movieCheckQuery, (movieTitle,))
        if (movieId):
            if len(movieId)>1:
                for i in range(len(movieId)):
                    movieQuery = "SELECT Title FROM Movie WHERE id = %s"
                    movie = utils.exec_get_one(conn, movieQuery, (movieId[i],))
                    dateQuery = "SELECT ReleaseDate FROM MoviePlatform WHERE MovieId = %s"
                    date = utils.exec_get_one(conn, dateQuery, (movieId[i],))
                    print(f"{i} {movie[0]} {format(date[0])}")
                index = -1
                while(index<0 or index>(len(movieId))):
                    index = input("Enter the number of the movie you want: ")
                    try:
                        index = int(index)
                    except ValueError:
                        index = -1
                        print("*** Invalid number ***")
            else:
                index = 0
            try:
                insert = "INSERT INTO MovieCollection (MovieId, CollectionId) VALUES (%s, %s)"
                utils.exec_commit(conn, insert, (movieId[index], collectionId,))
            except Exception:
                curs = conn.cursor()
                curs.execute("ROLLBACK")
                conn.commit()
                print("*** Already in collection ***")
        else:
            print("*** Movie not found ***")

def removeMovieFromCollection(conn):
    userId = utils.sessionToken
    print("*** Type QUIT to stop ***")
    while (True):
        collectionName = input("Name of collection: ")
        if collectionName.casefold() == "QUIT".casefold():
            return       
        collectionCheckQuery = "SELECT Name FROM UserMovieCollection WHERE name = %s"
        results = utils.exec_get_one(conn, collectionCheckQuery, (collectionName,))
        if (results):
            accesCheckQuery = "SELECT Id FROM UserMovieCollection WHERE UserId = %s and name = %s"
            collectionId = utils.exec_get_one(conn, accesCheckQuery, (userId, collectionName,))
            if(collectionId):
                break
            else:
                print("*** You Do Not Own That Collection ***")
        else:
            print("*** Collection not found ***")
    while (True):
        print("*** Type QUIT to stop ***")
        movieTitle = input("Title of movie: ")
        if movieTitle.casefold() == "QUIT".casefold():
            return       
        movieCheckQuery = "SELECT id FROM Movie WHERE Title = %s"
        movieId = utils.exec_get_all(conn, movieCheckQuery, (movieTitle,))
        if (movieId):
            if len(movieId)>1:
                for i in range(len(movieId)):
                    movieQuery = "SELECT Title FROM Movie WHERE id = %s"
                    movie = utils.exec_get_one(conn, movieQuery, (movieId[i],))
                    dateQuery = "SELECT ReleaseDate FROM MoviePlatform WHERE MovieId = %s"
                    date = utils.exec_get_one(conn, dateQuery, (movieId[i],))
                    print(f"{i} {movie[0]} {format(date[0])}")
                index = -1
                while(index<0 or index>(len(movieId))):
                    index = input("Enter the number of the movie you want: ")
                    try:
                        index = int(index)
                    except ValueError:
                        index = -1
                        print("*** Invalid number ***")
            else:
                index = 0
            movieCheckQuery = "SELECT MovieId FROM MovieCollection WHERE MovieId = %s AND CollectionId = %s"
            results = utils.exec_get_one(conn, movieCheckQuery, (movieId[index], collectionId,))
            if results:
                delete = "DELETE FROM MovieCollection WHERE MovieId = %s AND CollectionId = %s"
                utils.exec_commit(conn, delete, (movieId[index], collectionId,))
                print("*** Deleted ***")
            else:
                print("*** Movie not in Collection ***")

        else:
            print("*** Movie not found ***")

def deleteCollection(conn):
    userId = utils.sessionToken
    print("*** Type QUIT to stop ***")
    while (True):
        collectionName = input("Name of collection: ")
        if collectionName.casefold() == "QUIT".casefold():
            return       
        collectionCheckQuery = "SELECT Name FROM UserMovieCollection WHERE name = %s"
        results = utils.exec_get_one(conn, collectionCheckQuery, (collectionName,))
        if (results):
            accesCheckQuery = "SELECT Id FROM UserMovieCollection WHERE UserId = %s and name = %s"
            collectionId = utils.exec_get_one(conn, accesCheckQuery, (userId, collectionName,))
            if(collectionId):
                break
            else:
                print("*** You Do Not Own That Collection ***")
        else:
            print("*** Collection not found ***")
    delete = "DELETE FROM MovieCollection WHERE CollectionId = %s"
    utils.exec_commit(conn, delete, (collectionId,))
    delete = "DELETE FROM UserMovieCollection WHERE Id = %s"
    utils.exec_commit(conn, delete, (collectionId,))
    print("*** Deleted ***")

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
    "USER_SEARCH":
    {
        "helpText": "Search for other users to follow or unfollow",
        "actionFunction": userSearch,
        "isDbAccessCommand" : True
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
    "COLLECTION_COUNT":
    {
        "helpText": "Get the number of collections you own",
        "actionFunction": collectionCount,
        "isDbAccessCommand": True
    },
    "RECOMMENDED_MOVIES":
    {
        "helpText": "View the top 20 most viewed movies in the last 90 days",
        "actionFunction": recommendedMovies,
        "isDbAccessCommand": True
    },
    "NEW_RELEASES":
    {
        "helpText": "View the top 5 releases of this month",
        "actionFunction": topNewReleases,
        "isDbAccessCommand": True
    },
    "GET_TOP_TEN":
    {
        "helpText": "See your top ten favorite movies according to your ratings",
        "actionFunction": getTopTenMovies,
        "isDbAccessCommand": True
    },
    "FOLLOWER_FAVORITES":
    {
        "helpText": "See your top 20 favorite movies based on your followers watch history",
        "actionFunction": getTopTwentyMoviesAmongFollowers,
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
    "WATCH_COLLECTION" :
    {
        "helpText": "Binge your movie collections!",
        "actionFunction": watchCollection,
        "isDbAccessCommand": True
    },
    "CHANGE_COLLECTION_NAME" :
    {
        "helpText": "Change the name of a collection you own",
        "actionFunction": changeCollectionName,
        "isDbAccessCommand": True
    },
    "ADD_MOVIE_TO_COLLECTION" :
    {
        "helpText": "Add a movie to a collection you own",
        "actionFunction": addMovieToCollection,
        "isDbAccessCommand": True
    },
    "REMOVE_MOVIE_FROM_COLLECTION" :
    {
        "helpText": "Remove a movie to a collection you own",
        "actionFunction": removeMovieFromCollection,
        "isDbAccessCommand": True
    },
    "DELETE_COLLECTION" :
    {
        "helpText": "Delete a collection you own",
        "actionFunction": deleteCollection,
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

orderByCommands = {
        "Selection":
        {
            "M": "m.title",
            "S": "s.name",
            "G": "g.name",
            "R": "mp.releasedate",
            "": "m.title"
        },
        "Qualifier":
        {
            "A": "ASC",
            "D": "DESC",
            "": "ASC"
        }
    }

###### Helper funcs ######

## Password helper 
# length [8, 64]
# contains a lowercase letter
# contains a capital letter
# contains a number
# contains a symbol
# does not contain a space
def passwordHelp():
    print("**************** Password Requirements ****************")
    print("8 to 64 characters long")
    print("contain a lowercase letter")
    print("contain a capital letter")
    print("contain a number")
    print("contain a symbol (!@#$%^&*()_+-=[]'\\|,.<>/?)")
    print("contain no spaces")
    print("*******************************************************")


def salt():
    # TODO dont forget to add salt to users table
    print("SALT IS NOT IMPLEMENTED YET")