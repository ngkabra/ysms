from django.core.management.base import BaseCommand,CommandError
from smsyammer.ysms.models import YUser,Message,SentMessage 
from optparse import OptionParser, make_option
from datetime import *


class Command(BaseCommand):
     def handle(self,**options):
         sms_to_send = Message.objects.all()  
         if sms_to_send:
             cnt=Message.objects.to_send_sms()  
             if cnt==0:
                 print"No new sms to send"
             print"%d Sms Sent" % cnt
         print "There is no sms to Send"