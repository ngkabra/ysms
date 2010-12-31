from models import YUser
from django.contrib import admin


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

