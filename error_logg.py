import psycopg2
import pandas as pd
# conn = psycopg2.connect("host=localhost dbname=lastpos user=admin password=tms@123")
# cur = conn.cursor()
import smtplib
from os.path import basename
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import copy
import sys
import sys, os
from django.conf import settings


global er_logger
def er_logger(e, details):
    try:
        body = e + str(details)
        # fromaddr = "amrutha.n@travidux.com"
        # toaddr = "amrutha.n@travidux.com"
        toaddr = 'arunkumar@travidux.com'
        msg = MIMEMultipart()
        # msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Error"
        msg.attach(MIMEText(body, 'plain'))

        date  = datetime.strftime(datetime.now(),'%d_%m_%Y')
        filename = date+'.log'
        attachment = open(settings.BASE_DIR + '/log/'+date+'.log', "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)
        server = smtplib.SMTP('smtp.pepipost.com', 587)
        server.starttls()
        server.login("shafeer","Tdx@9846100662")
        text = msg.as_string()
        server.sendmail("info@enquirytrack.com",toaddr,text)
        server.quit()

    except Exception as e:
        raise


if __name__ == '__main__':
    er_logger()


# import logging
# import logging.handlers
# import smtplib
# import threading
# import sys, os
# from datetime import datetime
# def smtpThreadHolder(mailhost, port, username, password, fromaddr, toaddrs, msg):
#     try:
#         smtp = smtplib.SMTP(mailhost, port)
#     except:
#         logging.error("Trying to make smtp variable")
#
#     print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
#     if username:
#         smtp.ehlo()# for tls add this line
#         smtp.starttls()# for tls add this line
#         smtp.ehlo()# for tls add this line
#     smtp.login(username, password)
#     smtp.sendmail(fromaddr, toaddrs, msg)
#     smtp.quit()
# class ThreadedTlsSMTPHandler(logging.handlers.SMTPHandler):
#     def emit(self, record):
#         try:
#             import string #for tls add this line
#             try:
#                 from email.utils import formatdate
#             except ImportError:
#                 formatdate = self.date_time
#
#             print(record +'printtttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
#
#             port = self.mailport
#             import pdb; pdb.set_trace()
#             if not port:
#                 port = smtplib.SMTP_PORT
#             msg = self.format(record)
#             msg = ("From: %s\r\nTo"
#                 "%s\r\nSubject:"
#                 "%s\r\nDate: %s\r\n\r\n%s"
#                 %(self.fromaddr, string.join( self.toaddrs, ","), self.getSubject(record),formatdate(), msg))
#             thread = threading.Thread(target = smtpThreadHolder, args = (self.mailhost, port, self.username, self.password, self.fromaddr, self.toaddrs, msg))
#             thread.daemon = True
#             thread.start()
#         except(KeyboardInterrupt, SystemExit):
#             raise
#         except:
#             self.handleError(record)
# #(obj) Needed to access the class's name for python 2.6+
# #Not needed in python 3+ I believe
# class SomeClass(object):
#     def __init__(self):
#         self.setupLogging()
#
#     def setupLogging(self):
#         logDir  = '/Logs/'
#         time = datetime.strftime(datetime.now(),'%d_%m_%Y_%H_%M')
#         logFile = settings.BASE_DIR+ logDir + time+'.log'
#         # if not os.path.exists(logDir):
#         #     os.makedirs(logDir)
#
#         # create the file if it doesn't exist
#         if not os.path.exists(logFile):
#             with open(logFile, 'w+') as f:
#                 f.write('======== LOGGING FILE FOR SOMELOG ======\n')
#
#         self.logger = logging.getLogger(type(self).__name__)
#         self.logger.setLevel(logging.DEBUG)
#         formatter = logging.Formatter(
#                 '[%(name)-5.5s | %(levelname)-4.47s]'
#                 ' [%(threadName)-10.10s | Func: %(funcName)-10.10s | LN:%(lineno)-4.4d| %(asctime)-21s]'
#                 '  %(message)s')
#         streamHandler = logging.StreamHandler()
#         streamHandler.setFormatter(formatter)
#         streamHandler.setLevel(logging.DEBUG)
#         self.logger.addHandler(streamHandler)
#         fileHandler = logging.FileHandler(logFile, mode='a', encoding=None, delay=False)
#         fileHandler.setFormatter(formatter)
#         fileHandler.setLevel(logging.ERROR)
#         self.logger.addHandler(fileHandler)
#         host = 'smtp.gmail.com'
#         port = 587
#         destEmails = ['amrutha.n@travidux.com']
#         fromEmail = 'amrutha.n@travidux.com'
#         fromPass = ''
#
#         gm = ThreadedTlsSMTPHandler(
#             mailhost = (host, port),
#             fromaddr = fromEmail,
#             toaddrs = destEmails,
#             subject = 'Error!',
#             credentials = (
#               fromEmail,
#               fromPass
#               )
#             )
#         gm.setLevel(logging.ERROR)
#         gm.setFormatter(formatter)
#         self.logger.addHandler(gm)
#         #Send yourself an email with the body Test
#         self.logger.error("TEST")
   # def log_error(self,str_msg,dct_error,int_critical=0):
   #     #dct_error = {'user' : str(request.user.id),'line No': str(exc_tb.tb_lineno) }
   #     self.logger.error(e, extra=dct_error)
   #     send_mail()
