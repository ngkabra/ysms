import re

from django import forms
from models import YUser
class YUserForm(froms.ModelForm):
    def clean_mobile_no(self):
        mno = self.cleaned_data['mobile_no']
        mno = mno.replace(' ', '') # remove spaces
        if re.match('^\d{10}$', mno):
            return '91'+mno
        elif re.match('^91\d{10}$', mno):
            return mno
        else:
            raise forms.ValidationError('Mobile number must be 10 digits without any other characters')

    class Meta:
        model = YUser
        fields = ('fullname', 'mobile_no', 'disable_receives')
 
