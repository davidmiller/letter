"""
Example of sending a message via twitter
"""
from letter.social import TwitterPostie, TwitterAccount, Tweet

consumer_key=""
consumer_secret=""

access_token=""
access_token_secret=""

accounts = {
    'sru_dev': TwitterAccount(access_token, access_token_secret)
    }


postie = TwitterPostie(consumer_key, consumer_secret, accounts)

class Message(Tweet):
    Postie = postie

    From = 'sru_dev'
    To   = 'thatdavidmiller'
    Body = 'Hello from Letter!'

Message.send()
