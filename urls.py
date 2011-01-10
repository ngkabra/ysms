from django.conf.urls.defaults import *
from views import index,get_messages,sms_messages,receive_sms,clear_messages,add_user,authorize_user,yammer_callback
urlpatterns = patterns('', 
                       url(r'^$', index, name='ysms-index'),
                       url(r'^get_messages$', get_messages, name='get_messages'),
                       url(r'^sms_messages', sms_messages, name='sms_messages'),
                       url(r'^receive_sms', receive_sms, name='receive_sms'),
                       url(r'^clear_messages', clear_messages, name='clear_messages'),
                       url(r'^add_user', add_user, name='add_user'),
                       url(r'^authorize_user/(?P<yuserpk>\d+)/', authorize_user, name='authorize_user'),
                       url(r'^yammer_callback', yammer_callback, name='yammer_callback'),
                       url(r'^delete_user/(?P<yuserpk>\d+)/', delete_user, name='delete_user'),
                       )
