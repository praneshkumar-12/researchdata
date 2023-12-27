USE ssn_new;


CREATE TABLE users(
    author_id VARCHAR(35) PRIMARY KEY,
    staff_name VARCHAR(50),
    email_id VARCHAR(35),
    passkey VARCHAR(100)
);

create table adminusers(
	staff_name varchar(50),
    email_id varchar(50),
    passkey varchar(100)
    );

show tables;