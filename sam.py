from yammer import Yammer
yammer = Yammer(consumer_key='q9IF4stjqCsIGxYNtM8hg',
                consumer_secret='S91cacwu1hqdeDbFJIZwDBS12DkCuzkaxztUqJvb8w'
                )
print yammer.get_authorize_url()

oauth_verifier = raw_input("After authorizing, enter the OAuth "
                               "verifier (four characters): ")
access_token=yammer.get_access_token(oauth_verifier)
print access_token

yammer = Yammer(consumer_key='q9IF4stjqCsIGxYNtM8hg',
                consumer_secret='S91cacwu1hqdeDbFJIZwDBS12DkCuzkaxztUqJvb8w',
                oauth_token=access_token['oauth_token'],
                oauth_token_secret=access_token['oauth_token_secret'])

all_messages=yammer.messages.received()
all_users= yammer.users.all()
#yammer.messages.post("I am sam")
for user in all_users:
        print user['contact']['phone_numbers'][0]['number']     
        print user['id']
        print user['full_name']
for message in all_messages:
         
         print message['id']
         print message
