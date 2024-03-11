USE ssn_new;


CREATE TABLE users(
    author_id VARCHAR(35) PRIMARY KEY,
    staff_name VARCHAR(50),
    email_id VARCHAR(35) UNIQUE,
    passkey VARCHAR(100)
);

create table adminusers(
	staff_name varchar(50),
    email_id varchar(50) PRIMARY KEY,
    passkey varchar(100)
    );

show tables;

alter table adminusers add constraint pk_email_id PRIMARY KEY(email_id);
alter table users add constraint unique_email_id UNIQUE(email_id);
