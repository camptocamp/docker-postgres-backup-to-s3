CREATE TABLE data(
  id   serial,
  data int
);

INSERT INTO data (data) SELECT g.id FROM generate_series(1, 6000000) AS g (id);
