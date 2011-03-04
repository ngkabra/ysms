from django.core.management.base import BaseCommand,CommandError
from smsyammer.ysms.models import YUser,Message,SentMessage 
from optparse import OptionParser, make_option



class Command(BaseCommand):
     def handle(self,**options):
         cnt = YUser.objects.fetch_yammer_msgs()
         print "%d Messages Fetched" % cnt