drop table if exists fileset;
drop table if exists donut_log;
drop table if exists pick_log;

create table fileset (
    fid INTEGER primary key autoincrement,
    md5 TEXT not null,
    name TEXT not null
);
create table donut_log (
    did INTEGER primary key autoincrement,
    bake_time NUMBERIC not null,
    size_grade INTEGER not null,
    ip TEXT not null
);
create table pick_log (
    pid INTEGER primary key autoincrement,
    pick_time NUMBERIC not null,
    ip TEXT not null
);
