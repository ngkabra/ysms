"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".
"""
import unittest
from django.test import TestCase
from datetime import *
from models import YUser,Message,SentMessage,Group,Statistics,Company
from django.shortcuts import get_object_or_404

class TestBasic(TestCase):
    fixtures = ['ysms.json',]
    def setUp(self):
         group_id=115047
         content='Test Message'
         company=Company.objects.get(name='smriti.com')
         yuser=YUser.objects.get(fullname='samrudha',company=company)
         yuser1=YUser.objects.get(fullname='dhabbimirichi',company=company)
         yuser.post_message(content,group_id)
         self.yuser=yuser  
         self.yuser1=yuser1
         self.group_id=group_id
         self.message=content
         
    def tearDown(self):
         all_messages=Message.objects.all()
         for message in all_messages:
             message.from_user.yammer_api().messages.delete(message.message_id)    
     
    def test_fetch_msgs(self):
         count=1
         cnt = YUser.objects.fetch_yammer_msgs()
         all_messages=Message.objects.all()
         self.assertEqual(count,cnt)
         for message in all_messages:
             self.assertEqual(self.group_id,message.group.group_id)
             self.assertEqual(self.yuser,message.from_user)
             self.assertEqual(self.yuser1,message.to_user)
             self.assertEqual(self.message,message.message)
         
         
         
class TestAdvanced(TestCase):
    fixtures = ['ysms.json',]
    def setUp(self):
         companysmriti=Company.objects.get(name='smriti.com')
         yusersmriti=YUser.objects.get(fullname='samrudha',company=companysmriti)
         yusersmriti1=YUser.objects.get(fullname='dhabbimirichi',company=companysmriti)
         companywogma=Company.objects.get(name='wogma.com')
         yuserwogma=YUser.objects.get(fullname='samrudha',company=companywogma)
         yuserwogma1=YUser.objects.get(fullname='babdu reviewwala',company=companywogma)         
         self.companysmriti=companysmriti
         self.companywogma=companywogma
         self.yusersmriti=yusersmriti
         self.yusersmriti1=yusersmriti1
         self.yuserwogma=yuserwogma
         self.yuserwogma1=yuserwogma1  
         self.sms_pending=4
         self.post_pending=0
         self.statssmriti=2
         self.statswogma=2
         self.count=4
         self.text='Thank you, your message has been posted'
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
         for message in all_messages:
             message.from_user.yammer_api().messages.delete(message.message_id)    
    
    def fetch_msgs(self):
         cnt = YUser.objects.fetch_yammer_msgs()
         
         
    def test_clean_msgs(self):
         now = datetime.now()
         week = timedelta(7)
         date = now - week
         Message.objects.delete_messages(date)
         SentMessage.objects.delete_messages(date)
         print "Sms Deleted"    
         
    def test_receive_sms(self):
         response=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad staff 7 khoon maff theatre me patta saaf')
         response1=self.client.get('/ysms/receive_sms/?msisdn=919922900383&content=samvad staff 7 khoon maff theatre me patta saaf')
         response2=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad Bakwaas movies Patiala House kali ko boli pasand nahi')
         response3=self.client.get('/ysms/receive_sms/?msisdn=919922900383&content=samvad Bakwaas movies Patiala House kali ko boli pasand nah')
         self.assertContains(response, self.text,status_code=200,) 
         self.assertContains(response1, self.text,status_code=200,)
         self.assertContains(response2,self.text,status_code=200,)
         self.assertContains(response3, self.text,status_code=200,)
         smriticnt=Statistics.objects.get(company=self.companysmriti)
         wogmacnt=Statistics.objects.get(company=self.companywogma)
         self.assertEqual(self.statssmriti,smriticnt.sms_received)
         self.assertEqual(self.statswogma,wogmacnt.sms_received)
             
    def test_sms_msgs(self):
         cnt=Message.objects.to_send_sms()
         self.assertEqual(self.count,cnt)  
         smriticnt=Statistics.objects.get(company=self.companysmriti)
         wogmacnt1=Statistics.objects.get(company=self.companywogma)
         self.assertEqual(self.statssmriti,smriticnt.sms_sent)
         self.assertEqual(self.statswogma,wogmacnt1.sms_sent)
                
    def test_index(self):
         '''self.client.login(username='samrudhasmriti', password='samrudha')
         self.check_contextindex(company='smriti')
         self.client.logout()'''
         self.client.login(username='samrudhawogma', password='samrudha')
         self.check_contextindex(company='wogma')
         self.client.logout()
         
    def check_contextindex(self,company):  
         response=self.client.get('/ysms/')
         if company == 'smriti':
             self.assertEqual(self.yusersmriti, response.context['yusers'][0])
             self.assertEqual(self.yusersmriti1,response.context['yusers'][1])
         else:
             self.assertEqual(self.yuserwogma, response.context['yusers'][0])
             self.assertEqual(self.yuserwogma1,response.context['yusers'][1])
         self.assertEqual(self.sms_pending,response.context['sms_pending'] )
         self.assertEqual(self.post_pending,response.context['post_pending'])
           
    def test_delete_user(self):
         self.client.login(username='samrudhasmriti', password='samrudha')
         response=self.client.get('/ysms/delete-user/2/')  
         self.assertContains(response,text='', count=None,status_code=302,)
         self.client.logout()   