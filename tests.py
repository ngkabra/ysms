"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".
"""
import unittest
from django.test import TestCase
from datetime import *
from models import YUser,Message,SentMessage,Group,Statistics,Company

class TestBasic(TestCase):
    fixtures = ['ysms.json',]
    def test_basic(self):
        company=Company.objects.get(name='smriti.com')
        company1=Company.objects.get(name='wogma.com')
        print company
        print company1
        
    def test_fetch_msgs(self):
         cnt = YUser.objects.fetch_yammer_msgs()
         print "%d Messages Fetched" % cnt
 
    def test_sms_msgs(self):
         sms_to_send = Message.objects.all()  
         if sms_to_send:
             cnt=Message.objects.to_send_sms()  
             if cnt==0:
                 print"No new sms to send"
             print"%d Sms Sent" % cnt
         else:    
              print "There is no sms to Send"
         company=Company.objects.get(name='smriti.com')
         company1=Company.objects.get(name='wogma.com')     
         compcnt=Statistics.objects.get(company=company)
         compcnt1=Statistics.objects.get(company=company1)
         print"smriti.com count %d and wogma.com count %d" % (compcnt.sms_sent,compcnt1.sms_sent)
         
    def post_msgs(self):
         cnt = SentMessage.objects.post_pending()
         print '%d msgs posted' % cnt
        
    def test_clean_msgs(self):
         now = datetime.now()
         week = timedelta(7)
         date = now - week
         Message.objects.delete_messages(date)
         SentMessage.objects.delete_messages(date)
         print "Sms Deleted"    
         
    def test_login(self):
         #self.client.login(username='samrudha', password='samrudha') 
         response=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad staff 7 khoon maff theatre me patta saaf')
         print response  