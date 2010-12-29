# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from models import YUser,Message
from sms import SmsGupshupSender 
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from datetime import timedelta, datetime
import re

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

def clear_messages(request):
    now = datetime.now()
    week = timedelta(7)
    date = now - week
    Message.objects.delete_messages(date)
    return HttpResponse("Sms Deleted")

def receive_sms(request):
    phonecode = request.REQUEST.get('phonecode', '')
    keyword = request.REQUEST.get('keyword', '')
    phoneno = request.REQUEST.get('msisdn', '')
    content = request.REQUEST.get('content', '')

    # the first word in a question is the keyword.
    # get rid of that
    #question = re.sub('^\w+\s+', '', question)
    
    print 'phoneno=%s, content=%s' % (phoneno, content)
    if phoneno and content:
        if not phoneno.startswith('91'):
            phoneno = '91' + phoneno
        try:
            yuser = YUser.objects.get(mobile_no=phoneno)
        except YUser.DoesNotExist:
            return HttpResponse('There was some error')
        # send this message to yammer
        # using auth_token of yuser
        yuser.post_message(content)
        return HttpResponse('Thank you, your message has been posted')

    return HttpResponse('Done')


