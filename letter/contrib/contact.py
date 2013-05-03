"""
Django utilities for use with letter.

Contact Form/View being the frist of these.
"""
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.views.generic.edit import FormView

class ContactForm(forms.Form):
    """"
    Mailto links are awzm.
    """
    name    = forms.CharField()
    email   = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        """
        Do work.
        """
        site = Site.objects.get_current()

        body = "Contact-form from: {0}\n\n{1}".format(
            '{0} <{1}>'.format(
            self.cleaned_data['name'],
            self.cleaned_data['email']),
            self.cleaned_data['message'])

        import letter

        class Message(letter.Letter):
            Postie = letter.DjangoPostman()

            From    = getattr(settings, 'DEFAULT_FROM_EMAIL', 'contact@example.com')
            To      = getattr(settings, 'CONTACT_EMAIL',      'contact@example.com')
            Subject = '{0} - Contact Form'.format(site.domain)
            Body    = body

        Message.send()

        return


class ContactView(FormView):
    """
    Pointless form for people who don't like their email clients

    Please add a success url!
    Please add the setting CONTACT_EMAIL
    Please add the setting DEFAULT_FROM_EMAIL
    """
    template_name = 'contact.html'
    form_class    = ContactForm

    def form_valid(self, form):
        """
        Praise be, someone has spammed us.
        """
        form.send_email()
        return super(ContactView, self).form_valid(form)
