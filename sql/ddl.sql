CREATE DATABASE ssn_new;

USE ssn_new;

show tables;

-- select * from auth_user;

-- DROP TABLE publications;

CREATE TABLE publications
  (
	 uniqueid            VARCHAR(100) PRIMARY KEY,
     title               VARCHAR(500) NOT NULL,
     start_academic_month VARCHAR(10),
     start_academic_year YEAR,
     end_academic_month  VARCHAR(10),
     end_academic_year   YEAR,
     first_author        VARCHAR(50) NOT NULL,
     second_author       VARCHAR(50),
     third_author        VARCHAR(50),
     other_authors       VARCHAR(500),
     is_student_author   VARCHAR(10),
     student_name        VARCHAR(50),
     student_batch       VARCHAR(10),
     specification       VARCHAR(30),
     publication_type    VARCHAR(30),
     publication_name    VARCHAR(500),
     publisher           VARCHAR(100),
     year_of_publishing  YEAR,
     month_of_publishing VARCHAR(10),
     volume              INT,
     page_number         VARCHAR(100),
     indexing            VARCHAR(100),
     quartile            VARCHAR(10),
     citation            INT,
     doi                 VARCHAR(500),
     front_page_path     VARCHAR(500),
     url                 VARCHAR(500),
     ISSN                VARCHAR(500)
  );

-- ALTER TABLE publications ADD( CONSTRAINT pk_uniqueid PRIMARY KEY(uniqueid),
-- CONSTRAINT chk_quartile CHECK (quartile IN ('Q1', 'Q2', 'Q3', 'Q4')));

-- ALTER TABLE publications ADD COLUMN specification VARCHAR(50);
-- ALTER TABLE publications ADD COLUMN url VARCHAR(100);
-- ALTER TABLE publications ADD COLUMN ISSN VARCHAR(50);

desc publications;

select * from publications; 

-- update publications set issn=NULL where title='Assurance on data integrity in cloud data centre using PKI built RDIC method';

-- select doi from publications;

-- alter table publications modify academic_year varchar(25);

-- alter table publications drop constraint chk_academic_year;
-- update publications set academic_year='JULY 2021 - JUNE 2022';

-- commit;