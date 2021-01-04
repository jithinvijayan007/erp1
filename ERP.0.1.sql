

CREATE TABLE tax_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(100),
  int_intra_tax INTEGER DEFAULT 0,
  bln_active BOOLEAN
);

CREATE TABLE brands(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code VARCHAR(50),
  vchr_name VARCHAR(150),
  int_status INTEGER DEFAULT 1
);

CREATE TABLE company(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_name VARCHAR(50) NOT NULL,
    vchr_address VARCHAR(250),
    vchr_gstin VARCHAR(50),
    vchr_mail VARCHAR(150),
    vchr_phone VARCHAR(25),
    vchr_logo VARCHAR(350),
    vchr_print_logo VARCHAR(350),
    int_status INTEGER DEFAULT 1
);

CREATE TABLE states(
		pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_name VARCHAR(50),
    vchr_code VARCHAR(100)
);

INSERT INTO states (vchr_name) VALUES ('JAMMU & KASHMIR'),('HIMACHAL PRADESH'),('PUNJAB'),('CHANDIGARH'),('UTTARANCHAL'),('HARYANA'),('DELHI'),('RAJASTHAN'),('UTTAR PRADESH'),('BIHAR'),('SIKKIM'),('ARUNACHAL PRADESH'),('NAGALAND'),('MANIPUR'),('MIZORAM'),('TRIPURA'),('MEGHALAYA'),('ASSAM'),('WEST BENGAL'),('JHARKHAND'),('ORISSA'),('CHHATTISGARH'),('MADHYA PRADESH'),('GUJARAT'),('DAMAN & DIU'),('DADRA & NAGAR HAVELI'),('MAHARASHTRA'),('ANDHRA PRADESH'),('KARNATAKA'),('GOA'),('LAKSHADWEEP'),('KERALA'),('TAMIL NADU'),('PONDICHERRY'),('ANDAMAN & NICOBAR ISLANDS')

-- CREATE TABLE branch(
--   pk_bint_id BIGSERIAL PRIMARY KEY,
--   vchr_code VARCHAR(20),
--   vchr_name VARCHAR(50) NOT NULL,
--   vchr_address VARCHAR(100),
--   vchr_email VARCHAR(50),
--   vchr_phone VARCHAR(20),
--   dat_close TIMESTAMP,
--   bint_stock_limit BIGINT,
--   flt_static_ip FLOAT,
--   flt_latitude FLOAT,
--   flt_longitude FLOAT,
--   dat_inauguration DATE,
--   tim_inauguration TIME WITHOUT TIME ZONE,
--   vchr_inaugurated_by VARCHAR(50),
--   int_status INTEGER DEFAULT 1,
--   fk_category_id BIGINT REFERENCES other_category(pk_bint_id),
--   int_type INTEGER,
--   fk_states_id BIGINT REFERENCES states (pk_bint_id),
--   int_price_template INT
-- );
CREATE TABLE category(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code VARCHAR(30),
  vchr_name VARCHAR(30),
  int_status INTEGER,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  dat_updated TIMESTAMP
);


CREATE TABLE groups(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code VARCHAR(50),
  vchr_name VARCHAR(150),
  int_status INTEGER DEFAULT 1,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  fk_company_id BIGINT REFERENCES company(pk_bint_id)
);

CREATE TABLE job_position(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(150),
  fk_department_id BIGINT REFERENCES department(pk_bint_id),
  int_area_type INTEGER,
  json_area_id JSONB,
  bln_active BOOLEAN
);

ALTER TABLE job_position ADD COLUMN dbl_experience DOUBLE PRECISION;
ALTER TABLE job_position ADD COLUMN json_qualification JSONB;
ALTER TABLE job_position ADD COLUMN vchr_age_limit VARCHAR (50);
ALTER TABLE job_position ADD COLUMN txt_desc TEXT;
ALTER TABLE job_position ADD COLUMN int_notice_period INTEGER;
alter table job_position add column json_desc JSONB;
ALTER TABLE job_position add column fk_company_id BIGINT REFERENCES company(pk_bint_id);
ALTER TABLE job_position ADD COLUMN bln_admin BOOLEAN;
ALTER TABLE job_position ADD COLUMN int_permission INTEGER;
ALTER TABLE job_position ADD COLUMN bln_brand BOOLEAN DEFAULT FALSE;

CREATE TABLE wps (pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name TEXT, dat_created TIMESTAMP,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  bln_active BOOLEAN
);

CREATE TABLE session_handler(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_user_id BIGINT REFERENCES auth_user(id),
  vchr_session_key VARCHAR(500)
);


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

  insert into hierarchy (vchr_name,int_level) values ('TEAM',1),('FLOOR',2),('BRANCH',3),('DISTRICT',4),('TERIRTORY',5),('STATE',6),('ZONE',7),('COUNTRY',8);

  INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES ((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'ADD LOCATIONS','add locations',1,'mdi mdi-map-marker');

alter table department add int_status smallint;
CREATE TABLE country(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code  VARCHAR(15),
  vchr_name VARCHAR(50)
);

INSERT INTO country (vchr_name,vchr_code) VALUES ('INDIA','IND');



CREATE TABLE religion_caste (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(100),
  bln_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE admin_settings(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(50),
  vchr_value VARCHAR ARRAY [50],
  tim_punch_cool TIME,
  fk_company_id BIGINT REFERENCES company(pk_bint_id),
  bln_enabled BOOLEAN DEFAULT true,
  vchr_code VARCHAR(50)
);



CREATE TABLE emp_leave_data(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_employee_id BIGINT REFERENCES auth_user(id),
  dbl_number BIGINT
);
alter table states add fk_country_id bigint REFERENCES country(pk_bint_id);
update states set fk_country_id = 1;
alter table district add vchr_code varchar(10);

CREATE TABLE hierarchy_groups (pk_bint_id BIGSERIAL PRIMARY KEY,fk_hierarchy_id BIGINT REFERENCES hierarchy(pk_bint_id),vchr_name VARCHAR(50),int_status SMALLINT);
alter table hierarchy_groups add column fk_department_id bigint REFERENCES department(pk_bint_id);
alter table hierarchy add fk_department_id bigint REFERENCES department(pk_bint_id);
ALTER TABLE user_details ADD COLUMN vchr_weekoff_day VARCHAR(10);
ALTER TABLE user_details ADD COLUMN fk_religion_id BIGINT REFERENCES religion_caste(pk_bint_id);
ALTER TABLE user_details ADD COLUMN fk_desig_id  BIGINT REFERENCES job_position (pk_bint_id);
ALTER TABLE user_details ADD COLUMN fk_brand_id BIGINT REFERENCES brands (pk_bint_id);
ALTER TABLE user_details ADD COLUMN fk_wps_id BIGINT REFERENCES wps(pk_bint_id);
ALTER TABLE user_details ADD COLUMN json_documents JSONB;
alter table user_details add column fk_dist_id bigint REFERENCES district(pk_bint_id);
alter table user_details ADD COLUMN vchr_emp_remark TEXT;
alter table user_details ADD COLUMN int_official_num BIGINT;
alter table user_details ADD COLUMN json_weekoff JSONB;


CREATE TABLE document_hrms(
  	pk_bint_id BIGSERIAL PRIMARY KEY,
  	vchr_module_name VARCHAR(50) NOT NULL,
  	vchr_short_code VARCHAR(5) NOT NULL,
  	int_number INTEGER NOT NULL
);
ALTER TABLE document_hrms ADD COLUMN fk_company_id BIGINT REFERENCES company(pk_bint_id);
ALTER TABLE document_hrms ADD COLUMN chr_num_separate VARCHAR(2);
ALTER TABLE document_hrms ADD COLUMN int_num_length INTEGER DEFAULT 1;

CREATE TABLE emp_references(pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_employee_id BIGINT REFERENCES user_details(user_ptr_id),
  vchr_name VARCHAR(150),
  vchr_company_name VARCHAR(400),
  vchr_desig VARCHAR(200),
  vchr_phone VARCHAR(200),
  vchr_email VARCHAR(200)
);
ALTER TABLE emp_references ADD COLUMN int_status INTEGER DEFAULT 1;

CREATE TABLE emp_family(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(150), vchr_realation VARCHAR(150),
  dat_dob DATE, vchr_occupation VARCHAR(200),
  vchr_alive VARCHAR(50),
  fk_employee_id BIGINT REFERENCES user_details(user_ptr_id),
  int_status INT
);

CREATE TABLE emp_edu_details(  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_employee_id BIGINT REFERENCES user_details(user_ptr_id),
  bln_highest_qualif BOOLEAN,
  vchr_course VARCHAR(200),
  vchr_institution VARCHAR(300),
  vchr_university VARCHAR(300),
  int_pass_year INTEGER,
  bln_active BOOLEAN,
  dbl_percentage DOUBLE PRECISION,
  vchr_place VARCHAR (200),
  vchr_qualif VARCHAR(200),
  vchr_specialzation VARCHAR (200)
);

CREATE TABLE emp_exp_details(  pk_bint_id BIGSERIAL PRIMARY KEY,
  	fk_employee_id BIGINT REFERENCES user_details(user_ptr_id),
  	vchr_employer VARCHAR (300),
  	vchr_designation VARCHAR (200),
  	txt_exp_details TEXT,
  	bln_active BOOLEAN
  );


CREATE TABLE shift_schedule(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name  VARCHAR(50),
  vchr_code  VARCHAR(25),
  bln_night BOOLEAN,
  time_shift_from TIME,
  time_shift_to TIME,
  time_break_from TIME,
  time_break_to TIME,
  time_break_hrs TIME,
  time_shed_hrs TIME,
  time_full_day TIME,
  time_half_day TIME,
  bln_allowance BOOLEAN,
  dbl_allowance_amt DOUBLE PRECISION,
  vchr_remark TEXT,
  int_status INT,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP ,
  dat_updated TIMESTAMP
);
ALTER TABLE shift_schedule ALTER COLUMN time_full_day TYPE INTERVAL;
ALTER TABLE shift_schedule ALTER COLUMN time_half_day TYPE INTERVAL;
ALTER TABLE shift_schedule ALTER COLUMN time_shed_hrs TYPE INTERVAL;
ALTER TABLE shift_schedule ALTER COLUMN time_break_hrs TYPE INTERVAL;
ALTER TABLE shift_schedule ADD COLUMN bln_time_shift BOOLEAN DEFAULT FALSE;
ALTER TABLE shift_schedule ADD COLUMN int_shift_type INTEGER DEFAULT 0;


CREATE TABLE employee_shift(
  pk_bint_id  BIGSERIAL PRIMARY KEY,
  fk_employee_id BIGINT REFERENCES user_details(user_ptr_id),
  int_shift_type INT,
  json_shift JSONB,
  bln_active BOOLEAN,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  dat_updated TIMESTAMP
);

CREATE TABLE user_history(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_user_id BIGINT REFERENCES user_details(user_ptr_id),
  json_details JSONB,
  int_type INTEGER,
  bln_changed BOOLEAN DEFAULT FALSE,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP DEFAULT NOW(),
  fk_approved_id BIGINT REFERENCES auth_user(id),
  dat_approved TIMESTAMP,
  int_status INTEGER
);

alter table group_permissions add column fk_desig_id BIGINT REFERENCES job_position(pk_bint_id);
alter table user_details add fk_hierarchy_data_id bigint REFERENCES hierarchy_data(pk_bint_id);
