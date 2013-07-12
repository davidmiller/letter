import getpass, os

fromaddr = raw_input('from > ')
to  = raw_input('to > ')
reply_to  = raw_input('Replyto > ')

import letter

class Message(letter.Letter):
    Postie = letter.Postman() # Unauthorized SMTP, localhost:25

    From    = fromaddr
    To      = to
    ReplyTo = reply_to
    Subject = "I don't want to hear about it."
    Body    = 'Hai, this is an Email! If you just hit reply in a sane mail program, it will go to {0}'.format(reply_to)

Message.send()
