drop table if exists contacts;
create table contacts (
    id integer primary key autoincrement,
    firstname string not null,
    middlename string,
    lastname string not null,
    address string,
    phone string,
    email string
);
