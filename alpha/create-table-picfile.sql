drop table if exists picfile;
create table picfile (
    item_id int primary key,
    filename varchar(50),
    foreign key (item_id) references item(item_id) 
        on delete cascade on update cascade
);