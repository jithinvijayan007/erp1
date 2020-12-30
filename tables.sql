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

CREATE TABLE branch(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code VARCHAR(20),
  vchr_name VARCHAR(50) NOT NULL,
  vchr_address VARCHAR(100),
  vchr_email VARCHAR(50),
  vchr_phone VARCHAR(20),
  dat_close TIMESTAMP,
  bint_stock_limit BIGINT,
  flt_static_ip FLOAT,
  flt_latitude FLOAT,
  flt_longitude FLOAT,
  dat_inauguration DATE,
  tim_inauguration TIME WITHOUT TIME ZONE,
  vchr_inaugurated_by VARCHAR(50),
  int_status INTEGER DEFAULT 1,
  fk_category_id BIGINT REFERENCES other_category(pk_bint_id),
  int_type INTEGER,
  fk_states_id BIGINT REFERENCES states (pk_bint_id),
  int_price_template INT
);
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



CREATE TABLE userdetails(
  user_ptr_id BIGINT REFERENCES auth_user PRIMARY KEY,
  bint_phone BIGINT,
  vchr_pssrsttkn VARCHAR(30),
  bint_passrstflg BIGINT,
  dat_passrsttime TIMESTAMP,
  fk_group_id BIGINT REFERENCES groups(pk_bint_id),
  fk_company_id BIGINT REFERENCES company(pk_bint_id),
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id),
  fk_brand_id BIGINT REFERENCES brands(pk_bint_id),
  bint_usercode INTEGER UNIQUE,
  vchr_profpic VARCHAR(30),
  dat_resapp TIMESTAMP,
  int_areaid INTEGER,
  dat_created TIMESTAMP,
  dat_updated TIMESTAMP,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  json_product JSONB
);


CREATE TABLE specifications(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(50) NOT NULL,
  bln_status boolean DEFAULT true
);

CREATE TABLE products(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(50) NOT NULL,
  fk_category_id BIGINT REFERENCES category(pk_bint_id) NOT NULL,
  -- fk_specification_id BIGINT REFERENCES specifications(pk_bint_id) NOT NULL,
  int_status INTEGER DEFAULT 1,
  -- bln_sales boolean, -- true if sales,false if service
  dat_created  TIMESTAMP DEFAULT now(),
  fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
  fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
  int_sales INT
);

CREATE TABLE item_group (
	pk_bint_id BIGSERIAL PRIMARY KEY,
	vchr_item_group VARCHAR(30),
	int_status INTEGER DEFAULT 1,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP DEFAULT now(),
  dat_updated TIMESTAMP DEFAULT now()
);



CREATE TABLE item_category(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_item_category VARCHAR(50) NOT NULL,
  json_tax_master JSONB,
  json_specification_id JSONB,
  int_status INTEGER DEFAULT 1,
  dat_created  TIMESTAMP DEFAULT now(),
  fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
  fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
  vchr_hsn_code VARCHAR(50),
  vchr_sac_code VARCHAR(50)
);



CREATE TABLE item(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_product_id BIGINT REFERENCES products(pk_bint_id) NOT NULL,
  fk_brand_id BIGINT REFERENCES brands(pk_bint_id) NOT NULL,
  vchr_item_code VARCHAR(50) NOT NULL UNIQUE,
  fk_item_category_id BIGINT REFERENCES item_category(pk_bint_id) NOT NULL,
  fk_item_group_id BIGINT REFERENCES item_group(pk_bint_id) NOT NULL,
  dbl_supplier_cost DOUBLE PRECISION NOT NULL,
  dbl_dealer_cost DOUBLE PRECISION NOT NULL,
  dbl_mrp DOUBLE PRECISION NOT NULL,
  dbl_mop DOUBLE PRECISION NOT NULL,
  json_specification_id JSONB,
  int_reorder_level INTEGER,
  vchr_prefix VARCHAR(40),
  imei_status BOOLEAN, --true = imei number in serial number ,false if automatic serial number
  sale_status BOOLEAN, -- true saleable ,false not saleable
  int_status INTEGER DEFAULT 1,
  dat_created  TIMESTAMP DEFAULT now(),
  fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
  fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
  image1 VARCHAR(350),
  image2 VARCHAR(350),
  image3 VARCHAR(350),
  vchr_name VARCHAR(100)
);

create table supplier (
pk_bint_id BIGSERIAL PRIMARY KEY,
vchr_name VARCHAR(50),
dat_from TIMESTAMP,
vchr_code VARCHAR(50),
int_credit_days INTEGER,
bint_credit_limit BIGINT,
int_po_expiry_days INT,
vchr_tin_no VARCHAR(50),
vchr_cst_no VARCHAR(50),
vchr_gstin VARCHAR(50),
vchr_gstin_status VARCHAR(50),
fk_category_id BIGINT REFERENCES other_category,
fk_tax_class_id BIGINT REFERENCES tax_master(pk_bint_id),
vchr_account_group VARCHAR(50),
vchr_bank_account VARCHAR(50),
vchr_pan_no VARCHAR(50),
vchr_pan_status VARCHAR(50),
fk_created_id BIGINT REFERENCES auth_user(id),
fk_updated_id BIGINT REFERENCES auth_user(id),
dat_created TIMESTAMP DEFAULT now(),
dat_updated TIMESTAMP DEFAULT now(),
is_act_del INTEGER,
int_batch_no_offset INTEGER default 0
);



CREATE TABLE address_supplier(
pk_bint_id BIGSERIAL PRIMARY KEY,
vchr_address VARCHAR(185),
vchr_email VARCHAR(30),
bint_phone_no BIGINT,
INT_pin_code INT,
fk_supplier_id BIGINT REFERENCES supplier(pk_bint_id),
fk_states_id BIGINT REFERENCES states (pk_bint_id)
);
CREATE TABLE contact_person_supplier(
pk_bint_id BIGSERIAL PRIMARY KEY,
vchr_name VARCHAR(30),
vchr_designation VARCHAR(30),
vchr_department VARCHAR(30),
vchr_office VARCHAR(30),
bint_mobile_no BIGINT,
bint_mobile_no2 BIGINT,
fk_supplier_id BIGINT REFERENCES supplier(pk_bint_id)
);

CREATE TABLE dealer(
	pk_bint_id BIGSERIAL PRIMARY KEY,
	vchr_name VARCHAR(50),
	dat_from TIMESTAMP,
	vchr_code VARCHAR(50),
	int_credit_days INTEGER,
	bint_credit_limit BIGINT,
	dat_po_expiry_date TIMESTAMP,
	vchr_tin_no BIGINT,
	vchr_cst_no BIGINT,
	vchr_gstin VARCHAR(50),
	vchr_gstin_status VARCHAR(50),
	fk_category_id BIGINT REFERENCES category(pk_bint_id),
	fk_tax_class_id BIGINT REFERENCES tax_master(pk_bint_id),
	vchr_account_group VARCHAR(50),
	vchr_bank_account VARCHAR(50),
	vchr_pan_no VARCHAR(50),
	vchr_pan_status VARCHAR (50),
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  dat_updated TIMESTAMP,
  int_is_act_del INTEGER
);


CREATE TABLE dealer_address(
	pk_bint_id BIGSERIAL PRIMARY KEY,
	vchr_address VARCHAR(180),
	vchr_email VARCHAR(30),
	bint_phone_no BIGINT,
	int_pincode INTEGER,
	fk_dealer_id BIGINT REFERENCES dealer (pk_bint_id),
  bln_status BOOLEAN default True
);

CREATE TABLE dealer_contact_person(
	pk_bint_id BIGSERIAL PRIMARY KEY,
	vchr_name VARCHAR(50),
  vchr_designation VARCHAR(50),
	vchr_department VARCHAR (50),
	vchr_office VARCHAR(50),
	bint_mobile_no1 BIGINT,
	bint_mobile_no2 BIGINT,
	fk_dealer_id BIGINT REFERENCES dealer(pk_bint_id),
  bln_status BOOLEAN default True
);

CREATE TABLE dealer_log(
 pk_bint_id BIGSERIAL PRIMARY KEY,
 vchr_remarks TEXT,
 vchr_status VARCHAR(20),
 dat_created TIMESTAMP,
 fk_created_id BIGINT REFERENCES auth_user(id),
 fk_dealer_id BIGINT REFERENCES dealer
);

CREATE TABLE other_category(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(50),
  int_status INTEGER
);
CREATE TABLE supplier_log(
 pk_bint_id BIGSERIAL PRIMARY KEY,
 vchr_remarks TEXT,
 vchr_status VARCHAR(20),
 dat_created TIMESTAMP DEFAULT now(),
 fk_created_id BIGINT REFERENCES auth_user(id),
 fk_supplier_id BIGINT REFERENCES supplier
);


create table po_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_po_num VARCHAR(20),
  dat_po TIMESTAMP,
  dat_po_expiry TIMESTAMP,-->dat_po + expiry days for supplier
  fk_supplier_id BIGINT REFERENCES supplier(pk_bint_id),
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id),-->[warehouses or head office only]
  vchr_notes TEXT,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  int_doc_status INTEGER,
  int_status integer,
  int_total_qty INTEGER,
  dbl_total_amount DOUBLE PRECISION
   -->[-1,0,1]
);


create table po_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  fk_po_master_id BIGINT REFERENCES po_master(pk_bint_id),
  int_qty INTEGER,
  dbl_prate DOUBLE PRECISION,
  dbl_total_amount DOUBLE PRECISION
  );


CREATE TABLE document(
	pk_bint_id BIGSERIAL PRIMARY KEY,
	vchr_module_name VARCHAR(50) NOT NULL,
	vchr_short_code VARCHAR(5) NOT NULL,
	int_number INTEGER NOT NULL
);

create table grn_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_purchase_num VARCHAR(20),
  dat_purchase TIMESTAMP,
  fk_supplier_id BIGINT REFERENCES supplier(pk_bint_id),
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id),-->[warehouses or head office only]
  fk_po_id BIGINT REFERENCES po_master(pk_bint_id),
  int_fop INTEGER,
  dat_pay_before TIMESTAMP,
  dbl_total DOUBLE PRECISION,
  vchr_notes TEXT,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  int_doc_status INTEGER,
  dbl_addition DOUBLE PRECISION,
  dbl_deduction DOUBLE PRECISION,
  dbl_roundoff_value DOUBLE PRECISION null,
  int_approve INTEGER,
  vchr_bill_no VARCHAR(20),
  dat_bill TIMESTAMP,
  vchr_reject_reason TEXT,
  dbl_bill_amount DOUBLE PRECISION,
  vchr_bill_image VARCHAR(350)
   -->[-1,0,1]
);

create table grn_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  fk_purchase_id BIGINT REFERENCES purchase(pk_bint_id),
  int_qty INTEGER,
  int_free INTEGER,
  int_avail INTEGER,
  int_damaged INTEGER,
  dbl_costprice DOUBLE PRECISION,-->[price of a single piece without tax and discount]
  dbl_dscnt_percent DOUBLE PRECISION,-->[total discount percent]
  dbl_dscnt_perunit DOUBLE PRECISION,-->[per single piece]
  dbl_discount DOUBLE PRECISION,-->[total amount]
  jsn_tax JSONB,--> (CGST:4,SGST:4)[per piece]
  dbl_tax DOUBLE PRECISION,-->[tax amount per piece]
  dbl_ppu DOUBLE PRECISION,-->[price of a single piece with tax and discount]
  dbl_total_amount DOUBLE PRECISION,-->[dbl_ppu * int_qty]
  jsn_imei JSONB,-->text
  jsn_imei_avail JSONB,
  jsn_imei_dmgd JSONB,-->damaged item
  vchr_batch_no VARCHAR(30),
  dbl_perpie_aditn DOUBLE PRECISION,
  dbl_perpie_dedctn DOUBLE PRECISION
);

CREATE TABLE location(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(100),
  vchr_pin_code VARCHAR(10),
  fk_state_id BIGINT REFERENCES states(pk_bint_id)
);

CREATE TABLE customer_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(100),
  vchr_email VARCHAR(200),
  int_mobile BIGINT,
  txt_address TEXT,
  vchr_gst_no VARCHAR(30),
  int_otp_number BIGINT,
  fk_state_id BIGINT REFERENCES states(pk_bint_id),
  fk_location_id BIGINT REFERENCES location(pk_bint_id),
  int_loyalty_points BIGINT,
  int_redeem_point BIGINT,
  dbl_purchase_amount FLOAT,
  vchr_loyalty_card_number VARCHAR(50)
);

CREATE TABLE financial_year(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_financial_year VARCHAR(20),
  dat_start DATE,
  dat_end DATE
);

CREATE TABLE sales_master(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_customer_id BIGINT REFERENCES customer_details(pk_bint_id),
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id),
  dat_invoice DATE,
  fk_staff_id BIGINT REFERENCES userdetails(user_ptr_id),
  vchr_invoice_num VARCHAR(50),
  vchr_remarks VARCHAR(500),
  vchr_delete_remark VARCHAR(500),
  dbl_total_amt DOUBLE PRECISION,
  dbl_total_tax DOUBLE PRECISION,
  json_tax JSONB,
  dbl_discount DOUBLE PRECISION,
  fk_loyalty_id BIGINT REFERENCES loyalty_card(pk_bint_id),
  dbl_loyalty DOUBLE PRECISION,
  dbl_buyback DOUBLE PRECISION,
  dbl_supplier_amount DOUBLE PRECISION,
  fk_coupon_id BIGINT REFERENCES coupon(pk_bint_id),
  dbl_coupon_amt DOUBLE PRECISION,
  int_doc_status INTEGER,
  dat_created TIMESTAMP,
  dat_updated TIMESTAMP,
  fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
  fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
  fk_financial_year_id BIGINT REFERENCES financial_year(pk_bint_id)
);

CREATE TABLE sales_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_master_id BIGINT REFERENCES sales_master(pk_bint_id),
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  int_qty INTEGER,
  dbl_amount DOUBLE PRECISION,
  dbl_tax DOUBLE PRECISION,
  dbl_discount DOUBLE PRECISION,
  dbl_buyback DOUBLE PRECISION,
  json_tax JSONB,
  vchr_batch VARCHAR(50),
  json_imei JSONB,
  int_doc_status INTEGER,
  dbl_supplier_amount DOUBLE PRECISION,
  dbl_selling_price DOUBLE PRECISION
);

CREATE TABLE partial_invoice (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  json_data JSONB,
  int_active INTEGER DEFAULT 0,
  dat_created TIMESTAMP,
  dat_invoice TIMESTAMP,
  fk_invoice_id BIGINT REFERENCES sales_master(pk_bint_id)
);

CREATE TABLE branch_stock_master (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id),
  fk_created_id  BIGINT REFERENCES auth_user(id),
  dat_stock TIMESTAMP,
  dbl_tax DOUBLE PRECISION,
  dbl_amount DOUBLE PRECISION,
  jsn_tax JSONB
);

CREATE TABLE branch_stock_details (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  fk_master_id BIGINT REFERENCES branch_stock_master(pk_bint_id),
  int_qty INTEGER,
  jsn_imei JSONB,
  jsn_imei_avail JSONB,
  jsn_imei_dmgd JSONB,
  jsn_batch_no JSONB,
  fk_transfer_details_id BIGINT REFERENCES ist_details(pk_bint_id)
  -- fk_pd_id BIGINT REFERENCES purchase_details(pk_bint_id),
  -- dbl_unitprice DOUBLE PRECISION,-->[price of a single piece without tax and discount]
  -- dbl_ppu DOUBLE PRECISION,-->[price of a single piece with tax and discount]
  -- dbl_tax DOUBLE PRECISION,
  -- jsn_tax JSONB ,--> (CGST:4,SGST:4,IGST:4)[per piece]
  -- vchr_batch_no VARCHAR(30)
);

CREATE TABLE coupon(
pk_bint_id BIGSERIAL PRIMARY KEY,
vchr_coupon_code VARCHAR(30),
dat_expiry DATE,
fk_product_id BIGINT REFERENCES products,
fk_brand_id BIGINT REFERENCES brands,
fk_item_category_id BIGINT REFERENCES  item_category,
fk_item_group_id BIGINT REFERENCES item_group,
fk_item_id BIGINT REFERENCES item,
int_discount_percentage INT,
bint_max_discount_amt BIGINT,
bint_min_purchase_amt BIGINT,
int_max_usage_no INT,
fk_updated_id BIGINT REFERENCES auth_user(id),
fk_created_id BIGINT REFERENCES auth_user(id),
dat_created TIMESTAMP,
dat_updated TIMESTAMP,
int_which INT
);
CREATE TABLE type(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(30)
);
CREATE TABLE terms(
pk_bint_id BIGSERIAL PRIMARY KEY,
jsn_terms JSON,
fk_type_id BIGINT REFERENCES type,
int_status INTEGER,
fk_created_id BIGINT REFERENCES auth_user,
dat_created TIMESTAMP without time zone,
fk_updated_id BIGINT REFERENCES auth_user,
dat_updated TIMESTAMP without time zone);


create TABLE purchase_voucher(
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_voucher_num VARCHAR(20),
    fk_supplier_id BIGINT REFERENCES supplier(pk_bint_id),
    fk_grn_id BIGINT REFERENCES grn_master(pk_bint_id),
    dbl_voucher_amount DOUBLE PRECISION,
    vchr_voucher_bill_no VARCHAR(20),
    dat_voucher_bill TIMESTAMP,
    fk_created_id BIGINT REFERENCES auth_user(id),
    dat_created TIMESTAMP,
    fk_updated_id BIGINT REFERENCES auth_user(id),
    dat_updated TIMESTAMP,
    vchr_remark TEXT,
    int_doc_status INTEGER
);


CREATE TABLE branch_stock_imei_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_details_id BIGINT REFERENCES branch_stock_details(pk_bint_id),
  fk_grn_details_id BIGINT REFERENCES grn_details(pk_bint_id),
  jsn_imei JSONB,
  jsn_batch_no JSONB,
  int_qty INTEGER
);

create table stock_request(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_from_id BIGINT REFERENCES branch(pk_bint_id),
  fk_to_id BIGINT REFERENCES branch(pk_bint_id),
  vchr_stkrqst_num VARCHAR(20),
  dat_request TIMESTAMP,
  dat_expected TIMESTAMP,
  vchr_remarks TEXT,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  int_doc_status INTEGER, -->[-1,0,1]
  bln_approved INTEGER -->[]
);
create table isr_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_request_id BIGINT REFERENCES stock_request(pk_bint_id),
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  int_qty INTEGER
);

create table stock_transfer(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_request_id  BIGINT REFERENCES stock_request(pk_bint_id),
  fk_pd_id BIGINT REFERENCES purchase_details(pk_bint_id),
  fk_from_id BIGINT REFERENCES branch(pk_bint_id),
  fk_to_id BIGINT REFERENCES branch(pk_bint_id),
  vchr_stktransfer_num VARCHAR(20),
  dat_transfer TIMESTAMP,
  dat_expected TIMESTAMP,
  dat_acknowledge TIMESTAMP,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  int_doc_status INTEGER, -->[-1,0,1]
  int_acknowledge INTEGER,
  int_status INTEGER -->transit-0,received-1
);
create table ist_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_transfer_id BIGINT REFERENCES stock_transfer(pk_bint_id),
  fk_item_id BIGINT REFERENCES item(pk_bint_id),
  int_qty INTEGER,
  jsn_imei JSONB
);

CREATE TABLE transfer_history (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_transfer_id BIGINT REFERENCES stock_transfer(pk_bint_id),
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  vchr_status VARCHAR(30),
  int_doc_status INTEGER
);

CREATE TABLE transfer_mode_details (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_transfer_id BIGINT REFERENCES stock_transfer(pk_bint_id),
  int_medium INTEGER,
  vchr_name_responsible VARCHAR(30),
  bnt_contact_number BIGINT,
  bnt_number BIGINT,
  fk_created_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP,
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_updated TIMESTAMP,
  int_packet_no INTEGER,
  int_packet_received INTEGER,
  int_doc_status INTEGER,
  dbl_expense DOUBLE PRECISION
);

CREATE TABLE stock_transfer_imei_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_details_id BIGINT REFERENCES ist_details(pk_bint_id),
  fk_grn_details_id BIGINT REFERENCES grn_details(pk_bint_id),
  jsn_imei JSONB,
  jsn_batch_no JSONB
);
CREATE TABLE price_list2(
pk_bint_id BIGSERIAL PRIMARY KEY,
fk_item_id BIGINT REFERENCES item,
dbl_supp_amnt DOUBLE PRECISION,
dbl_cost_amnt DOUBLE PRECISION,
dbl_mop DOUBLE PRECISION,
dbl_mrp DOUBLE PRECISION,
dat_efct_from TIMESTAMP,
fk_created_id BIGINT REFERENCES auth_user,
dat_created TIMESTAMP,
fk_updated_id BIGINT REFERENCES auth_user,
dat_updated TIMESTAMP,
int_status INTEGER DEFAULT 1,
dbl_my_amt DOUBLE PRECISION,
dbl_dealer_amt DOUBLE PRECISION

);

CREATE TABLE loyalty_card(
pk_bint_id BIGSERIAL PRIMARY KEY,
vchr_card_name VARCHAR(50),
int_price_range_from BIGINT,
int_price_range_to BIGINT,
dbl_loyalty_percentage FLOAT,
dbl_min_purchase_amount FLOAT,
int_min_redeem_days INTEGER,
int_min_redeem_point BIGINT,
bln_status BOOLEAN,
fk_created_id BIGINT REFERENCES AUTH_USER,
fk_updated_id BIGINT REFERENCES AUTH_USER,
dat_created TIMESTAMP,
dat_updated TIMESTAMP
);

CREATE TABLE cust_service_delivery(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  fk_sales_master_id BIGINT REFERENCES sales_master(pk_bint_id),
  fk_customer_id BIGINT REFERENCES customer_details(pk_bint_id),
  vchr_cust_name VARCHAR(100),
  int_mobile BIGINT,
  txt_address TEXT,
  vchr_landmark VARCHAR(200),
  vchr_gst_no VARCHAR(30),
  fk_location_id BIGINT REFERENCES location(pk_bint_id),
  fk_state_id BIGINT REFERENCES states(pk_bint_id)
);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- #day_closure table

CREATE TABLE day_closure_master (
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_name VARCHAR(50) NOT NULL,
  bln_active BOOLEAN
);

insert into day_closure_master(vchr_name,bln_active) VALUES('2000',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('1000',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('500',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('200',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('100',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('50',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('20',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('10',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('5',True);
insert into day_closure_master(vchr_name,bln_active) VALUES('1',True);

CREATE TABLE day_closure_details(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  Dat_time TIMESTAMP,
  fk_staff_id BIGINT REFERENCES userdetails(user_ptr_id),
  total_amount DOUBLE PRECISION,
  json_dayclosure json,
  int_closed INTEGER,
  fk_branch_id BIGINT REFERENCES branch(pk_bint_id) NOT NULL
);
 --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


 ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 -- """company Permissions"""
 CREATE TABLE main_category(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     vchr_main_category_name VARCHAR(50) NOT NULL,
     vchr_main_category_value VARCHAR(50),
     int_main_category_order INTEGER,
     vchr_icon_name varchar(50)
 );

 CREATE TABLE sub_category(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_main_category_id BIGINT REFERENCES main_category(pk_bint_id) NOT NULL,
     vchr_sub_category_name VARCHAR(50) NOT NULL,
     vchr_sub_category_value VARCHAR(50),
     int_sub_category_order INTEGER,
     vchr_icon_name varchar(50)
 );

 CREATE TABLE menu_category(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     vchr_menu_category_name VARCHAR(50) NOT NULL,
     fk_sub_category_id BIGINT REFERENCES sub_category(pk_bint_id) NOT NULL,
     vchr_menu_category_value VARCHAR(50),
     int_menu_category_order INTEGER,
     bln_has_children BOOLEAN,
     vchr_addurl varchar(50),
     vchr_viewurl varchar(50),
     vchr_editurl varchar(50),
     vchr_listurl varchar(50)
 );


 CREATE TABLE category_items(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_main_category_id BIGINT REFERENCES main_category(pk_bint_id) NOT NULL,
     fk_sub_category_id BIGINT REFERENCES sub_category(pk_bint_id) NOT NULL,
     fk_menu_category_id BIGINT REFERENCES menu_category(pk_bint_id) NOT NULL,
     fk_company_id BIGINT REFERENCES company(pk_bint_id) NULL
 );


 CREATE TABLE group_permissions(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_groups_id BIGINT REFERENCES groups(pk_bint_id) NOT NULL,
     fk_category_items_id BIGINT REFERENCES category_items(pk_bint_id) NOT NULL,
     bln_view BOOLEAN NOT NULL DEFAULT FALSE,
     bln_add BOOLEAN NOT NULL DEFAULT FALSE,
     bln_delete BOOLEAN NOT NULL DEFAULT FALSE,
     bln_edit BOOLEAN NOT NULL DEFAULT FALSE
 );



 ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 ------------------------------------------------------------------------------------------------------------------------------------

 --add_combo

 CREATE TABLE add_combo_master(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   int_offer_type INTEGER,
   vchr_offer_name VARCHAR(100),
   fk_item_id BIGINT REFERENCES item(pk_bint_id),
   fk_brand_id BIGINT REFERENCES brands(pk_bint_id),
   dbl_amt DOUBLE PRECISION,
   int_status INTEGER default(1),
   int_quantity INTEGER,
   dat_from DATE,
   dat_to DATE,
   fk_company_id BIGINT REFERENCES company(pk_bint_id) NOT NULL
 );


 CREATE TABLE add_combo_discount(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   fk_master_id BIGINT REFERENCES add_combo_master(pk_bint_id),
   int_discount_type INTEGER,
   dbl_amt DOUBLE PRECISION,
   dbl_percent DOUBLE PRECISION
 );

 CREATE TABLE add_combo_discount_item(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   fk_master_id BIGINT REFERENCES add_combo_discount(pk_bint_id),
   int_quantity INTEGER,
   fk_item_id BIGINT REFERENCES item(pk_bint_id),
   dbl_amt DOUBLE PRECISION,
   dbl_percent DOUBLE PRECISION
 );
 ------------------------------------------------------------------------------------------------------------------------------------
 CREATE TABLE loyalty_card_invoice(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   fk_loyalty_id BIGINT REFERENCES loyalty_card(pk_bint_id),
   fk_customer_id BIGINT REFERENCES customer_details,
   int_points BIGINT NULL DEFAULT 0,
   dbl_amount DOUBLE PRECISION,
   fk_invoice_id BIGINT REFERENCES sales_master(pk_bint_id),
   dat_invoice TIMESTAMP);

 CREATE TABLE loyalty_card_status(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   fk_customer_id BIGINT REFERENCES customer_details,
   fk_old_card_id BIGINT REFERENCES loyalty_card(pk_bint_id),
   fk_new_card BIGINT REFERENCES loyalty_card(pk_bint_id),
   vchr_status VARCHAR(50),
   fk_staff_id  BIGINT REFERENCES auth_user,
   dat_eligible DATE,
   dat_given DATE,
   vchr_remark VARCHAR(500));

   CREATE TABLE receipt(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     dat_issue TIMESTAMP,
     fk_customer_id BIGINT REFERENCES customer_details(pk_bint_id),
     int_fop INT,
     dbl_amount DOUBLE PRECISION,
     vchr_remarks TEXT,
     fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
     fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
     int_doc_status INTEGER,
     dat_created TIMESTAMP,
     dat_updated TIMESTAMP,
     int_pstatus INT,
     int_receipt_type INT,
     fk_item_id BIGINT REFERENCES ITEM,
     vchr_bank VARCHAR(50),
     vchr_transaction_id VARCHAR(50),
     dat_approval TIMESTAMP,
     vchr_receipt_num VARCHAR(50)
   );

   CREATE TABLE payment_details(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_sales_master_id BIGINT REFERENCES sales_master(pk_bint_id) NOT NULL,
     int_fop INTEGER NOT NULL,
     vchr_card_number VARCHAR(20),
     vchr_name VARCHAR(100),
     vchr_finance_schema VARCHAR(20),
     vchr_reff_number VARCHAR(100),
     dbl_receved_amt DOUBLE PRECISION,
     dbl_finance_amt DOUBLE PRECISION,
     dat_created_at TIMESTAMP NOT NULL DEFAULT NOW()
   );
   CREATE TABLE payment(
  	pk_bint_id BIGSERIAL PRIMARY KEY,
  	vchr_doc_num VARCHAR(50),
  	dat_payment TIMESTAMP,
  	int_fop INTEGER,
  	int_payee_type INTEGER,
  	fk_payee_id INTEGER,
  	fk_branch_id BIGINT REFERENCES branch(pk_bint_id),
  	dbl_amount DOUBLE PRECISION,
    vchr_remarks TEXT,
 	  fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
   	fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
    fk_approved_by_id BIGINT REFERENCES userdetails(user_ptr_id),
   	int_doc_status INTEGER,
  	dat_created TIMESTAMP,
 	  dat_updated TIMESTAMP,
    int_approved INT
   	);
   CREATE TABLE receipt_invoice_matching(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   dbl_amount DOUBLE PRECISION,
   dat_created TIMESTAMP,
   fk_sales_master_id BIGINT REFERENCES sales_master,
   fk_receipt_id BIGINT REFERENCES receipt);


   CREATE TABLE day_closure_not_tally(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_day_closure_details_id BIGINT REFERENCES day_closure_details(pk_bint_id),
     Dat_time TIMESTAMP,
     fk_staff_id BIGINT REFERENCES userdetails(user_ptr_id),
     fk_approve_id BIGINT REFERENCES userdetails(user_ptr_id),
     total_amount DOUBLE PRECISION,
     json_dayclosure json,
     int_status INTEGER NOT NULL,
     fk_branch_id BIGINT REFERENCES branch(pk_bint_id) NOT NULL,
     vchr_remark VARCHAR(100)
   );




   CREATE TABLE sales_master_jio(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_customer_id BIGINT REFERENCES customer_details(pk_bint_id),
     fk_branch_id BIGINT REFERENCES branch(pk_bint_id),
     fk_item_id BIGINT REFERENCES item(pk_bint_id),
     vchr_batch VARCHAR(50),
     json_imei JSONB,
     int_qty INTEGER,
     dat_invoice DATE,
     fk_staff_id BIGINT REFERENCES userdetails(user_ptr_id),
     vchr_invoice_num VARCHAR(50),
     vchr_remarks VARCHAR(500),
     vchr_delete_remark VARCHAR(500),
     dbl_total_amt DOUBLE PRECISION,
     int_doc_status INTEGER,
     dat_created TIMESTAMP,
     dat_updated TIMESTAMP,
     fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
     fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
     fk_financial_year_id BIGINT REFERENCES financial_year(pk_bint_id)
   );


   CREATE TABLE bank(
   pk_bint_id BIGSERIAL PRIMARY KEY,
   vchr_name VARCHAR(50) NOT NULL,
   int_status INTEGER
   );
   CREATE TABLE case_closure_master (
     pk_bint_id BIGSERIAL PRIMARY KEY,
     vchr_name VARCHAR(50) NOT NULL,
     bln_active BOOLEAN
   );

   insert into case_closure_master(vchr_name,bln_active) VALUES('2000',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('500',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('200',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('100',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('50',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('20',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('10',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('5',True);
   insert into case_closure_master(vchr_name,bln_active) VALUES('1',True);

     CREATE TABLE case_closure_details(
       pk_bint_id BIGSERIAL PRIMARY KEY,
       dat_created TIMESTAMP,
       dat_updated TIMESTAMP,
       fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
       fk_updated_id BIGINT REFERENCES userdetails(user_ptr_id),
       dbl_total_amount DOUBLE PRECISION,
       json_case_closure json,
       int_status INTEGER,
       fk_branch_id BIGINT REFERENCES branch(pk_bint_id) NOT NULL,
       vchr_remark VARCHAR(350)
     );


  CREATE TABLE sales_customer_details(
     pk_bint_id BIGSERIAL PRIMARY KEY,
     fk_customer_id BIGINT REFERENCES customer_details(pk_bint_id),
     dat_created TIMESTAMP,
     fk_created_id BIGINT REFERENCES userdetails(user_ptr_id),
     vchr_name VARCHAR(100),
     vchr_email VARCHAR(200),
     int_mobile BIGINT,
     fk_state_id BIGINT REFERENCES states(pk_bint_id),
     int_loyalty_points BIGINT,
     int_redeem_point BIGINT,
     dbl_purchase_amount FLOAT,
     vchr_loyalty_card_number VARCHAR(50),
     txt_address TEXT,
     vchr_gst_no VARCHAR(30),
     int_otp_number BIGINT,
     fk_location_id BIGINT REFERENCES location(pk_bint_id),
     fk_loyalty_id BIGINT REFERENCES loyalty_card(pk_bint_id),
     vchr_code VARCHAR(25)
  );


create table tools (￼	
    pk_bint_id BIGSERIAL PRIMARY KEY,	
    vchr_tool_name VARCHAR(40),￼	
    vchr_tool_code VARCHAR(40),￼	
    jsn_data JSONB,￼	
    int_status INTEGER￼	
);