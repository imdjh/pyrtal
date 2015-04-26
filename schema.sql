drop table if exists fileset;
drop table if exists audit_log;

create table fileset (
    fid INTEGER primary key autocrement,
    md5 TEXT not null,
    name TEXT not null
)
create table audit_log (
    pid INTEGER primary key autocrement,
    fin_time NUMERIC not null,
    size_grade INTEGER not null
)
