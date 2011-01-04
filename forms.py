from django import forms
class YUserForm(forms.Form):
    fullname= forms.CharField(max_length=100)
    Mobile_no=forms.CharField(max_length=13)
  
