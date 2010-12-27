# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from models import YUser,Message
from sms import SmsGupshupSender 
from django.http import HttpResponseRedirect, HttpResponse
import datetime

def get_messages(request):
    YUser.objects.authenticate_users()
    return HttpResponse("Messages Updated")

def sms_messages(request):  
    sms_to_sent= Message.objects.all()  
    for sms in sms_to_sent:
        if sms.sms_sent==None:
            s = SmsGupshupSender()   
            s.send(9922900383,sms.message)
            sms.sms_sent=datetime.datetime.now()
            sms.save()
            return HttpResponse("Sms Sent")

def receive_sms(request):
    return HttpResponse('Done')


