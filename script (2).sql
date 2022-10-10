
CREATE DATABASE UserDB;

USE UserDB;

create table users(
 userid int not null   auto_increment,
username varchar(256) not null,
email varchar(256) not null,
password varchar(1000) not null,
primary key(userid)
);
create table files(
fileid int  not null auto_Increment,
fileuri varchar(5000),
userid int,
primary key(fileid),
foreign key (userid) references users(userid)
);