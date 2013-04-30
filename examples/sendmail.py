
import letter

class Message(letter.Letter):
    Postie = letter.Postman()

    From    = 'larry@example.com'
    To      = 'bill@example.com'
    Subject = 'Easy Emails'
    Body    = 'Hai Bill, this is an Email!'

Message.send()
