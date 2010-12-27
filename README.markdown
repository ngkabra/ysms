This is a simple sms-to-yammer gateway (for India). Basically it allows users to be connected to their yammer accounts (for getting status updates, as well as for posting updates) using plain sms text messages.

It is a django app that does the following:

- It allows the administrator to create user accounts with an Indian mobile phone number, and yammer user credentials
- Periodically it contacts yammer on behalf of each user (using the oauth token) and downloads any new messages for that user. These messages are forwarded to the mobile phone of that user. Currently the SMS Gupshup enterprise sms service is used for this. It should be easy to extend this to other services.
- Also, if your SMS Gupshup enterprise service is appropriately configured to forward all sms messages with a particular keyword to the 'receive_sms' url of this app, then it automatically posts this message to yammer on the behalf of the correct user. The correct yammer user is figured out based on the mobile phone number of the sender.

### How to use

This is intended to be used as a django app that can be added to any existing django project.

- Clone using git, and then drop the whole thing as an app in your django project. Update your INSTALLED_APPS and urls.py appropriately.
- Sign up for a yammer developer account and get a consumer key and consumer seccret from them and add the following to your settings.py
        YAMMER_CONSUMER_KEY='xxx'
        YAMMER_CONSUMER_SECRET='yyy'
- Get an SMS Gupshup Enterprise Account (you'll need to pay them for this!), and add the following to your settings.py
        SMS_GATEWAY_USERNAME='xxx'
        SMS_GATEWAY_PASSWORD='yyy'
- Create a new keyword on SMS Gupshup enterprise account, and point the url to:
        http://yourdomain.com/<path-to-this-app>/sms_receive/
    This will ensure that users can send an sms to post to their yammer account
- Set up a cron job to visit:
        http://yourdomain.com/<path-to-this-app>/get_messages/
    This ensures that all new messages on yammer are sent to the users via sms.
- Use the django admin interface to create a YUser account for each user you want to support. You'll need to add their mobile number, and oauth token and secret.

### ToDo

This app can be improved greatly. Here are some suggested features:

- Make it easier to add other sms-gateway services.
- Generalize it for use in countries other than India

CREDITS:

This app has been built by Samrudha Kulkarni, under the guidance of Navin Kabra.

