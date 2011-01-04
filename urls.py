from django.conf.urls.defaults import *
from views import get_messages,sms_messages,receive_sms,clear_messages,add_user,yammer_callback
urlpatterns = patterns('', 
                       url(r'^$', get_messages, name='get_messages'),
                       url(r'^sms_messages', sms_messages, name='sms_messages'),
                       url(r'^receive_sms', receive_sms, name='receive_sms'),
                       url(r'^clear_messages', clear_messages, name='clear_messages'),
                       url(r'^add_user', add_user, name='add_user'),
                       url(r'^yammer_callback', yammer_callback, name='yammer_callback'),
 
                       )
