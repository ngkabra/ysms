from django.conf.urls.defaults import *
from views import get_messages,sms_messages
urlpatterns = patterns('', 
                       url(r'^$', get_messages, name='get_messages'),
                       url(r'^sms_messages', sms_messages, name='sms_messages')
                       )
