from datetime import datetime

from django.db import models
from yammer import Yammer 
from django.conf import settings
from django.db.models import Max

# Create your models here.

class YUserManager(models.Manager):
    def fetch_yammer_msgs(self):
        cnt = 0
        for yuser in self.exclude(disable_receives=True):
            cnt += yuser.fetch_yammer_msgs()
        return cnt
    
    def delete_user(self, yuserpk):
        Message.objects.filter(from_user__pk=yuserpk).delete()
        Message.objects.filter(to_user__pk=yuserpk).delete()
        SentMessage.objects.filter(yuser__pk=yuserpk).delete()
        self.get(pk=yuserpk).delete()


class YUser(models.Model):
    yammer_user_id=models.BigIntegerField(null=True,default=0)
    max_message_id=models.BigIntegerField(default=0)
    fullname=models.CharField(max_length=100)
    mobile_no=models.CharField(max_length=13)
    disable_receives=models.BooleanField(default=False)
    oauth_token=models.CharField(null=True,max_length=150)
    oauth_token_secret=models.CharField(null=True,max_length=150)
    def __unicode__(self):
        s = "%s (%s)" % (self.fullname, self.mobile_no)
        if self.oauth_token:
            s += ' authorized'
        else:
            s += ' not yet authorized'
        return s

    objects = YUserManager()
    
    def fetch_yammer_msgs(self):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET,
                 oauth_token=self.oauth_token,
                 oauth_token_secret=self.oauth_token_secret)
        all_messages = yammer.messages.following(newer_than=self.max_message_id)
        cnt = self.get_all_messages(all_messages)  
        self.update_max_message_id()
        return cnt

    def yammer_api(self):
        return Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                      consumer_secret=settings.YAMMER_CONSUMER_SECRET,
                      oauth_token=self.oauth_token,
                      oauth_token_secret=self.oauth_token_secret) 

    def post_message(self, content):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET,
                 oauth_token=self.oauth_token,
                 oauth_token_secret=self.oauth_token_secret) 
        yammer.messages.post(content)         

    def get_all_messages(self, all_messages):
        cnt = 0
        for message in all_messages: 
            if self.yammer_user_id != message['sender_id']:
                try:
                    sender=YUser.objects.get(yammer_user_id=message['sender_id'])
                except YUser.DoesNotExist: 
                    sender=None   
                yammer_mes=Message(from_user=sender,to_user=self,message=message['body']['parsed'],thread_id=message['thread_id'],message_id=message['id'])
                yammer_mes.save() 
                cnt += 1
        return cnt
        
    def update_max_message_id(self):
        q =Message.objects.filter(from_user=self).aggregate(Max('message_id'))
        if q.get('message_id__max', 0):
            self.max_message_id = q['message_id__max']
            self.save()   
             
    def to_get_request_token(self,request):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY,
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET                 
                 )
        request.session['request_token'] = yammer.request_token['oauth_token']
        request.session['request_token_secret']=yammer.request_token['oauth_token_secret']
        return yammer

    def to_get_access_token(self,request,oauth_verifier):
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                 consumer_secret=settings.YAMMER_CONSUMER_SECRET, )
        yammer._request_token = dict(request_token=request.session['request_token'] , request_token_secret=request.session['request_token'] )       
        access_token=yammer.get_access_token(oauth_verifier)
        user_id=yammer.users.current()
        self.yammer_user_id=user_id['id'] 
        self.oauth_token=access_token['oauth_token']
        self.oauth_token_secret=access_token['oauth_token_secret']
        self.save()
        yammer = Yammer(consumer_key=settings.YAMMER_CONSUMER_KEY, 
                consumer_secret=settings.YAMMER_CONSUMER_SECRET,                 
                oauth_token=access_token['oauth_token'],
                oauth_token_secret=access_token['oauth_token_secret'])  
        return yammer
      
class MessageManager(models.Manager):   
    def delete_messages(self,date):
        del_messages=Message.objects.filter(sms_sent__lt=date).all() 
        del_messages.delete()
        
               
class Message(models.Model):
    thread_id=models.BigIntegerField(default=0)
    message_id=models.BigIntegerField(default=0)
    from_user=models.ForeignKey(YUser, null=True, blank=True)
    to_user=models.ForeignKey(YUser,related_name='to_user_set', null=True, blank=True)
    message=models.CharField(max_length=140)
    sms_sent=models.DateTimeField(null=True,editable=False)
    unique_together = ("message_id","to_user")
    def __unicode__(self):
        m = self.message
        if self.sms_sent:
            m += " (sms sent)"
        else:
            m += " (sms not sent)"
        return m

    objects = MessageManager()
                
class SentMessageManager(models.Manager):   
    def delete_messages(self,date):
        del_sent_messages=SentMessage.objects.filter(sms_sent__lt=date).all() 
        del_sent_messages.delete()

    def post_pending(self):
        cnt = 0
        for msg in self.filter(sent_time__isnull=True):
            msg.post_message()
            cnt += 1
        return cnt
          
class SentMessage(models.Model): 
    yuser=models.ForeignKey(YUser)
    message=models.CharField(max_length=140)  
    received_time=models.DateTimeField(null=True, blank=True, editable=False)
    sent_time= models.DateTimeField(null=True, blank=True, editable=False) 
    objects =SentMessageManager()
    def save(self):
        if not self.received_time:
            self.received_time = datetime.now()
        return super(SentMessage, self).save()

    def post_message(self):
        self.yuser.post_message(self.message)
        self.sent_time = datetime.now()
        self.save()

    def __unicode__(self):
        m = self.message 
        if self.sent_time:
            m += " (sent)"
        else:
            m += " (not sent)"
        return m

