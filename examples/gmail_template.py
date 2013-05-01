import getpass, os, time

user = raw_input('Username > ')
pw   = getpass.getpass()

import letter

HERE = os.path.dirname(__file__)

class Message(letter.Letter):
    Postie   = letter.GmailPostman(templatedir=HERE, user=user, pw=pw)

    From     = 'bill@example.com'
    To       = 'larry@example.com'
    Subject  = 'My Cool mail'

    Template = 'cool_email'
    Context  = {
        'href': 'http://example.com',
        'link': 'Examples!',
        'time': time.time()
        }



Message.send()
