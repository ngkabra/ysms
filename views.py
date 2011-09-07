# Create your views here.
import re
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

from models import YUser, Message, SentMessage, Group, Statistics, Company
from forms import YUserForm

sms_commands =[(re.compile(r'samvad staff (.*$)'), 'staff'),
               (re.compile(r'samvad bakwaas movies (.*$)'), 'bakwaas movies'),
               (re.compile(r'samvad smriti (.*$)'), 'smriti'),
               (re.compile(r'samvad wogma (.*$)'), 'wogma'),
               ]

@login_required
def index(request):
    '''Dashboard for a company'''
    try:
       company=Company.objects.get_company(request.user)
    except Company.DoesNotExist:
       raise Http404    

    yusers = YUser.objects.filter(company=company)
    post_pending = SentMessage.objects.filter(sent_time__isnull=True).count()
    sms_pending = Message.objects.filter(sms_sent__isnull=True).count()
    return render_to_response('ysms/index.html', 
                              dict(yusers=yusers,
                                   post_pending=post_pending,
                                   sms_pending=sms_pending),
                              context_instance=RequestContext(request))

def fetch_yammer_msgs(request):
    '''Fetch all messages for this user on yammer'''
    cnt = YUser.objects.fetch_yammer_msgs()
    return HttpResponse("%d Messages Fetched" % cnt)

def send_sms_msgs(request):  
    '''Send out sms based on messages fetched from yammer'''
    cnt = Message.objects.send_sms_msgs()  
    if cnt == 0:
        return HttpResponse("No new sms to send")
    return HttpResponse("%d Sms Sent" % cnt)

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
    '''See doc for clear_msgs'''
    clear_msgs()
    return HttpResponse("Messages older than one week have been deleted")

def receive_sms(request):
    '''Receive an sms from user and send it to yammer'''
    phoneno = request.REQUEST.get('msisdn', '')
    content = request.REQUEST.get('content', '')
    # the first word is the keyword. get rid of that
    content = re.sub("\s+" , " ", content.lower().strip())

    for (cmd_re, group_name) in sms_commands:
        '''If content matches one of the know commands
        Then adjust the content and group accordingly'''
        m = cmd_re.match(content)
        if m:  
            try:
                content = m.group(1)
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                pass

    if not phoneno or not content:
        return HttpResponse('Did nothing. No phone/content.')

    if not phoneno.startswith('91'):
        phoneno = '91' + phoneno

    try:
        yuser = YUser.objects.get(mobile_no=phoneno, company=group.company)
    except YUser.DoesNotExist:
        return HttpResponse('There was some error')

    sent_message=SentMessage(yuser=yuser, message=content, group=group)
    sent_message.save()
    Statistics.objects.update_sms_received(yuser.company) 
            
    # send this message to yammer using auth_token of yuser
    sent_message.post_message(content)
    return HttpResponse('Thank you, your message has been posted')

def post_msgs_to_yammer(request):
    '''Post pending messages to yammer'''
    cnt = SentMessage.objects.post_pending()
    return HttpResponse('%d msgs posted' % cnt)

def yammer_authorization_redirect(request, yuser):
    yammer = yuser.yammer_api()
    request.session['yuser_pk'] = yuser.pk
    request.session['request_token'] = \
        yammer.request_token['oauth_token']
    request.session['request_token_secret'] = \
        yammer.request_token['oauth_token_secret']
    return HttpResponseRedirect(yammer.get_authorize_url())

@login_required
@csrf_protect
def add_user(request):
    if request.method == 'POST':
        form = YUserForm(request.POST) 
        if form.is_valid(): 
            yuser = form.save()

            '''Update the company based on company of logged in user'''
            company = Company.objects.get_company(request.user)
            yuser.company = company
            yuser.save()

            '''Redirect user to yammer for yammer authentication'''
            return yammer_authorization_redirect(request, yuser)
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
    except Company.DoesNotExist:
        raise Http404    

    if yuser.company.name == company.name: 
        yuser.unauthorize()
        return yammer_authorization_redirect(request, yuser)
    else:
        raise Http404
            
@csrf_protect
def yammer_callback(request):
    '''This callback comes from yammer after the authorization redirect'''
    yuserpk = request.session.get('yuser_pk')
    req_token = request.session.get('request_token')
    req_secret = request.session.get('request_token_secret')
    if not yuserpk or not req_token or not req_secret:
        return HttpResponse('Error')

    if not request.method == 'POST':
        '''This should never happen'''
        return render_to_response('ysms/yammer_callback.html', {},
                                  context_instance=RequestContext(request))

    oauth_verifier=request.POST['oauth_verifier']
    yuser = YUser.objects.get(pk=yuserpk)
    yammer = yuser.yammer_api()
    yammer._request_token = dict(oauth_token=req_token, 
                                 oauth_token_secret=req_secret)       
    
    access_token = yammer.get_access_token(oauth_verifier)
    yuser.oauth_token = access_token['oauth_token']
    yuser.oauth_token_secret = access_token['oauth_token_secret']
    yuser.save()
    
    # Unfortunately, yammer.py does not update itself with the
    # access_token, so we need to recreate it
    yammer = yuser.yammer_api()
    yuser.yammer_user_id = yammer.users.current()['id'] 
    yuser.save()
    
    return HttpResponseRedirect(reverse('ysms-index'))

@login_required
def delete_user(request, yuserpk):
    yuser = get_object_or_404(YUser, pk=yuserpk)
    try:
        company = Company.objects.get_company(request.user)
    except Company.DoesNotExist:
        raise Http404  

    if yuser.company.name != company.name: 
        raise Http404
    
    YUser.objects.delete_user(yuserpk)
    return HttpResponseRedirect(reverse('ysms-index'))
