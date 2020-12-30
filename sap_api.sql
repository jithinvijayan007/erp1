create table sap_api_track(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  int_document_id INTEGER,
  int_type INTEGER,
  int_status INTEGER,
  dat_document TIMESTAMP,
  dat_push TIMESTAMP,
  txt_remarks TEXT
);

alter table payment add column fk_bank_id BIGINT REFERENCES bank(pk_bint_id);

ALTER TABLE customer_details ADD vchr_code VARCHAR(25);
UPDATE customer_details SET vchr_code = 'CST1';
ALTER TABLE branch ALTER COLUMN vchr_address TYPE VARCHAR(300);

CREATE TABLE location_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  int_code BIGINT,
  vchr_location VARCHAR(256)
);

alter table tax_master add column vchr_code VARCHAR(20);
alter table tax_master add column dbl_rate DOUBLE PRECISION;

create table opening_balance(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_acc_no VARCHAR(20),
    fk_financial_id BIGINT REFERENCES financial_year(pk_bint_id),
    vchr_acc_name VARCHAR(300),
    dbl_debit_amount DOUBLE PRECISION,
    dbl_credit_amount DOUBLE PRECISION
);

create table import_files(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_file_name VARCHAR(50),
  fk_uploaded_by BIGINT REFERENCES userdetails(user_ptr_id),
  dat_uploaded DATE
);

create table chart_of_accounts(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_acc_code VARCHAR(30),
  vchr_acc_name VARCHAR(100),
  vchr_acc_type VARCHAR (5)
);

ALTER TABLE item_group ADD COLUMN vchr_group_code VARCHAR(50);

alter table branch add column fk_location_master_id BIGINT REFERENCES location_master(pk_bint_id);

create table sap_tax_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code varchar(20),
  vchr_name varchar(100),
  dbl_rate double precision,
  jsn_tax_master jsonb
);

ALTER TABLE item ADD COLUMN vchr_old_item_code VARCHAR(50);
ALTER TABLE item ADD COLUMN dat_updated TIMESTAMP;
ALTER TABLE item ALTER COLUMN vchr_name TYPE VARCHAR(200);
INSERT INTO tax_master(vchr_name,bln_active) VALUES('KFC',TRUE);

-- INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('GST18','GST @18%',12.000000,(select pk_bint_id from tax_master where vchr_name in ('SGST','CGST'))
-- INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('GST18','GST @18%',12.000000,'[1,2]')

-- INSERT INTO sap_tax_master(vchr_code,vchr_name,dbl_rate,jsn_tax_master) values('GST18','GST @18%',12.000000,'[1,2]')




CREATE TABLE accounts_map(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_module_name VARCHAR(50) NOT NULL,
    vchr_category VARCHAR(250),
    fk_coa_id BIGINT REFERENCES chart_of_accounts(pk_bint_id),
    int_status INTEGER DEFAULT 1,
    int_type INTEGER DEFAULT 1,
    fk_branch_id BIGINT REFERENCES branch(pk_bint_id)
);



-- create table sap_api_time_track(
--     pk_bint_id BIGSERIAL PRIMARY KEY,
--     vchr_api_name VARCHAR(50) NOT NULL,
--     vchr_category VARCHAR(250),
--     dat_document TIMESTAMP,
--     int_status INTEGER DEFAULT 0
-- )