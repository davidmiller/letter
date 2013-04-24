import os

import letter

user = os.environ.get('USER', 'not a real user dummy')
pw   = os.environ.get('PASS', 'not a real pass dummy')

class Message(letter.Letter):
    Postie   = letter.GmailPostman('.', user=user, pw=pw)

    From     = 'bill@example.com'
    To       = 'larry@example.com'
    Subject  = 'My Cool mail'

    Template = 'cool_email'
    Context  = {
        'href': 'http://example.com',
        'link': 'Examples!',
        }

Message.send()
