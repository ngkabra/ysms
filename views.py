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
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.core.urlresolvers import reverse

def index(request):
    yusers = YUser.objects.all()
    return render_to_response('ysms/index.html', 
                              dict(yusers=yusers),
                              context_instance=RequestContext(request))


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

@csrf_protect
def add_user(request):
    if request.method == 'POST':
        form = YUserForm(request.POST) 
        if form.is_valid(): 
            yuser = form.save()
            request.session['yuser_pk'] = yuser.pk
            yammer=yuser.to_get_request_token(request)
            yammer_redirect=yammer.get_authorize_url()
            return HttpResponseRedirect(yammer_redirect)
    else:
        form = YUserForm() 
    return render_to_response('ysms/add_user.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def authorize_user(request, yuserpk):
    yuser = get_object_or_404(YUser, pk=yuserpk)
    request.session['yuser_pk'] = yuser.pk
    yammer=yuser.to_get_request_token(request)
    return HttpResponseRedirect(yammer.get_authorize_url())

@csrf_protect
def yammer_callback(request):
    yuserpk = request.session.get('yuser_pk')
    req_token = request.session.get('request_token')
    req_secret = request.session.get('request_token_secret')
    if not yuserpk or not req_token or not req_secret:
        return HttpResponse('Error')
    if request.method == 'POST':
        oauth_verifier=request.POST['oauth_verifier']
        yuser = YUser.objects.get(pk=yuserpk)
        yammer=yuser.to_get_access_token(request,oauth_verifier)         
        return HttpResponseRedirect(reverse('ysms-index'))
    return render_to_response('ysms/yammer_callback.html', context_instance=RequestContext(request))
    

def delete_user(request, yuserpk):
    YUser.objects.delete_user(yuserpk)
    return HttpResponseRedirect(reverse('ysms-index'))
