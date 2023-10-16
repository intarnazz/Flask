CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER,
    post TEXT NOT NULL,
    img BLOB,
    tred_true INTEGER,
    type TEXT,
    PRIMARY KEY("post_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS treds (
    tred_id INTEGER,
    tred TEXT NOT NULL,
    URL TEXT,
    img BLOB,
    PRIMARY KEY("tred_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS users (
    loggin TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    ava BLOB,
    id_user INTEGER NOT NULL UNIQUE,
    PRIMARY KEY("id_user" AUTOINCREMENT)
);