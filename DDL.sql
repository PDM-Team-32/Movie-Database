CREATE TABLE Users(
    id SERIAL PRIMARY KEY,
    FirstName VARCHAR(32) NOT NULL,
    LastName VARCHAR(32) NOT NULL,
    Email VARCHAR(320) NOT NULL,
    UserName VARCHAR(32) NOT NULL,
    Password INT NOT NULL,
    CreationDate DATE NOT NULL,
    LastAccessDate DATE NOT NULL
);

CREATE TABLE Studio(
    id SERIAL PRIMARY KEY,
    Name VARCHAR(64) NOT NULL
);

CREATE TABLE CastMember(
    id SERIAL PRIMARY KEY,
    FirstName VARCHAR(32) NOT NULL,
    LastName VARCHAR(32) NOT NULL,
    StageName VARCHAR(32) DEFAULT NULL
);

CREATE TABLE Movie(
    id SERIAL PRIMARY KEY,
    Title VARCHAR(256) NOT NULL,
    MPAA_Rating VARCHAR(5) NOT NULL,
    CONSTRAINT CC1 CHECK(MPAA_Rating IN ('Unrated', 'G', 'PG', 'PG-13', 'R', 'NC-17')),
    Length Int NOT NULL
);

CREATE TABLE Genre(
    id SERIAL PRIMARY KEY,
    Name VARCHAR(30) NOT NULL
);

CREATE TABLE ReleasePlatform(
    id SERIAL PRIMARY KEY,
    Name VARCHAR(30) NOT NULL
);

CREATE TABLE UserMovieCollection(
    id SERIAL PRIMARY KEY,
    UserId INT NOT NULL,
    FOREIGN KEY (UserId)   REFERENCES Users(id),
    Name VARCHAR(30) DEFAULT 'My Collection'
);

CREATE TABLE MovieGenre(
    MovieId INT PRIMARY KEY,
    GenreId INT PRIMARY KEY,
    FOREIGN KEY (GenreId) REFERENCES Genre(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE MoviePlatform(
    MovieId INT PRIMARY KEY,
    PlatformID INT PRIMARY KEY,
    FOREIGN KEY (PlatformID) REFERENCES ReleasePlatform(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    ReleaseDate DATE NOT NULL
);

CREATE TABLE UserWatchesMovie(
    MovieId INT PRIMARY KEY,
    UserId INT PRIMARY KEY,
    FOREIGN KEY (UserId) REFERENCES Users(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    StartTime TIMESTAMP NOT NULL,
    EndTime TIMESTAMP DEFAULT NULL
);

CREATE TABLE UserRatesMovie(
    MovieId INT PRIMARY KEY,
    UserId INT PRIMARY KEY,
    FOREIGN KEY (UserId) REFERENCES Users(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    StarRating INT NOT NULL
);

CREATE TABLE MovieCollection(
    MovieId INT PRIMARY KEY,
    CollectionId INT PRIMARY KEY,
    FOREIGN KEY (CollectionId) REFERENCES UserMovieCollection(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE UserFollowingUser(
    FollowedUserId INT PRIMARY KEY,
    FollowingUserId INT PRIMARY KEY,
    FOREIGN KEY (FollowedUserId) REFERENCES Users(id),
    FOREIGN KEY (FollowingUserId) REFERENCES Users(id)
);

CREATE TABLE CastDirects(
    CastId INT PRIMARY KEY,
    MovieId INT PRIMARY KEY,
    FOREIGN KEY (CastId) REFERENCES CastMember(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE CastActs(
    CastId INT PRIMARY KEY,
    MovieId INT PRIMARY KEY,
    FOREIGN KEY (CastId) REFERENCES CastMember(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE MovieStudio(
    StudioId INT PRIMARY KEY,
    MovieId INT PRIMARY KEY,
    FOREIGN KEY (StudioId) REFERENCES Studio(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);