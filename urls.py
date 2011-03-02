from django.conf.urls.defaults import *
from django.contrib.auth.views import login,logout
urlpatterns = patterns('ysms.views', 
                       url(r'^$', 'index', name='ysms-index'),
                       url(r'^login/', login, {'template_name': 'ysms/login.html/'},name='ysms-login'),
                       url(r'^logout/', logout, {'next_page':'/ysms/login/'},name='ysms-logout'),
                       url(r'^fetch-yammer-msgs/', 'fetch_yammer_msgs', name='ysms-fetch-yammer-msgs'),
                       url(r'^send-sms-msgs/', 'send_sms_msgs', name='ysms-send-sms-msgs'),
                       url(r'^receive_sms/', 'receive_sms', name='ysms-receive-sms'),
                       url(r'^post-msgs-to-yammer/', 'post_msgs_to_yammer', name='ysms-post-msgs-to-yammer'),
                       url(r'^clear-messages/', 'clear_messages', name='ysms-clear-messages'),
                       url(r'^add-user/', 'add_user', name='ysms-add-user'),
                       url(r'^authorize-user/(?P<yuserpk>\d+)/', 'authorize_user', name='ysms-authorize-user'),
                       url(r'^yammer_callback/', 'yammer_callback', name='ysms-yammer-callback'),
                       url(r'^delete-user/(?P<yuserpk>\d+)/', 'delete_user', name='ysms-delete-user'),
                       )

