"""
Django utilities for use with letter.

Contact Form/View being the frist of these.
"""
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.views.generic.edit import FormView
from six import u

try:
    from captcha.fields import ReCaptchaField
except ImportError:
    ReCaptchaField = lambda: None


class EmailForm(forms.Form):
    name    = forms.CharField()
    email   = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self, to):
        """
        Do work.
        """
        body = self.body()
        subject = self.subject()

        import letter

        class Message(letter.Letter):
            Postie = letter.DjangoPostman()

            From    = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@example.com')
            To      = to
            Subject = subject
            Body    = body

        if hasattr(self, 'reply_to'):
            Message.ReplyTo = self.reply_to()

        Message.send()
        return


class ContactForm(EmailForm):
    """"
    Mailto links are awzm.
    """
    def body(self):
        return u"Contact-form from: {0}\n\n{1}".format(
            u'{0} <{1}>'.format(
                u(self.cleaned_data.get('name', '')),
                u(self.cleaned_data.get('email', ''))),
            u(self.cleaned_data.get('message', '')))

    def subject(self):
        site = Site.objects.get_current()
        return '{0} - Contact Form'.format(site.domain)


class ReCaptchaContactForm(ContactForm):
    """
    Contact form with a Captcha field.
    Requires:

    - django-recaptcha installation
    - setting RECAPTCHA_PRIVATE_KEY
    - setting RECAPTCHA_PUBLIC_KEY
    """
    captcha = ReCaptchaField()


class EmailView(FormView):
    """
    Base class for views that will send an email.

    Subclasses should specify the following properties:
    * template_name
    * form_class
    * success_url
    """
    to_addr       = getattr(settings, 'CONTACT_EMAIL',      'contact@example.com')

    def form_valid(self, form):
        """
        Praise be, someone has spammed us.
        """
        form.send_email(to=self.to_addr)
        return super(EmailView, self).form_valid(form)


class ContactView(EmailView):
    """
    Pointless form for people who don't like their email clients

    Please add a success url!
    Please add the setting CONTACT_EMAIL
    Please add the setting DEFAULT_FROM_EMAIL
    """
    template_name = 'contact.html'
    form_class    = ContactForm
