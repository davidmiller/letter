
import ffs
import letter

here = ffs.Path(__file__).parent

class Message(letter.Letter):
    Postie = letter.Postman(templatedir=here)

    From     = 'larry@example.com'
    To       = 'david@deadpansincerity.com'
    Subject  = 'Easy Templated Emails'
    Template = 'cool_email'
    Context  = {
        'href': 'http://www.example.com',
        'link': 'Exemplary'
        }

Message.send()
