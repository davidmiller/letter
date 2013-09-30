"""
Sending SMS with letter.
"""
import twilio
from twilio.rest import TwilioRestClient

class TwillioPostie(object):
    """
    Render messages from templates and handle deliery.
    """
    def __init__(self, sid=None, token=None):
        self.client = TwilioRestClient(sid, token)

    def send(self, to, from_, body):
        """
        Send BODY to TO from FROM as an SMS!
        """
        try:
            msg = self.client.sms.messages.create(
                body=body,
                to=to,
                from_=from_
                )
            print msg.sid
        except twilio.TwilioRestException as e:
            raise


class SMS(object):
    """
    The top level API for our SMS messages
    """
    @classmethod
    def send(klass):
        klass.Postie.send(klass.To, klass.From, klass.Body)
