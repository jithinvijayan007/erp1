alter table branch add column fk_hierarchy_data_id bigint REFERENCES hierarchy_data(pk_bint_id);
create table hierarchy(
  pk_bint_id  BIGSERIAL PRIMARY KEY,
  int_level smallint,
  vchr_name varchar(100)
  );

create table hierarchy_data(
  pk_bint_id  BIGSERIAL PRIMARY KEY,
  vchr_name varchar(100),
  vchr_code varchar(5),
  fk_hierarchy_id bigint REFERENCES hierarchy(pk_bint_id),
  fk_hierarchy_data_id bigint REFERENCES hierarchy_data(pk_bint_id)
  );