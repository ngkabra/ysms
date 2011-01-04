# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from models import YUser,Message,SentMessage
from sms import SmsGupshupSender 
import yammer
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from datetime import timedelta, datetime
import re
from forms import YUserForm
def get_messages(request):
    YUser.objects.get_messages()
    return HttpResponse("Messages Updated")

def sms_messages(request):  
    sms_to_send= Message.objects.all()  
    if sms_to_send:
        for sms in sms_to_send:
            if sms.sms_sent==None:
                s = SmsGupshupSender()   
                s.send(sms.to_user.mobile_no,sms.message)
                sms.sms_sent=datetime.datetime.now()
                sms.save()
        return HttpResponse("Sms Sent")
    return HttpResponse("There is no Sms to Send")

def clear_messages(request):
    now = datetime.now()
    week = timedelta(7)
    date = now - week
    Message.objects.delete_messages(date)
    SentMessage.objects.delete_messages(date)
    return HttpResponse("Sms Deleted")

def receive_sms(request):
    phonecode = request.REQUEST.get('phonecode', '')
    keyword = request.REQUEST.get('keyword', '')
    phoneno = request.REQUEST.get('msisdn', '')
    content = request.REQUEST.get('content', '')
    

    # the first word in a question is the keyword.
    # get rid of that
    content = re.sub('^\w+\s+', '', content)
    
    print 'phoneno=%s, content=%s' % (phoneno, content)
    if phoneno and content:
        if not phoneno.startswith('91'):
            phoneno = '91' + phoneno
        try:
            yuser = YUser.objects.get(mobile_no=phoneno)
            sent_message=SentMessage(yuser=yuser,message=content)
            sent_message.save()
        except YUser.DoesNotExist:
            return HttpResponse('There was some error')
        # send this message to yammer
        # using auth_token of yuser
        yuser.post_message(content)
        sent_message.sent_time=datetime.now()
        sent_message.save() 
        return HttpResponse('Thank you, your message has been posted')

    return HttpResponse('Done')

def add_user(request):
    if request.method == 'POST': # If the form has been submitted...
        yuser=YUser()
        form = YUserForm(request.POST,instance=yuser) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            form.save()
            print yuser.fullname
            yammer=yuser.to_get_request_token(request)
            yammer_redirect=yammer.get_authorize_url()
            return HttpResponseRedirect('%s' % yammer_redirect) # Redirect after POST
    else:
        form = YUserForm() # An unbound form
    return render_to_response('ysms/add_user.html', {
        'form': form,
    })

def yammer_callback(request):
   yuser=YUser()
   yammer=yuser.to_get_acces_token(request)    
 

