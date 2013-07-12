"""
Get a twitter access token/secret for our account!
"""
import time
import webbrowser

import tweepy

consumer_key=""
consumer_secret=""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
redirect_url = auth.get_authorization_url()

webbrowser.open(redirect_url)
time.sleep(0.5)
print 'Authorize in your browser, then '

verifier = raw_input('enter your pin: ')
access_token, access_token_secret = [x.split('=')[1] for
                                     x in str(auth.get_access_token(verifier)).split('&')]

print 'Access Token:', access_token
print 'Access Token Secret:', access_token_secret
