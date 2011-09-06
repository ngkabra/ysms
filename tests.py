"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".
"""
import unittest
from django.test import TestCase
from datetime import *
from models import YUser,Message,SentMessage,Group,Statistics,Company
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.test.client import Client

class TestBasic(TestCase):
    fixtures = ['ysms.json',]
    def setUp(self):
         self.group_id=115047
         self.content='Test Message'
         self.content1='Test Message for group'
         company=Company.objects.get(name='smriti.com')
         self.yuser=YUser.objects.get(fullname='samrudha',company=company)
         self.yuser1=YUser.objects.get(fullname='dhabbimirichi',company=company)
         self.yuser2=YUser.objects.get(fullname='kulkarni',company=company)
         self.yuser.post_message(self.content,None)
         self.yuser.post_message(self.content1,self.group_id)
         self.yuser1.post_message(self.content,None)
         self.yuser1.post_message(self.content1,self.group_id)
         
    def tearDown(self):
         all_messages=Message.objects.all()
         for message in all_messages:
             message.from_user.yammer_api().messages.delete(message.message_id)   
     
    def test_fetch_msgs(self):
         count=1
         cnt = YUser.objects.fetch_yammer_msgs()
         # Message is posted by samrudha without group 
         message=Message.objects.get(from_user=self.yuser,to_user=self.yuser1,group=None)
         self.assertEqual(None,message.group)
         self.assertEqual(self.yuser,message.from_user)
         self.assertEqual(self.yuser1,message.to_user)
         self.assertEqual(self.content,message.message)
         message=Message.objects.get(from_user=self.yuser,to_user=self.yuser2,group=None)
         self.assertEqual(None,message.group)
         self.assertEqual(self.yuser,message.from_user)
         self.assertEqual(self.yuser2,message.to_user)
         self.assertEqual(self.content,message.message)
         # Message is posted by samrudha for a group 
         group=Group.objects.get(group_id=self.group_id)
         message=Message.objects.get(from_user=self.yuser,to_user=self.yuser1,group=group)
         self.assertEqual(self.group_id,message.group.group_id)
         self.assertEqual(self.yuser,message.from_user)
         self.assertEqual(self.yuser1,message.to_user)
         self.assertEqual(self.content1,message.message)
         self.assertRaises(Message.DoesNotExist,
            Message.objects.get,
            from_user=self.yuser,to_user=self.yuser2,group=group
        )
         # Message is posted by dhabbimirichi for group
         group=Group.objects.get(group_id=self.group_id)
         message=Message.objects.get(from_user=self.yuser1,to_user=self.yuser,group=group)
         self.assertEqual(self.group_id,message.group.group_id)
         self.assertEqual(self.yuser1,message.from_user)
         self.assertEqual(self.yuser,message.to_user)
         self.assertEqual(self.content1,message.message)
         # Message is posted by dhabbimirichi without a group 
         self.assertRaises(Message.DoesNotExist,
            Message.objects.get,
            from_user=self.yuser1,to_user=self.yuser,group=None
        )
         
         
class Testreceive_and_send(TestCase):
    fixtures = ['ysms.json',]
    def test_receive_send(self):
        self.group_id=115047
        self.group_smriti=0
        self.yammer_mes='7 khoon maff theatre me patta saaf'
        self.companysmriti=Company.objects.get(name='smriti.com')
        self.yuser=YUser.objects.get(fullname='samrudha',company=self.companysmriti)
        self.yuser1=YUser.objects.get(fullname='dhabbimirichi',company=self.companysmriti)
        self.yuser2=YUser.objects.get(fullname='kulkarni',company=self.companysmriti)
        self.text='Thank you, your message has been posted'
        self.companywogma=Company.objects.get(name='wogma.com')
        response=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad smriti 7 khoon maff theatre me patta saaf')
        response1=self.client.get('/ysms/receive_sms/?msisdn=917588234173&content=samvad staff 7 khoon maff theatre me patta saaf')
        response2=self.client.get('/ysms/receive_sms/?msisdn=919922900383&content=samvad staff 7 khoon maff theatre me patta saaf') 
        self.assertContains(response, self.text,status_code=200,) 
        self.assertContains(response1, self.text,status_code=200,) 
        self.assertContains(response2, self.text,status_code=200,)
        smriticnt=Statistics.objects.get(company=self.companysmriti)
        self.assertRaises(Statistics.DoesNotExist,
            Statistics.objects.get,
            company=self.companywogma
        )
        self.assertEqual(3,smriticnt.sms_received)
        self.fetch_msgs()  
        cnt=Message.objects.to_send_sms()
        self.assertEqual(3,cnt)  
        smriticnt=Statistics.objects.get(company=self.companysmriti)
        self.assertRaises(Statistics.DoesNotExist,
            Statistics.objects.get,
            company=self.companywogma
        )
        self.assertEqual(3,smriticnt.sms_sent)
        self.sent_messages_check()
    
    def sent_messages_check(self):
        all_messages=SentMessage.objects.count()
        self.assertEqual(3,all_messages)
        group=Group.objects.get(group_id=self.group_smriti,company=self.companysmriti)
        message=SentMessage.objects.get(yuser=self.yuser1,group=group)
        self.assertEqual(message.yuser,self.yuser1)
        self.assertEqual(message.message,self.yammer_mes)
        self.assertEqual(message.group,group)
        group=Group.objects.get(group_id=self.group_id,company=self.companysmriti)
        message=SentMessage.objects.get(yuser=self.yuser1,group=group)
        self.assertEqual(message.yuser,self.yuser1)
        self.assertEqual(message.message,self.yammer_mes)
        self.assertEqual(message.group,group)
        message=SentMessage.objects.get(yuser=self.yuser,group=group)
        self.assertEqual(message.yuser,self.yuser)
        self.assertEqual(message.message,self.yammer_mes)
        self.assertEqual(message.group,group)
              
    def fetch_msgs(self):
         cnt = YUser.objects.fetch_yammer_msgs()  
         message=Message.objects.get(from_user=self.yuser1,to_user=self.yuser2,group=None)
         self.assertEqual(None,message.group)
         self.assertEqual(self.yuser1,message.from_user)
         self.assertEqual(self.yuser2,message.to_user)
         self.assertEqual(self.yammer_mes,message.message)
         self.assertRaises(Message.DoesNotExist,
            Message.objects.get,
            from_user=self.yuser1,to_user=self.yuser,group=None
        )
         group=Group.objects.get(group_id=self.group_id,company=self.companysmriti)
         message=Message.objects.get(from_user=self.yuser1,to_user=self.yuser,group=group)
         self.assertEqual(group,message.group)
         self.assertEqual(self.yuser1,message.from_user)
         self.assertEqual(self.yuser,message.to_user)
         self.assertEqual(self.yammer_mes,message.message)
         self.assertRaises(Message.DoesNotExist,
            Message.objects.get,
             from_user=self.yuser1,to_user=self.yuser2,group=group
        )
         message=Message.objects.get(from_user=self.yuser,to_user=self.yuser1,group=group)
         self.assertEqual(group,message.group)
         self.assertEqual(self.yuser,message.from_user)
         self.assertEqual(self.yuser1,message.to_user)
         self.assertEqual(self.yammer_mes,message.message)
         self.assertRaises(Message.DoesNotExist,
            Message.objects.get,
             from_user=self.yuser,to_user=self.yuser2,group=group
        )
    def tearDown(self):
         all_messages=Message.objects.all()
         for message in all_messages:
             message.from_user.yammer_api().messages.delete(message.message_id)    
          
            
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
         self.sms_pending=11
         self.post_pending=0
         self.statssmriti=5
         self.statswogma=6
         self.count=11
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
         
         
    '''def test_clean_msgs(self):
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
         self.assertEqual(2,smriticnt.sms_received)
         self.assertEqual(2,wogmacnt.sms_received)
         
             
    def test_sms_msgs(self):
         cnt=Message.objects.to_send_sms()
         self.assertEqual(self.count,cnt)  
         smriticnt=Statistics.objects.get(company=self.companysmriti)
         wogmacnt1=Statistics.objects.get(company=self.companywogma)
         self.assertEqual(self.statssmriti,smriticnt.sms_sent)
         self.assertEqual(self.statswogma,wogmacnt1.sms_sent)'''
                
    def test_indexsmriti(self):
         self.client.login(username='samrudhasmriti', password='samrudha')
         self.check_contextindex(company='smriti')
         self.client.logout()
         
    def test_indexwogma(self):     
         self.client.login(username='samrudhawogma', password='samrudha')
         self.check_contextindex(company='wogma')
         self.client.logout()
         
    def check_contextindex(self,company):  
         
         if company == 'smriti':
             response=self.client.get('/ysms/')
             self.assertEqual(self.yusersmriti, response.context['yusers'][0])
             self.assertEqual(self.yusersmriti1,response.context['yusers'][1])
         else:
             response=self.client.get('/ysms/')
             self.assertEqual(self.yuserwogma, response.context['yusers'][0])
             self.assertEqual(self.yuserwogma1,response.context['yusers'][1])
         self.assertEqual(self.sms_pending,response.context['sms_pending'] )
         self.assertEqual(self.post_pending,response.context['post_pending'])
    
        
    '''def test_delete_user(self):
         self.client.login(username='samrudhasmriti', password='samrudha')
         yuser=YUser.objects.get(id=5)
         self.assertEqual('dhabbimirichi',yuser.fullname)
         response=self.client.get('/ysms/delete-user/5/')
         self.assertRaises(YUser.DoesNotExist,
            YUser.objects.get,
            fullname="dhabbimirichi"
        )
         self.assertContains(response,text='', count=None,status_code=302,)
         self.client.logout() 
         #test_delete user different Company login 
         self.client.login(username='samrudhawogma', password='samrudha')
         self.assertRaises(TemplateDoesNotExist,self.client.get,'/ysms/delete-user/5/')
         self.client.logout() 
         #test_delete user without login
         self.client.login(username='samru', password='samrudha')
         self.assertRaises(TemplateDoesNotExist,self.client.get,'/ysms/delete-user/5/')
         self.client.logout()'''