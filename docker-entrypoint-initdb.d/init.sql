-- Postgres DB
CREATE TABLE data(
  id   serial,
  data text
);

-- Generate a 5Go DB
INSERT INTO data (data) SELECT g.id::text || 'Some more data to fill the DB' FROM generate_series(1, (6000000 / 438) * 5000) AS g (id);

-- Application DB
CREATE DATABASE application;
\c application;

CREATE TABLE data(
  id   serial,
  data text
);

-- Generate a 5Mo DB
INSERT INTO data (data) SELECT g.id::text || 'Some more data to fill the DB' FROM generate_series(1, (6000000 / 438) * 5) AS g (id);

-- Data DB
CREATE DATABASE data;
\c data;

CREATE TABLE data(
  id   serial,
  data text
);

-- Generate a 500Mo DB
INSERT INTO data (data) SELECT g.id::text || 'Some more data to fill the DB' FROM generate_series(1, (6000000 / 438) * 500) AS g (id);
