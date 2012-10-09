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

import ffs
from ffs.contrib import mold
import jinja2
import mailtools
import regex

__all__ = [
    '__version__',
    'Postman'
    ]

u = unicode
flatten = lambda x: [item for sublist in x for item in sublist]

class Error(Exception): pass
class NoTemplateError(Error): pass

class Postman(object):
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
        if isinstance(templatedir, list):
            self.tpls = [ffs.Path(t) for t in templatedir]
        else:
            self.tpls = [ffs.Path(templatedir)]

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

    def _find_tpl(self, name):
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
            contents = [f for f in loc.ls() if f.find(name) != -1 and f.endswith('.jinja2')]
            if contents:
                found = contents[0]
                break
        return found


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

