# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from models import YUser,Message,SentMessage,Group,Statistics,Company
from sms import SmsGupshupSender 
import yammer
from django.http import HttpResponseRedirect, HttpResponse
from datetime import *
import re
from forms import YUserForm
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404


sms_commands =[(re.compile(r'samvad staff (.*$)'), 'staff'),
               (re.compile(r'samvad bakwaas movies (.*$)'), 'bakwaas movies'),
               ]

@login_required
def index(request):
    try:
       company=Company.objects.get_company(request.user)
       yusers = YUser.objects.filter(company=company)
       post_pending = SentMessage.objects.filter(sent_time__isnull=True).count()
       sms_pending = Message.objects.filter(sms_sent__isnull=True).count()
       return render_to_response('ysms/index.html', 
                                       dict(yusers=yusers,
                                       post_pending=post_pending,
                                       sms_pending=sms_pending),
                                  context_instance=RequestContext(request))
    except Company.DoesNotExist:
       raise Http404    
        

def fetch_yammer_msgs(request):
    cnt = YUser.objects.fetch_yammer_msgs()
    return HttpResponse("%d Messages Fetched" % cnt)

def send_sms_msgs(request):  
    sms_to_send = Message.objects.all()  
    if sms_to_send:
        cnt = Message.objects.to_send_sms()  
        if cnt == 0:
            return HttpResponse("No new sms to send")
        return HttpResponse("%d Sms Sent" % cnt)
    return HttpResponse("There is no sms to Send")

def clear_msgs():
    '''Clear Message and SentMessage instances older than a week

    We have separated this out from the clear_messages view because
    we want to be able to call this from a management command
    '''
    now = datetime.now()
    week = timedelta(7)
    date = now - week
    Message.objects.delete_messages(date)
    SentMessage.objects.delete_messages(date)

def clear_messages(request):
    clear_msgs()
    return HttpResponse("Messages older than one week have been deleted")

def receive_sms(request):
    phoneno = request.REQUEST.get('msisdn', '')
    content = request.REQUEST.get('content', '')
    # the first word in a question is the keyword.
    # get rid of that
    content=re.sub("\s+" , " ", content.lower().strip())
    for (cmd_re, group_name) in sms_commands:
        sms = cmd_re.match(content)
        print group_name,content,sms
        try:
            if sms:  
                content = sms.group(1)
                print content   
                group = Group.objects.get(name=group_name)
                print group.company.name
        except Group.DoesNotExist:
            pass
        
    if phoneno and content:
        if not phoneno.startswith('91'):
            phoneno = '91' + phoneno
        try:
            yuser = YUser.objects.get(mobile_no=phoneno,company=group.company)
            sent_message=SentMessage(yuser=yuser,message=content,group=group)
            sent_message.save()
            Statistics.objects.update_sms_received(yuser.company) 
        
        except YUser.DoesNotExist:
            return HttpResponse('There was some error')
        # send this message to yammer
        # using auth_token of yuser
        sent_message.post_message(content)
        return HttpResponse('Thank you, your message has been posted')
    return HttpResponse('Done')

def post_msgs_to_yammer(request):
    cnt = SentMessage.objects.post_pending()
    return HttpResponse('%d msgs posted' % cnt)

@login_required
@csrf_protect
def add_user(request):
     if request.method == 'POST':
         form = YUserForm(request.POST) 
         if form.is_valid(): 
             yuser = form.save()
             company = Company.objects.get_company(request.user)
             yuser.company=company
             yuser.save()
             yammer = yuser.yammer_api()
             request.session['yuser_pk'] = yuser.pk
             request.session['request_token'] = yammer.request_token['oauth_token']
             request.session['request_token_secret'] = yammer.request_token['oauth_token_secret']
             yammer_redirect = yammer.get_authorize_url()
             return HttpResponseRedirect(yammer_redirect)
     else:
        form = YUserForm() 
     return render_to_response('ysms/add_user.html', {
        'form': form,
        }, context_instance=RequestContext(request))

@login_required
def authorize_user(request, yuserpk):
    yuser = get_object_or_404(YUser, pk=yuserpk)
    try:
        company = Company.objects.get_company(request.user)
        if yuser.company.name == company.name: 
            yuser.unauthorize()
            yammer = yuser.yammer_api()
            request.session['yuser_pk'] = yuser.pk
            request.session['request_token'] = yammer.request_token['oauth_token']
            request.session['request_token_secret'] = yammer.request_token['oauth_token_secret']
            return HttpResponseRedirect(yammer.get_authorize_url())
        else:
            raise Http404
    except Company.DoesNotExist:
        raise Http404    
            
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
        yammer = yuser.yammer_api()
        yammer._request_token = dict(oauth_token=req_token , oauth_token_secret=req_secret)       
        access_token = yammer.get_access_token(oauth_verifier)
        yuser.oauth_token = access_token['oauth_token']
        yuser.oauth_token_secret = access_token['oauth_token_secret']
        yuser.save()
        # Unfortunately, yammer.py does not update itself with the
        # access_token, so we need to recreate it
        yammer = yuser.yammer_api()
        user_id = yammer.users.current()
        yuser.yammer_user_id=user_id['id'] 
        yuser.save()
        return HttpResponseRedirect(reverse('ysms-index'))
    return render_to_response('ysms/yammer_callback.html', context_instance=RequestContext(request))

@login_required
def delete_user(request, yuserpk):
    yuser = get_object_or_404(YUser, pk=yuserpk)
    try:
        company = Company.objects.get_company(request.user)
        if yuser.company.name == company.name: 
            YUser.objects.delete_user(yuserpk)
            return HttpResponseRedirect(reverse('ysms-index'))
        else:
            raise Http404
    except Company.DoesNotExist:
        raise Http404  