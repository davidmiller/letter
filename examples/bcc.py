import getpass, os

to  = raw_input('Send To > ')
cc  = raw_input('CC > ')
bcc = raw_input('BCC > ')

import letter

class Message(letter.Letter):
    Postie = letter.Postman() # Unauthorized SMTP, localhost:25

    From    = 'larry@example.com'
    To      = to
    Cc      = cc
    Bcc     = bcc
    Subject = 'Emailin with Carbon'
    Body    = 'Hai, this is an Email! It went to more people than you know via "BCC"'

Message.send()
