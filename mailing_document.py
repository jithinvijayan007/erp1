from branch_stock.models import MailingProduct
import pandas as pd

auto_mailer=pd.read_excel('Auto Mailer Reports.xlsx','mail id')
from products.models import Products

for data in auto_mailer.iterrows():
          vchr_product=''
          lst_product=[]
          ins_mailing=MailingProduct()
          if data[1]['NAME']:
             ins_mailing.vchr_name=data[1]['NAME']
          if data[1]['email id']:
             ins_mailing.vchr_email = data[1]['email id']
          if data[1]['MOBILE']=='√':
              vchr_product='MOBILE'
              lst_product.append(vchr_product)
          if data[1]['TAB']=='√':
              vchr_product='TABLET'
              lst_product.append(vchr_product)
          if data[1]['LAPTOP']=='√':
              vchr_product='LAPTOP'
              lst_product.append(vchr_product)
          if data[1]['TV']=='√':
              vchr_product = 'TV'
              lst_product.append(vchr_product)
          if data[1]['AC']=='√':
              vchr_product = 'AIR CONDITIONER'
              lst_product.append(vchr_product)
          if data[1]['RIG']=='√':
              vchr_product = 'RIG'
              lst_product.append(vchr_product)
          if data[1]['DESKTOP']=='√':
              vchr_product = 'DESKTOP'
              lst_product.append(vchr_product)
          if data[1]['CAMERA']=='√':
              vchr_product = 'CAMERA'
              lst_product.append(vchr_product)
        #   if data[1]['DOMO']=='√':
        #       vchr_product = 'MYG DOMO'
        #       lst_product.append(vchr_product)
          if data[1]['IT PRODUCTS']=='√':
              vchr_product = 'IT PRODUCT'
              lst_product.append(vchr_product)
          if data[1]['SMART CHOICE']=='√':
              vchr_product = 'SMART CHOICE'
              lst_product.append(vchr_product)
          if data[1]['SPARE']=='√':
              vchr_product = 'SPARE'
              lst_product.append(vchr_product)
          if data[1]['ACC BGN.ACC ZRD,HVA,BT SPEAKER,SPEAKER,SMARTWATCH,WATCH']=='√':
              lst_product.extend(['ACC BGN','ACC ZRD','HVA','BT SPEAKERS','SPEAKER','SMART WATCH','WATCH']


          )
          for product in lst_product:

            if Products.objects.filter(vchr_name=product).first()==None:
                continue
            MailingProduct.objects.create(fk_product_id=Products.objects.filter(vchr_name=product).first().pk_bint_id,vchr_name=data[1]['NAME'],vchr_email=data[1]['email id'])

for data in auto_mailer.iterrows():
    if data[1]['ALL PRODUCTS']=='√':
        MailingProduct.objects.create(vchr_name =data[1]['NAME'],vchr_email=data[1]['email id'])

