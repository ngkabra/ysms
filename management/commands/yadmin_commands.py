from django.core.management.base import BaseCommand,CommandError
from smsyammer.ysms.models import YUser,Message,SentMessage 
from optparse import OptionParser, make_option
from datetime import *

option_list = BaseCommand.option_list + (make_option('--ysmscron',
            dest='ysms_cron'), make_option('--fetchmsgs', action='store_true',dest='fetch_msgs'),
            make_option('--sms_msgs', dest='sms_msgs'),make_option('--post_msgs', dest='post_msgs'),make_option('--clean_msgs', dest='clean_msgs'))

class Command(BaseCommand):
     def handle(self,**options):
         command=Command()
         if options['ysms_cron']:
            command.ysms_cron() 
         if options['fetch_msgs']:
            command.fetch_msgs() 
         if options['sms_msgs']:
            command.sms_msgs() 
         if options['post_msgs']:
            command.post_msgs() 
         if options['clean_msgs']:
            command.clean_msgs() 
  
     def ysms_cron(self):
         self.fetch_msgs()
         self.sms_msgs()
         self. post_msgs() 
         self.clean_msgs()
             
     def fetch_msgs(self):
         cnt = YUser.objects.fetch_yammer_msgs()
         print "%d Messages Fetched" % cnt
 
     def sms_msgs(self):
         sms_to_send = Message.objects.all()  
         if sms_to_send:
             cnt=Message.objects.to_send_sms()  
             if cnt==0:
                 print"No new sms to send"
             print"%d Sms Sent" % cnt
         print "There is no sms to Send"

     def post_msgs(self):
         cnt = SentMessage.objects.post_pending()
         print '%d msgs posted' % cnt
        
     def clean_msgs(self):
         now = datetime.now()
         week = timedelta(7)
         date = now - week
         Message.objects.delete_messages(date)
         SentMessage.objects.delete_messages(date)
         print "Sms Deleted"


 