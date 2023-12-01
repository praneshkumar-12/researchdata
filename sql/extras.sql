USE ssn_new;

ALTER TABLE publications ADD COLUMN verified VARCHAR(10);

UPDATE publications set verified='False';