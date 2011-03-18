from datetime import *
from sms import SmsGupshupSender
from django.db import models, IntegrityError
from yammer import Yammer
from django.conf import settings
from django.contrib.auth.models import User
from collections import defaultdict

# Create your models here.

class CompanyManager(models.Manager):
    def get_company(self,user):
        company=self.get(admins=user)
        return company
    
    
class Company(models.Model):

    name = models.CharField(max_length=140)
    admins = models.ManyToManyField(User, blank=True)
    gupshup_user = models.CharField(max_length=140)
    gupshup_password = models.CharField(max_length=140)
    app_consumer_key=models.CharField(max_length=140)
    app_consumer_secret=models.CharField(max_length=140)
    objects=CompanyManager()
    def __unicode__(self):
        return '%s%s%s' % (self.gupshup_user, self.name,
                           self.gupshup_password)


class Group(models.Model):

    group_id = models.IntegerField(null=True)
    company =  models.ForeignKey(Company,blank=True,null=True)
    keyword = models.CharField(max_length=140)
    name = models.CharField(max_length=140)

    def __unicode__(self):
        return '%s%s' % (self.keyword, self.name)


class YUserManager(models.Manager):

    def fetch_yammer_msgs(self):
        cnt=0
        for yuser in self.exclude(disable_receives=True):
            cnt = yuser.fetch_yammer_msgs(cnt)
        return cnt

    def delete_user(self, yuserpk):
        Message.objects.filter(from_user__pk=yuserpk).delete()
        Message.objects.filter(to_user__pk=yuserpk).delete()
        SentMessage.objects.filter(yuser__pk=yuserpk).delete()
        self.get(pk=yuserpk).delete()


class YUser(models.Model):

    yammer_user_id = models.BigIntegerField(null=True, default=0)
    max_message_id = models.BigIntegerField(default=0)
    company = models.ForeignKey(Company, null=True, blank=True)
    fullname = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=13)
    disable_receives = models.BooleanField(default=False)
    oauth_token = models.CharField(null=True, max_length=150)
    oauth_token_secret = models.CharField(null=True, max_length=150)

    def __unicode__(self):
        s = '%s (%s)' % (self.fullname, self.mobile_no)
        if self.oauth_token:
            s += ' authorized'
        else:
            s += ' not yet authorized'
        return s

    objects = YUserManager()

    def yammer_api(self):
        return Yammer(consumer_key=self.company.app_consumer_key,
                      consumer_secret=self.company.app_consumer_secret,
                      oauth_token=self.oauth_token,
                      oauth_token_secret=self.oauth_token_secret)

    def unauthorize(self):
        self.oauth_token = None
        self.oauth_token_secret = None
        self.save()

    def fetch_yammer_msgs(self,cnt):
        yammer = self.yammer_api()
        all_messages = \
            yammer.messages.following(newer_than=self.max_message_id)
        cnt = self.get_all_messages(all_messages,cnt)
        return cnt

    def post_message(self, content, group_id):
        self.yammer_api().messages.post(content, group_id)    

    def get_all_messages(self,all_messages,cnt):
        for message in all_messages:
            msg_id = message['id']
            if self.max_message_id <= msg_id:
                self.max_message_id = msg_id
            if self.yammer_user_id != message['sender_id']:
                try:
                    sender = \
                        YUser.objects.get(yammer_user_id=message['sender_id'
                            ])
                    yammer_mes = Message(from_user=sender,
                            to_user=self, message=message['body'
                            ]['parsed'], thread_id=message['thread_id'
                            ], message_id=msg_id)
                    try:
                        yammer_mes.save()
                        if message.get('group_id', None):
                            try:
                                group = \
                                    Group.objects.get(group_id=message['group_id'
                                        ])
                                yammer_mes.group = group
                                yammer_mes.save()
                            except Group.DoesNotExist:
                                pass
                        cnt+=1
                    except IntegrityError:
                        pass  # probably a unique-together violation
                except YUser.DoesNotExist:

                    pass

                        # Error?!
                        # Probably a user that has been added to
                        # yammer but not added to this gateway.
                        # for now, ignore...

        self.save()
        return cnt


class MessageManager(models.Manager):

    def delete_messages(self, date):
        del_messages = Message.objects.filter(sms_sent__lt=date).all()
        del_messages.delete()

    def to_send_sms(self):
        count = 0
        statistics = defaultdict(int)
        for sms in self.all():
            if sms.sms_sent == None:
                ''''s = SmsGupshupSender(username=sms.to_user.company.gupshup_user,password=sms.to_user.company.gupshup_password)
                s.send(sms.to_user.mobile_no, sms.message)'''
                sms.sms_sent = datetime.now()
                sms.save()
                count += 1
                statistics[sms.to_user.company] += 1
        for (company, cnt) in statistics.iteritems():
            Statistics.objects.update_sms_sent(company, cnt)
        return count


class Message(models.Model):

    thread_id = models.BigIntegerField(default=0)
    message_id = models.BigIntegerField(default=0)
    from_user = models.ForeignKey(YUser, null=True, blank=True)
    to_user = models.ForeignKey(YUser, related_name='to_user_set',
                                blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    message = models.CharField(max_length=140)
    sms_sent = models.DateTimeField(null=True, editable=False)


    class Meta:

        unique_together = ('message_id', 'to_user')


    def __unicode__(self):
        m = '%s ::from=%s, to=%s' % (self.message,
                self.from_user.fullname, self.to_user.fullname)
        if self.sms_sent:
            m += ' (sms sent)'
        else:
            m += ' (sms not sent)'
        return m

    objects = MessageManager()


class SentMessageManager(models.Manager):

    def delete_messages(self, date):
        del_sent_messages = \
            SentMessage.objects.filter(sent_time__lt=date).all()
        del_sent_messages.delete()

    def post_pending(self):
        cnt = 0
        for msg in self.filter(sent_time__isnull=True):
            msg.post_message()
            cnt += 1
        return cnt


class SentMessage(models.Model):

    yuser = models.ForeignKey(YUser)
    group = models.ForeignKey(Group, blank=True)
    message = models.CharField(max_length=140)
    received_time = models.DateTimeField(null=True, blank=True,
            editable=False)
    sent_time = models.DateTimeField(null=True, blank=True,
            editable=False)
    objects = SentMessageManager()

    def save(self):
        if not self.received_time:
            self.received_time = datetime.now()
        return super(SentMessage, self).save()

    def post_message(self, message):
        if  self.group.group_id == 0:
            self.yuser.post_message(message, None )
        else:    
            self.yuser.post_message(message, self.group.group_id)   
        self.sent_time = datetime.now()
        self.save()

    def __unicode__(self):
        m = '%s ::from=%s' % (self.message, self.yuser.fullname)
        if self.sent_time:
            m += ' (sent)'
        else:
            m += ' (not sent)'
        return m


class StatisticsManager(models.Manager):

    def update_sms_received(self,company):
        try:
            stats = Statistics.objects.get(date=date.today(),company=company)
        except Statistics.DoesNotExist:
            stats = Statistics()
            stats.company = company
            stats.date = date.today()
        stats.sms_received = stats.sms_received + 1
        stats.save()    

    def update_sms_sent(self,company,cnt):
        try:
            stats = Statistics.objects.get(date=date.today(),company=company)
        except Statistics.DoesNotExist:
            stats = Statistics()
            stats.company = company
            stats.date = date.today()
        stats.sms_sent = stats.sms_sent + cnt
        stats.save()    

class Statistics(models.Model):

    company = models.ForeignKey(Company, blank=True)
    date = models.DateField(blank=True, editable=False)
    sms_sent = models.IntegerField(default=0)
    sms_received = models.IntegerField(default=0)
    objects = StatisticsManager()


