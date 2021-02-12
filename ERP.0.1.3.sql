CREATE TABLE customer_rating (
    pk_bint_id BIGSERIAL PRIMARY KEY,
    vchr_feedback TEXT NULL,
    dbl_rating DOUBLE PRECISION ,
    fk_customer_id BIGINT REFERENCES customer_details (pk_bint_id) NOT NULL,
    fk_user_id BIGINT REFERENCES userdetails ( user_ptr_id) NOT NULL
);
CREATE TABLE emp_category(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  vchr_code VARCHAR(10),
  vchr_name VARCHAR(150),
  int_status INTEGER ,
  fk_created_id BIGINT REFERENCES auth_user(id),
  fk_updated_id BIGINT REFERENCES auth_user(id),
  dat_created TIMESTAMP ,
  dat_updated TIMESTAMP
);

ALTER TABLE userdetails
DROP COLUMN fk_category_id;

ALTER TABLE userdetails
ADD COLUMN fk_category_id BIGINT REFERENCES emp_category(pk_bint_id);