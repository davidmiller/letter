import getpass

import letter

user = raw_input('Username > ')
pw   = getpass.getpass()

class Message(letter.Letter):
    Postie   = letter.GmailPostman(user=user, pw=pw)

    From     = user
    To       = 'david@deadpansincerity.com'
    Subject  = 'My Cool mail via Gmail'
    Body     = 'Hai larry'

Message.send()
