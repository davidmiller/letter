import letter

class Message(letter.Letter):
    Postie  = letter.DjangoPostman()

    From     = 'bill@example.com'
    To       = 'larry@example.com'
    Subject  = 'My Cool mail'

    Template = 'email/some_email'
    Context  = {
        'href': 'http://example.com',
        'link': 'Examples!',
        }

Message.send()
