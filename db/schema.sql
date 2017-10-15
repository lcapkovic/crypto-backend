drop table if exists submissions;
    create table submissions (
    id integer primary key autoincrement,
    problemId integer not null,
    answer text not null,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    correct integer not null
);