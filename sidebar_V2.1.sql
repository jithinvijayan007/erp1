----update queries
insert into main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order) values('TRANSACTIONS','transactions',5);
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('CASH ClOSURE');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'reports') where vchr_sub_category_name in ('STOCK','ITEM LOOKUP','REPORTS');
update sub_category set vchr_sub_category_name = 'SALES' where vchr_sub_category_name = 'REPORTS';
insert into main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order) values('SETTINGS','settings',6);
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'settings') where vchr_sub_category_name in ('TOOLS SETTING');


serviceinvoicelist
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Service Invoice',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'serviceinvoice',5,'false','/invoice/serviceinvoicelist');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Credit Approval List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'creditapprovallist',9,'false','/invoice/creditapprovallist');
update menu_category set vchr_menu_category_name='Jobsheet List',vchr_menu_category_value='jobsheetlist' where vchr_menu_category_value='servicelist';

INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'TRANSACTIONS'),'LEDGER','ledger',9,'mdi mdi-clipboard');


INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Ledger Statements',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'LEDGER'),'ledgerstatement',2,'false','/ledger/ledgerstatement');
-- INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Service Invoice',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'serviceinvoice',3,'false','/invoice/servicelist');
-- update menu_category set vchr_menu_category_name='Jobsheet List',vchr_menu_category_value='jobsheetlist' where vchr_menu_category_value='servicelist';



update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('INVOICE');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('RECEIPT');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('PAYMENT');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('STOCK REQUEST');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('STOCK TRANSFER');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('PURCHASE');
update sub_category set fk_main_category_id = (select pk_bint_id from main_category where vchr_main_category_value = 'transactions') where vchr_sub_category_name in ('DAY ClOSURE');
  INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Imei Transfer',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK TRANSFER'),'imei_scan',4,'false','/stocktransfer/imei_scan');
  UPDATE menu_category set vchr_menu_category_name='Batch Transfer' where vchr_menu_category_name='Add Stock Transfer';

-- ledger cashbook sidebar query - 6-Aug-2020
  INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Cash Book',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'LEDGER'),'cashbook',2,'false','/ledger/cashbook');
