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

  insert into hierarchy (vchr_name,int_level) values ('TEAM',1),('FLOOR',2),('BRANCH',3),('DISTRICT',4),('TERIRTORY',5),('STATE',6),('ZONE',7),('COUNTRY',8);

  INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES ((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'ADD LOCATIONS','add locations',1,'mdi mdi-map-marker');
