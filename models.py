from datetime import datetime

from django.db import models
from yammer import Yammer 
from django.conf import settings
from django.db.models import Max

# Create your models here.

class YUserManager(models.Manager):
    def authenticate_users (self):
        for yuser in self.all():
            yuser.update_messages()
    
    
    
class YUser(models.Model):
    yammer_user_id=models.BigIntegerField(default=0)
    update_max_message_id=models.BigIntegerField(default=0)
    fullname=models.CharField(max_length=100)
    mobile_no=models.CharField(max_length=13)
    oauth_token=models.CharField(max_length=150)
    oauth_token_secret=models.CharField(max_length=150)
    def __unicode__(self):
        return self.fullname
    objects = YUserManager()
    
    def update_messages(self):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET,
                 oauth_token=self.oauth_token,
                 oauth_token_secret=self.oauth_token_secret)    
        all_messages= yammer.messages.sent(newer_than=self.update_max_message_id)
        self.get_all_messages(all_messages)  
        self.get_max_message_id()

    def post_message(self,content):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET,
                 oauth_token=self.oauth_token,
                 oauth_token_secret=self.oauth_token_secret) 
        yammer.messages.post(content)         

    def get_all_messages(self,all_messages):
        for message in all_messages:         
            yammer_mes=Message(from_user=self,to_user=None,message=message['body']['parsed'],thread_id=message['thread_id'],message_id=message['id'])
            yammer_mes.save() 
            
    def get_max_message_id(self):
        q =Message.objects.filter(from_user=self).aggregate(Max('message_id'))
        if q.get('message_id__max', 0):
            self.update_max_message_id = q['message_id__max']
            self.save()    


class MessageManager(models.Manager):   
    def delete_messages(self,date):
        del_messages=Message.objects.filter(sms_sent__lt=date).all() 
        del_messages.delete()
                       
class Message(models.Model):
    thread_id=models.BigIntegerField(default=0)
    message_id=models.BigIntegerField(primary_key=True, default=0)
    from_user=models.ForeignKey(YUser, null=True, blank=True)
    to_user=models.ForeignKey(YUser,related_name='to_user_set', null=True, blank=True)
    message=models.CharField(max_length=140, editable=True)
    sms_sent=models.DateTimeField(null=True,editable=False)
    def __unicode__(self):
        return self.message
    objects = MessageManager()
    
class SentMessage(models.Model): 
    yuser=models.ForeignKey(YUser)
    message=models.CharField(max_length=140, editable=False)  
    received_time=models.DateTimeField(null=True, blank=True, editable=False)
    sent_time= models.DateTimeField(null=True, blank=True, editable=False) 
    
    def save(self):
        if not self.received_time:
            self.received_time = datetime.now()
        return super(SentMessage, self).save()

    def __unicode__(self):
        return self.message 
