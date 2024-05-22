USE ssn_new;

ALTER TABLE publications ADD COLUMN verified VARCHAR(10);

UPDATE publications set verified='False';

USE ssn_new;

ALTER TABLE publications ADD COLUMN admin_verified VARCHAR(10);

UPDATE publications set admin_verified='False';

ALTER TABLE publications ADD COLUMN impact_factor FLOAT;
