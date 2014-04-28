DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS snaps;
CREATE TABLE users (username text, passwordhash int, user_role int, sync text);
CREATE TABLE sessions (username text, session text, date text);
CREATE TABLE snaptime (username text, time_stamp text, snapshot text);
INSERT INTO users (username, passwordhash, user_role, sync) VALUES ("admin", '58acb7acccce58ffa8b953b12b5a7702bd42dae441c1ad85057fa70b', 1, 'text');