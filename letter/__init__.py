"""
Send letters electronically.

We assume you're likely to want to send emails from templates.
Let's make that as easy as possible.
"""
from _version import __version__

import collections
import contextlib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import itertools
import smtplib
import types

import ffs
from ffs.contrib import mold
import jinja2

__all__ = [
    '__version__',
    'Postman',
    'DjangoPostman',
    'GmailPostman',
    'setup_test_environment',
    'teardown_test_environment'
    ]

u = unicode
flatten = lambda x: [item for sublist in x for item in sublist]
stringy = lambda x: isinstance(x, types.StringTypes)
listy   = lambda x: isinstance(x, (list, tuple))

OUTBOX = []
SMTP   = None

class Error(Exception): pass
class NoTemplateError(Error): pass
class NoContentError(Error): pass

def _stringlist(*args):
    """
    Take a lists of strings or strings and flatten these into
    a list of strings.

    Arguments:
    - `*args`: "" or [""...]

    Return: [""...]
    Exceptions: None
    """
    return list(itertools.chain.from_iterable(itertools.repeat(x,1) if stringy(x) else x for x in args if x))

class BaseMailer(object):
    """
    Mailers either handle the construction and delivery of message
    objects once we have determined the contents etc.
    """

    def tolist(self, to):
        """
        Make sure that our addressees are a unicoded list

        Arguments:
        - `to`: str or list

        Return: [u, ...]
        Exceptions: None
        """
        return ', '.join(isinstance(to, list) and [u(x) for x in to] or [u(to)])

    def send(self, sender, to, subject, plain=None, html=None, cc=None, bcc=None):
        """
        Send the message.

        If we have PLAIN and HTML versions, send a multipart alternative
        MIME message, else send whichever we do have.

        If we have neither, raise NoContentError

        Arguments:
        - `sender`: str
        - `to`: list
        - `subject`: str
        - `plain`: str
        - `html`: str

        Return: None
        Exceptions: NoContentError
        """
        if not plain and not html:
            raise NoContentError()


class BaseSMTPMailer(BaseMailer):
    """
    Construct the message
    """

    def send(self, sender, to, subject, plain=None, html=None, cc=None, bcc=None):
        """
        Send the message.

        If we have PLAIN and HTML versions, send a multipart alternative
        MIME message, else send whichever we do have.

        If we have neither, raise NoContentError

        Arguments:
        - `sender`: str
        - `to`: list
        - `subject`: str
        - `plain`: str
        - `html`: str
        - `cc`: str or [str]
        - `bcc`: str or [str]

        Return: None
        Exceptions: NoContentError
        """
        super(BaseSMTPMailer, self).send(sender, to, subject, plain=plain, html=html)
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = u(subject)
        msg['From']    = u(sender)
        msg['To']      = self.tolist(to)
        msg['Cc']      = self.tolist(cc)

        recipients = _stringlist(to, cc, bcc)

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        if plain:
            msg.attach(MIMEText(u(plain), 'plain'))
        if html:
            msg.attach(MIMEText(u(html), 'html'))

        self.deliver(msg, recipients)


class SMTPMailer(BaseSMTPMailer):
    """
    Use SMTP to deliver our message.
    """

    def __init__(self, host, port):
        """
        Store vars
        """
        self.host = host
        self.port = port

    def deliver(self, message, to):
        """
        Deliver our message

        Arguments:
        - `message`: MIMEMultipart

        Return: None
        Exceptions: None
        """
        # Send the message via local SMTP server.
        s = smtplib.SMTP(self.host, self.port)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.

        s.sendmail(message['From'], to, message.as_string())
        s.quit()
        return


class SMTPAuthenticatedMailer(BaseSMTPMailer):
    """
    Use authenticated SMTP to deliver our message
    """
    def __init__(self, host, port, user, pw):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw


    def deliver(self, message, to):
        """
        Deliver our message

        Arguments:
        - `message`: MIMEMultipart

        Return: None
        Exceptions: None
        """
        # Send the message via local SMTP server.
        s = smtplib.SMTP(self.host, self.port)
        s.ehlo()
        s.starttls()
        s.login(self.user, self.pw)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(message['From'], to, message.as_string())
        s.quit()
        return


class DjangoMailer(BaseMailer):
    """
    Send email using whatever is configured in our Django project's
    email settings etc etc
    """

    def send(self, sender, to, subject, plain=None, html=None, cc=None, bcc=None):
        """
        Send the message.

        If we have PLAIN and HTML versions, send a multipart alternative
        MIME message, else send whichever we do have.

        If we have neither, raise NoContentError

        Arguments:
        - `sender`: str
        - `to`: list
        - `subject`: str
        - `plain`: str
        - `html`: str

        Return: None
        Exceptions: NoContentError
        """
        if cc or bcc:
            raise NotImplementedError('Cc & Bcc not implemented for Django yet!')
        super(DjangoMailer, self).send(self, sender, to, subject, plain=plain, html=html)

        # This comes straight from the docs at
        # https://docs.djangoproject.com/en/dev/topics/email/
        from django.core.mail import EmailMultiAlternatives

        if not plain:
            plain = ''

        msg = EmailMultiAlternatives(u(subject), u(text_content), u(plain), self.tolist(to))

        if html_content:
            msg.attach_alternative(u(html), "text/html")

        msg.send()
        return


class BasePostman(object):
    """
    Implement common postman-esque methods
    """

    def __init__(self, templatedir):
        """
        Set template locations
        """
        if isinstance(templatedir, (list, tuple)):
            self.tpls = [ffs.Path(t) for t in templatedir]
        else:
            self.tpls = [ffs.Path(templatedir)]
        return

    def _find_tpl(self, name, extension='.jinja2'):
        """
        Return a Path object representing the Template we're after,
        searching SELF.tpls or None

        Arguments:
        - `name`: str

        Return: Path or None
        Exceptions: None
        """
        found = None
        for loc in self.tpls:
            if not loc:
                continue
            contents = [f for f in loc.ls() if f.find(name) != -1 and f.endswith(extension)]
            if contents:
                found = contents[0]
                break
            exact = loc + (name + extension)
            if exact.is_file:
                found = exact
        return found

    def _find_tpls(self, name):
        """
        Return plain, html templates for NAME

        Arguments:
        - `name`: str

        Return: tuple
        Exceptions: None
        """
        return self._find_tpl(name, extension='.txt'), self._find_tpl(name, extension='.html')

    def _send(self, sender, to, subject, message, cc=None, bcc=None):
        """
        Send a Letter (MESSAGE) from SENDER to TO, with the subject SUBJECT

        Arguments:
        - `sender`: unicode
        - `to`: unicode
        - `subject`: unicode
        - `message`: unicode
        - `cc`: str or [str]
        - `bcc`: str or [str]

        Return: None
        Exceptions: None
        """
        self.mailer.send(sender, to, subject, plain=message, cc=cc, bcc=bcc)
        return

    send = _send

    def _sendtpl(self, sender, to, subject, cc=None, bcc=None, **kwargs):
        """
        Send a Letter from SENDER to TO, with the subject SUBJECT.
        Use the current template, with KWARGS as the context.

        Arguments:
        - `sender`: unicode
        - `to`: unicode
        - `subject`: unicode
        - `cc`: str or [str]
        - `bcc`: str or [str]
        - `**kwargs`: objects

        Return: None
        Exceptions: None
        """
        # message = mold.cast(self._activetpl, **kwargs)
        # self._send(sender, to, subject, message)
        plain, html = self.body(**kwargs)
        self.mailer.send(sender, to, subject, plain=plain, html=html, cc=cc, bcc=bcc)
        return

    def body(self, **kwargs):
        """
        Return the plain and html versions of our contents.

        Return: tuple
        Exceptions: None
        """
        text_content, html_content = None, None
        if self.plain:
            text_content = mold.cast(self.plain, **kwargs)
        if self.html:
            html_content = mold.cast(self.html, **kwargs)
        return text_content, html_content

    @contextlib.contextmanager
    def template(self, name):
        """
        Set an active template to use with our Postman.

        This changes the call signature of send.

        Arguments:
        - `name`: str

        Return: None
        Exceptions: None
        """
        self.plain, self.html = self._find_tpls(name)
        if not self.plain:
            self.plain = self._find_tpl(name)
        try:
            self.send = self._sendtpl
            yield
        finally:
            self.plain, self.html = None, None
            self.send = self._send


class SMTPPostman(BasePostman):
    """
    The SMTP Postman is a utility class for using SMTP as
    a delivery method for our messages.
    """
    def __init__(self, templatedir=None, host='localhost', port=25):
        super(SMTPPostman, self).__init__(templatedir)
        self.mailer = SMTPMailer(host, port)


class SMTPAuthenticatedPostman(BasePostman):
    """
    The SMTP Postman is a utility class for using SMTP as
    a delivery method for our messages.
    """
    def __init__(self, templatedir=None, host='localhost', port=25, user=None, pw=None):
        super(SMTPAuthenticatedPostman, self).__init__(templatedir)
        self.mailer = SMTPAuthenticatedMailer(host, port, user, pw)


class Postman(SMTPPostman):
    """
    The Postman is your main entrypoint to sending Electronic Mail.

    Set up an SMTP mailer at HOST:PORT using TEMPLATEDIR as the place
    to look for templates.

    If BLOCKING is True, use the blocking mailer.

    Arguments:
    - `templatedir`: str
    - `host`: str
    - `port`: int

    Return: None
    Exceptions: None
    """


class DjangoPostman(BasePostman):
    """
    Postman for use with Django's mail framework.
    """
    def __init__(self):
        """
        Do Django imports...
        """
        self.html, self.plain = None, None
        from django.conf import settings
        from django.utils.functional import empty
        if settings._wrapped is empty:
            settings.configure()
        self.settings = settings
        super(DjangoPostman, self).__init__(settings.TEMPLATE_DIRS)
        self.mailer = DjangoMailer()


class GmailPostman(SMTPAuthenticatedPostman):
    """
    OK, so we're sending emails via Google's SMTP servers.

    >>> postie = GmailPostman('.', user='username', pw='password')
    """
    def __init__(self, templatedir='.', user=None, pw=None):
        super(GmailPostman, self).__init__(templatedir=templatedir,
                                           host='smtp.gmail.com',
                                           port=587,
                                           user=user,
                                           pw=pw)


class Letter(object):
    """
    An individual Letter
    """
    @classmethod
    def send(klass):
        to = klass.To
        if isinstance(to, types.StringTypes):
            to = [to]
        if getattr(klass, 'Body', None):
            klass.Postie.send(
                klass.From,
                to,
                klass.Subject,
                klass.Body,
                cc=getattr(klass, 'Cc', None),
                bcc=getattr(klass, 'Bcc', None),
                )
            return

        with klass.Postie.template(klass.Template):
            klass.Postie.send(
                klass.From,
                to,
                klass.Subject,
                cc=getattr(klass, 'Cc', None),
                bcc=getattr(klass, 'Bcc', None),
                **klass.Context
                )

"""
Testing utilities start here.
"""
def _parse_outgoing_mail(sender, to, msgstring):
    """
    Parse an outgoing mail and put it into the OUTBOX.


    Arguments:
    - `sender`: str
    - `to`: str
    - `msgstring`: str

    Return: None
    Exceptions: None
    """
    global OUTBOX
    OUTBOX.append(email.message_from_string(msgstring))
    return

def setup_test_environment():
    """
    Set up our environment to test the sending of
    email with letter.

    We return an outbox for you, into which all emails
    will be delivered.

    Requires the Mock library.

    Return: list
    Exceptions: None
    """
    import mock
    global OUTBOX, SMTP

    SMTP = smtplib.SMTP
    mock_smtp = mock.MagicMock(name='Mock SMTP')
    mock_smtp.return_value.sendmail.side_effect = _parse_outgoing_mail
    smtplib.SMTP = mock_smtp
    return OUTBOX

def teardown_test_environment():
    """
    Tear down utilities for the testing of mail sent with letter.

    Return: None
    Exceptions: None
    """
    global OUTBOX, SMTP
    smtplib.SMTP = SMTP
    OUTBOX = []
    return
