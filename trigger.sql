
CREATE LANGUAGE plpythonu;
CREATE PROCEDURAL LANGUAGE 'plpython' HANDLER plpython_call_handler;

CREATE TABLE trigger_error_log(
  pk_bint_id BIGSERIAL PRIMARY KEY,
  int_device_id BIGINT,
  vchr_user_id VARCHAR(256),
  dat_time_punch TIMESTAMP,
  txt_error TEXT,
  dat_error TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE FUNCTION api_track() RETURNS TRIGGER AS $$
import sys
from datetime import datetime
int_document=TD["new"]["pk_bint_id"]
int_type=TD["args"][0]

int_status=0
dat_document=datetime.now()
try:
  if TD["args"][0]=='1' and TD["new"]["dbl_total_amt"] >=0:
    if TD["new"].get('vchr_journal_num'):
      int_type = 10
      tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
      ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
      int_type = 1
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='3':
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='4' and TD["new"]["int_pstatus"] ==0 and not TD["new"]["fk_sales_return_id"]:
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='5' and TD["new"]["int_pstatus"] ==0 and TD["new"]["int_doc_status"] ==0 and not TD["new"]["fk_sales_return_id"]:
    if TD["new"]["int_fop"] in [4,5,6] and not TD["new"]["vchr_sap_key"]: 
      tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
      ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='6':
    if TD["new"].get('dbl_indirect_discount'):
      int_type = 15
      tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
      ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
      int_type = 6
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='7':
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='8':
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
  if TD["args"][0]=='12':
    tdc=plpy.prepare("insert into sap_api_track (int_document_id,int_type,int_status,dat_document) values ($1,$2,$3,$4)",["int","int","int","timestamp"])
    ext=plpy.execute(tdc,[int_document,int_type,int_status,dat_document])
    return str(ext[0])
except Exception as e:
  exc_type, exc_obj, exc_tb = sys.exc_info()
  str_exception = str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)
  plpy.execute(plpy.prepare("INSERT INTO trigger_error_log (txt_error) VALUES ( $1)", ["text"]), [str_exception])
$$ LANGUAGE plpython VOLATILE;


CREATE TRIGGER bill_to_sap AFTER INSERT ON sales_master FOR EACH ROW EXECUTE PROCEDURE api_track('1');
CREATE TRIGGER return_to_sap AFTER INSERT ON sales_return FOR EACH ROW EXECUTE PROCEDURE api_track('6');
CREATE TRIGGER stock_trsr_to_sap AFTER INSERT ON branch_stock_master FOR EACH ROW EXECUTE PROCEDURE api_track('3');
CREATE TRIGGER advance_to_sap AFTER INSERT ON receipt FOR EACH ROW EXECUTE PROCEDURE api_track('4');
CREATE TRIGGER check_rtgs_to_sap AFTER UPDATE ON receipt FOR EACH ROW EXECUTE PROCEDURE api_track('5');
CREATE TRIGGER angamaly_stock AFTER INSERT ON stock_transfer FOR EACH ROW EXECUTE PROCEDURE api_track('8');
CREATE TRIGGER payment_to_sap AFTER INSERT ON payment FOR EACH ROW EXECUTE PROCEDURE api_track('7');
CREATE TRIGGER purchase_request AFTER INSERT ON purchase_request FOR EACH ROW EXECUTE PROCEDURE api_track('12');






































-- int_device_id = TD["new"]["deviceid"]
-- vchr_user_id = TD["new"]["userid"]
-- dat_time_punch = TD["new"]["logdate"]
-- dat_time = datetime.strptime(dat_time_punch, '%Y-%m-%d %H:%M:%S')
--
-- try:
--   rst_emp_data = plpy.execute(plpy.prepare("SELECT pemp.pk_bint_id, user_ptr_id, shft.pk_bint_id AS shift_id, time_shift_from, time_shift_to, time_shed_hrs, usd.fk_company_id FROM punching_emp as pemp LEFT JOIN user_details AS usd on usd.user_ptr_id=pemp.fk_user_id LEFT JOIN shift_allocation AS alctn ON alctn.fk_employee_id=usd.user_ptr_id AND dat_shift=$1 LEFT JOIN shift_schedule AS shft ON shft.pk_bint_id=alctn.fk_shift_id WHERE pemp.vchr_user_log_id=$2 and pemp.int_active != -1", ["date", "text"]), [dat_time_punch, vchr_user_id])
--   if not rst_emp_data:
--     ins_user = plpy.execute(plpy.prepare("SELECT user_ptr_id FROM user_details join auth_user on id=user_ptr_id WHERE is_active = true AND TRIM(TRIM(TRIM(vchr_employee_code,'MYGC-'),'MYGE-'),'MYGT-')=$1", ["text"]), [vchr_user_id])
--     if ins_user:
--       plpy.execute(plpy.prepare("INSERT INTO punching_emp (vchr_user_log_id, fk_user_id) VALUES ($1, $2)", ["text", "int"]), [vchr_user_id, ins_user[0]['user_ptr_id']])
--     else:
--       plpy.execute(plpy.prepare("INSERT INTO punching_emp (vchr_user_log_id) VALUES ($1)", ["text"]), [vchr_user_id])
--     rst_emp_data = plpy.execute(plpy.prepare("SELECT pemp.pk_bint_id, user_ptr_id, shft.pk_bint_id AS shift_id, time_shift_from, time_shift_to, time_shed_hrs, usd.fk_company_id FROM punching_emp as pemp LEFT JOIN user_details AS usd on usd.user_ptr_id=pemp.fk_user_id LEFT JOIN shift_allocation AS alctn ON alctn.fk_employee_id=usd.user_ptr_id AND dat_shift=$1 LEFT JOIN shift_schedule AS shft ON shft.pk_bint_id=alctn.fk_shift_id WHERE pemp.vchr_user_log_id=$2 and pemp.int_active != -1", ["date", "text"]), [dat_time_punch, vchr_user_id])
--   int_emp_id = rst_emp_data[0]["pk_bint_id"]
--
--   rst_admin_settings = plpy.execute(plpy.prepare("SELECT tim_punch_cool FROM admin_settings WHERE vchr_code='COOL_TIME' AND fk_company_id=$1", ["int"]), [rst_emp_data[0]["fk_company_id"]])
--   if rst_admin_settings and rst_emp_data[0]['time_shift_from']:
--     tim_cool = datetime.strptime(rst_admin_settings[0]['tim_punch_cool'],'%H:%M:%S').time()
--     tim_shift_start = datetime.strptime(rst_emp_data[0]['time_shift_from'],"%H:%M:%S").time()
--     time_shift_from = str(timedelta(hours=tim_shift_start.hour,minutes=tim_shift_start.minute,seconds=tim_shift_start.second) + timedelta(hours=tim_cool.hour,minutes=tim_cool.minute,seconds=tim_cool.second))
--   else:
--     time_shift_from = rst_emp_data[0]['time_shift_from']
--
--   rst_punchlog_data = plpy.execute(plpy.prepare("SELECT pk_bint_id, int_start_device_id, dat_start, int_end_device_id, dat_end, vchr_direction FROM punch_log WHERE fk_punchingemp_id=$1 AND dat_punch=$2", ["int","date"]), [int_emp_id, dat_time_punch])
--   int_punchlog_id = 0
--   bln_punch = True
--   if not rst_punchlog_data:
--     plpy.execute(plpy.prepare("INSERT INTO punch_log (int_start_device_id, fk_punchingemp_id, dat_start, dat_punch, vchr_direction) VALUES ($1, $2, $3, $4, 'IN')", ["int", "int", "timestamp", "date"]), [int_device_id, int_emp_id, dat_time_punch, dat_time_punch])
--     rst_punchlog_data = plpy.execute(plpy.prepare("SELECT pk_bint_id, int_start_device_id, dat_start, int_end_device_id, dat_end, vchr_direction FROM punch_log WHERE fk_punchingemp_id=$1 AND dat_punch=$2", ["int","date"]), [int_emp_id, dat_time_punch])
--     if rst_emp_data[0]['user_ptr_id'] and rst_emp_data[0]['shift_id']:
--       if datetime.strptime(time_shift_from,"%H:%M:%S").time() >= dat_time.time():
--         plpy.execute(plpy.prepare("INSERT INTO punching_attendance (fk_punchingemp_id, fk_shift_id, fk_log_id, int_ellc) VALUES ($1, $2, $3, 0)", ["int", "int", "int"]), [int_emp_id, rst_emp_data[0]['shift_id'], rst_punchlog_data[0]['pk_bint_id']])
--       else:
--         plpy.execute(plpy.prepare("INSERT INTO punching_attendance (fk_punchingemp_id, fk_shift_id, fk_log_id, int_ellc) VALUES ($1, $2, $3, 1)", ["int", "int", "int"]), [int_emp_id, rst_emp_data[0]['shift_id'], rst_punchlog_data[0]['pk_bint_id']])
--     else:
--       plpy.execute(plpy.prepare("INSERT INTO punching_attendance (fk_punchingemp_id, fk_log_id) VALUES ($1, $2)", ["int", "int"]), [int_emp_id, rst_punchlog_data[0]['pk_bint_id']])
--   elif ((rst_punchlog_data[0]["dat_end"] and (((dat_time - datetime.strptime(rst_punchlog_data[0]["dat_end"], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) >= 1 or ((datetime.strptime(rst_punchlog_data[0]["dat_end"], '%Y-%m-%d %H:%M:%S') - dat_time).total_seconds() / 60) >= 1)) or (not rst_punchlog_data[0]["dat_end"] and (((dat_time - datetime.strptime(rst_punchlog_data[0]["dat_start"], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) >= 1 or ((datetime.strptime(rst_punchlog_data[0]["dat_start"], '%Y-%m-%d %H:%M:%S') - dat_time).total_seconds() / 60) >= 1))) and dat_time < datetime.strptime(rst_punchlog_data[0]["dat_start"], '%Y-%m-%d %H:%M:%S'):
--     if rst_punchlog_data[0]["dat_end"] and datetime.strptime(rst_punchlog_data[0]["dat_end"], '%Y-%m-%d %H:%M:%S') > dat_time:
--       plpy.execute(plpy.prepare("UPDATE punch_log set int_start_device_id = $1, dat_start = $2 WHERE fk_punchingemp_id = $3 AND dat_punch = $4", ["int", "timestamp", "int", "date"]), [int_device_id, dat_time_punch, int_emp_id, dat_time_punch])
--     else:
--       plpy.execute(plpy.prepare("UPDATE punch_log set int_start_device_id = $1, dat_start = $2, int_end_device_id = $3, dat_end = $4 WHERE fk_punchingemp_id = $5 AND dat_punch = $6", ["int", "timestamp", "int", "timestamp", "int", "date"]), [int_device_id, dat_time_punch, rst_punchlog_data[0]["int_start_device_id"], rst_punchlog_data[0]["dat_start"], int_emp_id, dat_time_punch])
--   elif (rst_punchlog_data[0]["dat_end"] and ((dat_time - datetime.strptime(rst_punchlog_data[0]["dat_end"], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) >= 1) or (not rst_punchlog_data[0]["dat_end"] and ((dat_time - datetime.strptime(rst_punchlog_data[0]["dat_start"], '%Y-%m-%d %H:%M:%S')).total_seconds() / 60) >= 1):
--     plpy.execute(plpy.prepare("UPDATE punch_log set int_end_device_id = $1, dat_end = $2 WHERE fk_punchingemp_id = $3 AND dat_punch = $4", ["int", "timestamp", "int", "date"]), [int_device_id, dat_time_punch, int_emp_id, dat_time_punch])
--   else:
--     bln_punch = False
--
--   int_punchlog_id = rst_punchlog_data[0]['pk_bint_id']
--
--   punch_direction_update = plpy.prepare("UPDATE punch_log SET vchr_direction = $1 WHERE pk_bint_id = $2", ["text", "int"])
--   if bln_punch:
--     rst_logdetails_data = plpy.execute(plpy.prepare("SELECT * FROM punch_log_detail WHERE fk_log_id=$1 AND tim_end is null", ["int"]), [int_punchlog_id])
--     if not rst_logdetails_data:
--       plpy.execute(plpy.prepare("INSERT INTO punch_log_detail (fk_log_id, int_start_device_id, tim_start) VALUES ($1, $2, $3)", ["int", "int", "time without time zone"]), [int_punchlog_id, int_device_id, dat_time_punch])
--       plpy.execute(punch_direction_update, ["IN", int_punchlog_id])
--       if rst_emp_data[0]['user_ptr_id'] and rst_emp_data[0]['shift_id']:
--         if datetime.strptime(time_shift_from,"%H:%M:%S").time() >= datetime.strptime(rst_punchlog_data[0]['dat_start'],'%Y-%m-%d %H:%M:%S').time():
--           int_ellc = 0
--         else:
--           int_ellc = 1
--         plpy.execute(plpy.prepare("UPDATE punching_attendance SET fk_shift_id = $1, int_ellc = $2 WHERE fk_log_id = $3", ["int", "int", "int"]), [rst_emp_data[0]['shift_id'], int_ellc, int_punchlog_id])
--     else:
--       if dat_time.time() < datetime.strptime(rst_logdetails_data[0]['tim_start'], '%H:%M:%S').time():
--         plpy.execute(plpy.prepare("UPDATE punch_log_detail SET int_start_device_id = $1, tim_start = $2, int_end_device_id = $3, tim_end = $4 WHERE fk_log_id = $5 AND tim_end is null", ["int", "time without time zone", "int", "time without time zone", "int"]), [int_device_id, dat_time_punch, rst_logdetails_data[0]['int_start_device_id'], rst_logdetails_data[0]['tim_start'], int_punchlog_id])
--       else:
--         plpy.execute(plpy.prepare("UPDATE punch_log_detail SET int_end_device_id = $1, tim_end = $2 WHERE fk_log_id = $3 AND tim_end is null", ["int", "time without time zone", "int"]), [int_device_id, dat_time_punch, int_punchlog_id])
--       plpy.execute(punch_direction_update, ["OUT", int_punchlog_id])
--       tim_active = plpy.execute(plpy.prepare("SELECT SUM(tim_end-tim_start) AS tim_active, fk_log_id FROM punch_log_detail WHERE fk_log_id=$1 GROUP BY fk_log_id", ["int"]), [int_punchlog_id])
--       if rst_emp_data[0]['user_ptr_id'] and rst_emp_data[0]['shift_id']:
--         if datetime.strptime(time_shift_from,"%H:%M:%S").time() >= datetime.strptime(rst_punchlog_data[0]['dat_start'],'%Y-%m-%d %H:%M:%S').time():
--           if datetime.strptime(rst_emp_data[0]['time_shift_to'],'%H:%M:%S').time() > dat_time.time() or datetime.strptime(tim_active[0]['tim_active'],'%H:%M:%S') < datetime.strptime(rst_emp_data[0]['time_shed_hrs'],'%H:%M:%S'):
--             int_ellc = -1
--           else:
--             int_ellc = 0
--         else:
--           if datetime.strptime(rst_emp_data[0]['time_shift_to'],'%H:%M:%S').time() > dat_time.time() or datetime.strptime(tim_active[0]['tim_active'],'%H:%M:%S') < datetime.strptime(rst_emp_data[0]['time_shed_hrs'],'%H:%M:%S'):
--             int_ellc = 2
--           else:
--             int_ellc = 1
--         plpy.execute(plpy.prepare("UPDATE punching_attendance SET fk_shift_id=$1, int_ellc=$2, dur_active=$3 WHERE fk_log_id=$4", ["int", "int", "time without time zone", "int"]), [rst_emp_data[0]['shift_id'], int_ellc, tim_active[0]['tim_active'], int_punchlog_id])
--       else:
--         plpy.execute(plpy.prepare("UPDATE punching_attendance SET dur_active=$1 WHERE fk_log_id=$2", ["time without time zone", "int"]), [tim_active[0]['tim_active'], int_punchlog_id])
-- except Exception as e:
--     exc_type, exc_obj, exc_tb = sys.exc_info()
--     str_exception = str(e)+ ' in Line No: '+str(exc_tb.tb_lineno)
--     plpy.execute(plpy.prepare("INSERT INTO trigger_error_log (int_device_id, vchr_user_id, dat_time_punch, txt_error) VALUES ($1, $2, $3, $4)", ["int", "text", "timestamp", "text"]), [int_device_id, vchr_user_id, dat_time_punch, str_exception])
-- $$ LANGUAGE plpython VOLATILE;
