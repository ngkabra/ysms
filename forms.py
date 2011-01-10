from django.forms import ModelForm
from models import YUser
class YUserForm(ModelForm):
    class Meta:
        model = YUser
        fields = ('fullname', 'mobile_no', 'disable_receives')
  
