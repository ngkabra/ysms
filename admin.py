from models import YUser,Message
from django.contrib import admin

class MessageAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [
        'message_id',
        'from_user',
        'to_user',
        'message',
        ]}),]
    list_display = ('message_id', 'message')
    search_fields = ['to_user']

admin.site.register(Message,MessageAdmin)


class YUserAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': [
        'yammer_user_id',
        'max_message_id',
        'fullname',
        'mobile_no',
        'oauth_token',
        'oauth_token_secret',
        ]}),]
    list_display = ('fullname', 'mobile_no')
    search_fields = ['fullname']
    


admin.site.register(YUser,YUserAdmin)

