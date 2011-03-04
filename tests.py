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
    def setUp(self):
         index=1
         all_user=YUser.objects.all()
         for yuser in all_user:
             content='Test Message %d'% index
             yuser.post_message(content,None)
             index+=1 
         self.fetch_msgs()    
    def tearDown(self):
         self.fetch_msgs() 
         all_messages=Message.objects.all()
         print all_messages
         for message in all_messages:
             print message.message_id
             message.from_user.yammer_api().messages.delete(message.message_id)    
    
    def fetch_msgs(self):
         cnt = YUser.objects.fetch_yammer_msgs()
         print "%d Messages Fetched" % cnt
         
    def test_clean_msgs(self):
         now = datetime.now()
         week = timedelta(7)
         date = now - week
         Message.objects.delete_messages(date)
         SentMessage.objects.delete_messages(date)
         print "Sms Deleted"    
         
    def test_receive_sms(self):
         response=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad staff 7 khoon maff theatre me patta saaf')
         response=self.client.get('/ysms/receive_sms/?msisdn=919922900383&content=samvad staff 7 khoon maff theatre me patta saaf')
         response1=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad Bakwaas movies Patiala House kali ko boli pasand nahi')
         response1=self.client.get('/ysms/receive_sms/?msisdn=919922900383&content=samvad Bakwaas movies Patiala House kali ko boli pasand nah')
         print response,response1  
         company=Company.objects.get(name='smriti.com')
         company1=Company.objects.get(name='wogma.com')     
         compcnt=Statistics.objects.get(company=company)
         compcnt1=Statistics.objects.get(company=company1)
         print"smriti.com count %d and wogma.com count %d" % (compcnt.sms_received,compcnt1.sms_received)
             
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
                
    def test_index(self):
         self.client.login(username='samrudhasmriti', password='samrudha')
         response=self.client.get('/ysms/')
         print response.context['yusers']
         print 'post pending %d'% response.context['post_pending']
         print 'sms pending %d' % response.context['sms_pending']
         self.client.logout()
         
    '''def test_delete_user(self):
         self.client.login(username='samrudhasmriti', password='samrudha')
         response=self.client.get('/ysms/delete-user/130/')  
         print response
         self.client.logout()'''     