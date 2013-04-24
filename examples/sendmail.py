
import letter

class Message(letter.Letter):
    Postie = letter.Postman()

    From    = 'larry@example.com'
    To      = 'david@deadpansincerity.com'
    Subject = 'Easy Emails'
    Body    = 'Hai David, this is an Email!'

Message.send()
