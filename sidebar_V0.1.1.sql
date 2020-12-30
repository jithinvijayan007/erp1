----------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- master
INSERT INTO main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order,vchr_icon_name) VALUES('MASTER','master',1,'');
-- Admin panel
INSERT INTO main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order,vchr_icon_name) VALUES('Admin Panel','adminpanel',2,'');
-- reports
INSERT INTO main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order,vchr_icon_name) VALUES('Reports','reports',3,'');
-- invoice
INSERT INTO main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order,vchr_icon_name) VALUES('Invoice','invoice',4,'');
-- accounts
INSERT INTO main_category(vchr_main_category_name,vchr_main_category_value,int_main_category_order,vchr_icon_name) VALUES('Accounts','accounts',5,'');

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- company
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'COMPANY','company',1,'mdi mdi-home-map-marker');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Company',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'COMPANY'),'addcompany',1,'false','/company/addcompany');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Company Permissions',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'COMPANY'),'companypermissions',2,'false','/companypermissions/companypermissions');
-- user
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'USER','user',2,'mdi mdi-face');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add User',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'USER'),'adduser',1,'false','/user/adduser');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl,vchr_editurl) VALUES('User List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'USER'),'userlist',2,'false','/user/listuser','/user/viewuser','/user/edituser');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add User Group',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'USER'),'addusergroup',3,'false','/user/usergroupadd');
--group
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'GROUP','group',2,'mdi mdi-face');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Group',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'GROUP'),'addgroup',1,'false','/group/addgroup');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Group List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'GROUP'),'grouplist',2,'false','/group/listgroup');
-- brand
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'BRAND','brand',3,'mdi mdi-tag-plus');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Brand',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'BRAND'),'addbrand',1,'false','/brand/brandlist');
-- product
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'PRODUCT','product',4,'mdi mdi-cart-plus');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Product',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PRODUCT'),'addproduct',1,'false','/product/addproduct');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl) VALUES('Product List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PRODUCT'),'productlist',2,'false','/product/productlist','/product/addproduct');
-- branch
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'BRANCH','branch',5,'mdi mdi-source-branch');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Branch',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'BRANCH'),'addbranch',1,'false','/branch/addbranch');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl) VALUES('Branch List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'BRANCH'),'branchlist',2,'false','/branch/branchlist','/branch/editbranch');
--category
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'CATEGORY','category',6,'mdi mdi-buffer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Category',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'CATEGORY'),'addcategory',1,'false','/category/addcategory');
-- stock request
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'STOCK REQUEST','stockrequest',7,'mdi mdi-package-variant');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Request',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK REQUEST'),'addrequest',1,'false','/stockrequest/stockrequest');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Request',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK REQUEST'),'listrequest',2,'false','/stockrequest/stockrequestlist','/stocktransfer/stocktransfer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Requested',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK REQUEST'),'listrequested',3,'false','/stockrequest/requestedlist','/stockrequest/stockrequestview');
-- stock transfer
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'STOCK TRANSFER','stockrequest',8,'mdi mdi-group');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Stock Transfer',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK TRANSFER'),'addstocktransfer',1,'false','/stocktransfer/stocktransfer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Transfer',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK TRANSFER'),'listtransfer',2,'false','/stocktransfer/transferlist','/stocktransfer/transferview');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Transfered',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK TRANSFER'),'listtransferd',3,'false','/stocktransfer/transferredlist','/stocktransfer/transferview');
-- item
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'ITEM','item',9,'mdi mdi-clipboard');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Item',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'additem',1,'false','/item/additem');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl) VALUES('List Item',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'itemlist',2,'false','/item/itemlist','/item/additem');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Item Category',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'additemcategory',3,'false','/item/additemcategory');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl) VALUES('Item Category List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'itemcategorylist',4,'false','/item/itemcategorylist','/item/edititemcategory');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Item Group',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'additemgroup',5,'false','/item/additemgroup');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl) VALUES('Item Group List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM'),'itemgrouplist',6,'false','/item/itemgrouplist');
-- supplier
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'SUPPLIER','supplier',10,'mdi mdi-account-network');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Supplier',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'SUPPLIER'),'addsupplier',1,'false','/supplier/addsupplier');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl,vchr_viewurl) VALUES('Supplier List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'SUPPLIER'),'supplierlist',2,'false','/supplier/listsupplier','/supplier/editsupplier','/supplier/viewsupplier');
-- invoice
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'INVOICE','invoice',11,'mdi mdi-file-check');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Sales Order List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'salesorderlist',1,'false','/invoice/saleslist');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Invoice List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'invoicelist',2,'false','/invoice/listinvoice');
-- dealer
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'DEALER','dealer',12,'mdi mdi-account-switch');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Dealer',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'DEALER'),'adddealer',1,'false','/dealer/adddealer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl,vchr_viewurl) VALUES('Dealer List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'DEALER'),'dealerlist',2,'false','/dealer/dealerlist','/dealer/editdealer','/dealer/viewdealer');
-- coupon
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'COUPON','coupon',13,'mdi mdi-ticket');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Coupon',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'COUPON'),'addcoupon',1,'false','/coupon/addcoupon');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl,vchr_viewurl) VALUES('Coupon List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'COUPON'),'couponlist',2,'false','/coupon/listcoupon','/coupon/editcoupon','/coupon/viewcoupon');
-- price
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'PRICE','price',14,'mdi mdi-coin');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Price',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PRICE'),'addprice',1,'false','/price/addprice');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_editurl) VALUES('Price List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PRICE'),'pricelist',2,'false','/price/listprice','/price/editprice');
-- purchase
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'PURCHASE','purchase',15,'mdi mdi-cart-outline');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Purchase Order',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PURCHASE'),'addpurchaseorder',1,'false','/purchase/purchaseorder');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('Purchase Order List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PURCHASE'),'purchaseorderlist',2,'false','/purchase/purchaseorderlist','/purchase/purchaseorderview');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add GRN',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PURCHASE'),'addgrn',3,'false','/purchase/purchase');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('GRN List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PURCHASE'),'grnlist',4,'false','/purchase/purchaselist','/purchase/purchaselistview');
-- stock
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'STOCK','stock',16,'mdi mdi-widgets');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Stock',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK'),'liststock',1,'false','/stock/list_stock','stock/view_stock_ack');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl) VALUES('List Branch Stock',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK'),'listbranchstock',2,'false','/stock/list_branch_stock');
-- groups
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'GROUP','group',16,'mdi mdi-widgets');
INSERT INTO menu_category(fk_sub_category_id,vchr_menu_category_name,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl,vchr_listurl,vchr_viewurl,vchr_editurl) VALUES((SELECT pk_bint_id from sub_category WHERE vchr_sub_category_value = 'group'),'Group','group',1,'true','/group/addgroup','/group/listgroup','group/viewgroup','group/editgroup');

-- item lookup
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'ITEM LOOKUP','itemlookup',17,'mdi mdi-widgets');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('Item Lookup',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ITEM LOOKUP'),'imeilookup',1,'false','/purchase/imeilookup','/purchase/imeilookup');
--daily sales report
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'REPORTS','reports',18,'mdi mdi-widgets');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_viewurl,vchr_listurl) VALUES('Daily Sales Report',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'REPORTS'),'reports',1,'false','/salesreport/dailysalesreport','/salesreport/dailysalesreport');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_viewurl,vchr_listurl) VALUES('Branch Stock Report',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'REPORTS'),'reports',1,'false','/report/stockreport','/report/stockreport');
-- day_closure
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'DAY ClOSURE','day_closure',19,'mdi mdi-widgets');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_viewurl,vchr_listurl) VALUES('Day Closure',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'DAY ClOSURE'),'day_closure_view',1,'false','/dayclosure/dayclosure','/dayclosure/dayclosure');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_viewurl,vchr_listurl) VALUES('Day Closure List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'DAY ClOSURE'),'day_closure_list',1,'false','/dayclosure/listdayclosure','/dayclosure/listdayclosure');


-- ==================13-09-2019======================
-- payment
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'PAYMENT','payment',7,'mdi mdi-cash-100');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Payment',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PAYMENT'),'addpayment',1,'false','/payment/addpayment');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Payment',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PAYMENT'),'listpayment',2,'false','/payment/listpayment','/payment/viewpayment');


-- receipt
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'RECEIPT','receipt',7,'mdi mdi-receipt');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Add Receipt',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'RECEIPT'),'addreceipt',1,'false','/receipt/addreceipt');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('List Receipt',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'RECEIPT'),'listreceipt',2,'false','/receipt/listreceipt','/receipt/viewreceipt');


-- tool settings
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'TOOLS SETTING','tools settings',10,'mdi mdi-home-map-marker');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl,vchr_editurl) VALUES('Settings List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'TOOLS SETTING'),'settings list',1,'false','/tools/list-tools','/tools/set-tools');

-- accounts map
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'ACCOUNTS','accounts',20,'mdi-square-inc-cash');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Accounts Map List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ACCOUNTS'),'accountsmaplist',1,'false','/accounting/listaccouting');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Accounts Map Add',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'ACCOUNTS'),'accountsmapadd',1,'false','/accounting/addaccouting');


-- sales return in invoice
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Sales Return',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'salesreturn',4,'false','/invoice/salesreturn');


-- ===========================
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'CUSTOMER','customer',21,'mdi mdi-human');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Customer Edit',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'CUSTOMER'),'editcustomer',1,'false','/customer/editcustomer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Invoice Customer Edit',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'CUSTOMER'),'invoicecustomer',1,'false','/invoice/invoicecustomer');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Customer History',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'CUSTOMER'),'history',1,'false','/customer/history');

INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl) VALUES('Non Saleable',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'STOCK'),'nonsaleable',4,'false','/stock/nonsalable');


-- case_closure
INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'CASE ClOSURE','day_closure',19,'mdi mdi-widgets');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_viewurl,vchr_listurl) VALUES('Case Closure',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'CASE ClOSURE'),'day_closure_view',1,'false','/caseclosure/caseclosure','/caseclosure/caseclosure');

-- bajaj
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Bajaj Finance',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'bajajlist',5,'false','/invoice/bajaj_list');


---change case closure to cash closure
---update sub_category set vchr_sub_category_name='CASH ClOSURE' where vchr_sub_category_name = 'CASE ClOSURE';
---update menu_category set vchr_menu_category_name='Cash Closure' where vchr_menu_category_name = 'Case Closure';
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Sales Return List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'salesreturnlist',6,'false','/invoice/salesreturnlist');
-- exchange list
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Exchange List',(SELECT pk_bint_id from sub_categ
ory WHERE vchr_sub_category_name = 'INVOICE'),'exchangelist',7,'false','/invoice/exchangelist');

-- service list
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Service List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'servicelist',3,'false','/invoice/servicelist');

INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Purchase Request',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'PURCHASE'),'purchaserequest',1,'false','/purchaserequest/request');

-- Approve list
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl) VALUES('Approve List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'INVOICE'),'approvelist',4,'false','/invoice/approvelist');


update sub_category set vchr_sub_category_name='IMEI LOOKUP',vchr_sub_category_value='imeilookup' where vchr_sub_category_value='itemlookup';
update menu_category set vchr_menu_category_name='Imei Lookup',vchr_menu_category_value='imeilookup' where vchr_menu_category_value='imeilookup';

update sub_category set vchr_sub_category_name='ADMIN SETTINGS',vchr_sub_category_value='adminsettings' where vchr_sub_category_value='tools settings';
-- update menu_category set vchr_menu_category_name='Imei Lookup',vchr_menu_category_value='imeilookup' where vchr_menu_category_value='imeilookup';


INSERT INTO sub_category(fk_main_category_id,vchr_sub_category_name,vchr_sub_category_value,int_sub_category_order,vchr_icon_name) VALUES((SELECT pk_bint_id from main_category WHERE vchr_main_category_name = 'MASTER'),'TOOLS SETTING','tools settings',10,'mdi mdi-home-map-marker');
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_addurl,vchr_editurl) VALUES('Settings List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'TOOLS SETTING'),'settings list',1,'false','/tools/list-tools','/tools/set-tools');

-- Receipt Order list
INSERT INTO menu_category(vchr_menu_category_name,fk_sub_category_id,vchr_menu_category_value,int_menu_category_order,bln_has_children,vchr_listurl,vchr_viewurl) VALUES('Receipt Order List',(SELECT pk_bint_id from sub_category WHERE vchr_sub_category_name = 'RECEIPT'),'receipt-order-list',3,'false','/receipt/receipt-order-list','/receipt/addreceipt');
