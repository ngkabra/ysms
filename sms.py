import urllib
import urllib2
from django.conf import settings
class Error(Exception):
    pass

class GatewayNotAvailableError(Error): 
    pass

class SmsGupshupError(Error):
    '''An sms error with two attributes - errorcode, errormessage'''
    def __init__(self, errorcode, errormessage):
        self.errorcode = errorcode
        self.errormessage = errormessage

    def __unicode__(self):
        return '[%s] %s' % (self.errorcode, self.errormessage)

class SmsGupshupFailure(SmsGupshupError):
    '''same as SmsGupshupError, but it's a temporary failure
    '''
    pass


class SmsGupshupSender():
    # SMS Gupshup configuration
    username=settings.SMS_GATEWAY_USERNAME
    password=settings.SMS_GATEWAY_PASSWORD
    version = '1.0'
    url='http://enterprise.smsgupshup.com/GatewayAPI/rest'

    def __init__(self,
                 username=None,
                 password=None):
        if username: self.username = username 
        if password: self.password = password

    def send(self, number, message):
        '''
        Sends message to number.

        Don't use this method directly. 
        Instead, use the 'send' method which in turn calls this

        raises sms.Error(errorcode, errormessage) 
        >>> import sms
        >>> s = sms.Sender.defaultSender()
        >>> msg = 'Using you as a guinea pig for testing BharatHealth sms service. Reply "ok" to 98220 20096 (Navin) if you receive this. thanks -Navin Kabra/Amit Paranjape'
        >>> s.send('9822020096', msg)
        >>>
        '''
        params = {'method': 'sendMessage',
                  'send_to': number,
                  'msg': message,
                  'userid': self.username,
                  'password': self.password,}
        data = urllib.urlencode(params)
        the_url = self.url + '?' + data
        try:
            response = urllib2.urlopen(the_url)
        except :
            raise GatewayNotAvailableError()
        r = [x.strip() for x in response.read().split('|')]
        if r[0] != 'success':
            if len(r) == 3:
                raise SmsGupshupError(r[1], r[2])
            else:
                raise SmsGupshupFailure(r[2], r[3])
