USE ssn_new;


CREATE TABLE users(
    author_id VARCHAR(35) PRIMARY KEY,
    staff_name VARCHAR(50),
    email_id VARCHAR(35),
    passkey VARCHAR(100)
);

show tables;