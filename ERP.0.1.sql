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

Alter table department ADD int_status smallint;

 insert into brands(vchr_code,vchr_name,int_status) values ('ACER','ACER',0),('AMAZON','AMAZON',0),('APPLE','APPLE',0);

insert into other_category (vchr_name, int_status) values ('dealer',1),('supplier',2),('branch',3);

