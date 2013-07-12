
import letter
from letter.sms import TwillioPostie, SMS

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = ""
auth_token  = ""

postie = TwillioPostie(sid=account_sid, token=auth_token)

class Message(SMS):

    Postie = postie

    To   = '+447854880889'
    From = '+15005550006'
    Body = 'This is an SMS from Letter!'

Message.send()
