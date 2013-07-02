
import letter

toaddr = raw_input('To address > ')
attachment = raw_input('Path to attachment > ')

class Message(letter.Letter):
    Postie = letter.Postman() # Unauthorized SMTP, localhost:25

    From       = 'letter@example.com'
    To         = toaddr
    Subject    = 'Easy Emails'
    Body       = 'Hai Bill, this is an Email!'
    Attach     = attachment

Message.send()
