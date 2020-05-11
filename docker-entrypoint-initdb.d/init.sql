CREATE TABLE data(
  id   serial,
  data text
);

-- Generate a 50Go DB
INSERT INTO data (data) SELECT g.id::text || 'Some more data to fill the DB' FROM generate_series(1, (6000000 / 438) * 50000) AS g (id);
