CREATE TABLE Users(
    id SERIAL PRIMARY KEY,
    FirstName VARCHAR(32) NOT NULL,
    LastName VARCHAR(32) NOT NULL,
    Email VARCHAR(320) NOT NULL,
    UserName VARCHAR(32) NOT NULL UNIQUE,
    Password VARCHAR(64) NOT NULL,
    CreationDate DATE NOT NULL,
    LastAccessDate DATE NOT NULL,
    Salt VARCHAR(32)
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
    Name VARCHAR(128) DEFAULT 'My Collection'
);

CREATE TABLE MovieGenre(
    MovieId INT NOT NULL,
    GenreId INT NOT NULL,
    CONSTRAINT "MovieGenre_PK"
        PRIMARY KEY (MovieId, GenreId),
    FOREIGN KEY (GenreId) REFERENCES Genre(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE MoviePlatform(
    MovieId INT NOT NULL,
    PlatformID INT NOT NULL,
    CONSTRAINT "MoviePlatform_PK"
        PRIMARY KEY (MovieId, PlatformID),
    FOREIGN KEY (PlatformID) REFERENCES ReleasePlatform(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    ReleaseDate DATE NOT NULL
);

CREATE TABLE UserWatchesMovie(
    MovieId INT NOT NULL,
    UserId INT NOT NULL,
    StartTime TIMESTAMP NOT NULL,
    CONSTRAINT "UserWatchesMovie_PK"
        PRIMARY KEY (MovieId, UserId, StartTime),
    FOREIGN KEY (UserId) REFERENCES Users(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    EndTime TIMESTAMP DEFAULT NULL
);

CREATE TABLE UserRatesMovie(
    MovieId INT NOT NULL,
    UserId INT NOT NULL,
    CONSTRAINT "UserRatesMovie_pk"
        PRIMARY KEY (MovieId, UserId),
    FOREIGN KEY (UserId) REFERENCES Users(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id),
    StarRating INT NOT NULL
);

CREATE TABLE MovieCollection(
    MovieId INT NOT NULL,
    CollectionId INT NOT NULL,
    CONSTRAINT "MovieCollection_pk"
        PRIMARY KEY (MovieId, CollectionId),
    FOREIGN KEY (CollectionId) REFERENCES UserMovieCollection(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE UserFollowingUser(
    FollowedUserId INT NOT NULL,
    FollowingUserId INT NOT NULL,
    CONSTRAINT "UserFollowingUser_pk"
        PRIMARY KEY (FollowedUserId, FollowingUserId),
    CONSTRAINT CU1 CHECK(FollowedUserId != FollowingUserId),
    FOREIGN KEY (FollowedUserId) REFERENCES Users(id),
    FOREIGN KEY (FollowingUserId) REFERENCES Users(id)
);

CREATE TABLE CastDirects(
    CastId INT NOT NULL,
    MovieId INT NOT NULL,
    CONSTRAINT "CastDirects_pk"
        PRIMARY KEY (CastId, MovieId),
    FOREIGN KEY (CastId) REFERENCES CastMember(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE CastActs(
    CastId  INT NOT NULL,
    MovieId INT NOT NULL,
    CONSTRAINT "CastActs_pk"
        PRIMARY KEY (CastId, MovieId),
    FOREIGN KEY (CastId) REFERENCES CastMember(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);

CREATE TABLE MovieStudio(
    StudioId INT NOT NULL,
    MovieId INT NOT NULL,
    CONSTRAINT "MovieStudio_pk"
        PRIMARY KEY (StudioId, MovieId),
    FOREIGN KEY (StudioId) REFERENCES Studio(id),
    FOREIGN KEY (MovieId) REFERENCES Movie(id)
);
