"""
Send letters electronically.

We assume you're likely to want to send emails from templates.
Let's make that as easy as possible.

Let's do as little as possible.

If you don't want easy template integration, then you probably just want to use
mailtools. Look that up instead :)
"""
from _version import __version__

import contextlib
import types

import ffs
from ffs.contrib import mold
import jinja2
import mailtools
import regex

__all__ = [
    '__version__',
    'Postman',
    'DjangoPostman',
    ]

u = unicode
flatten = lambda x: [item for sublist in x for item in sublist]

class Error(Exception): pass
class NoTemplateError(Error): pass


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


class Postman(BasePostman):
    """
    The Postman is your main entrypoint to sending Electronic Mail.

    Set up an SMTP mailer at HOST:PORT using TEMPLATEDIR as the place
    to look for templates.

    If TRANSPORT_ARGS is passed, pass through these arguments to the
    mail transport.

    If BLOCKING is True, use the blocking mailer.

    Arguments:
    - `templatedir`: str
    - `host`: str
    - `port`: int
    - `transport_args`: dict
    - `blocking`: bool

    Return: None
    Exceptions: None
    """

    def __init__(self, templatedir, host, port=25, transport_args={}, blocking=False):
        self.mailer = mailtools.SMTPMailer(host, port=port, transport_args=transport_args)
        if not blocking:
            self.mailer = mailtools.ThreadedMailer(self.mailer)
        super(BasePostman, self).__init__(templatedir)

    def _send(self, sender, to, subject, message):
        """
        Send a Letter (MESSAGE) from SENDER to TO, with the subject SUBJECT

        Arguments:
        - `sender`: unicode
        - `to`: unicode
        - `subject`: unicode
        - `message`: unicode

        Return: None
        Exceptions: None
        """
        tolist = isinstance(to, list) and [u(x) for x in to] or [u(to)]
        sender, subject, message = u(sender), u(subject), u(message)
        self.mailer.send_plain(sender, tolist, subject, message)
        return

    send = _send

    def _sendtpl(self, sender, to, subject, **kwargs):
        """
        Send a Letter from SENDER to TO, with the subject SUBJECT.
        Use the current template, with KWARGS as the context.

        Arguments:
        - `sender`: unicode
        - `to`: unicode
        - `subject`: unicode
        - `**kwargs`: objects

        Return: None
        Exceptions: None
        """
        message = mold.cast(self._activetpl, **kwargs)
        self._send(sender, to, subject, message)
        return

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
        tpl = self._find_tpl(name)
        if tpl is None:
            raise NoTemplateError(name)
        try:
            self._activetpl = tpl
            self.send = self._sendtpl
            yield
        finally:
            self._activetpl = None
            self.send = self._send


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


    @contextlib.contextmanager
    def template(self, name):
        """
        Set the active template for use with our postman.
        If a Message class is defined, send it.

        Arguments:
        - `name`: str

        Return: None
        Exceptions: NoTemplateError
        """
        try:
            self.plain, self.html = self._find_tpls(name)
            yield
        except:
            raise
        finally:
            self.plain, self.html = None, None
            pass

    def send(self, from_email, to_email, subject, **kwargs):
        """
        Actually send the mail, via Django's interface

        Arguments:
        - `from_email`: str
        - `to_email`: list
        - `subject`: str
        - `kwargs`:

        Return: None
        Exceptions: None
        """
        # This comes straight from the docs at
        # https://docs.djangoproject.com/en/dev/topics/email/
        from django.core.mail import EmailMultiAlternatives

        text_content, html_content = '', ''
        if self.plain:
            text_content = mold.cast(self.plain, **kwargs)
        if self.html:
            html_content = mold.cast(self.html, **kwargs)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return



class Letter(object):
    """
    An individual Letter
    """
    @classmethod
    def send(klass):
        to = klass.To
        if isinstance(to, types.StringTypes):
            to = [to]
        with klass.Postie.template(klass.Template):
            klass.Postie.send(
                klass.From,
                to,
                klass.Subject,
                **klass.Context
                )
