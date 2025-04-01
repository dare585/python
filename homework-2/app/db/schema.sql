DROP TABLE IF EXISTS aws_config;

CREATE TABLE aws_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    aws_access_key_id TEXT UNIQUE NOT NULL,
    aws_secret_access_key TEXT NOT NULL,
    aws_session_token TEXT UNIQUE NOT NULL,
    aws_region TEXT NOT NULL,
    session_expiration TIMESTAMP NOT NULL
);