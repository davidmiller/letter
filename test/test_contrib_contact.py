"""
Unittests for the letter.contrib.contact module
"""
import sys
import unittest

from mock import MagicMock, patch
from django.test import utils, TestCase

if sys.version_info <  (2, 7): import unittest2 as unittest

import letter
from letter.contrib import contact


def setup_module():
    utils.setup_test_environment()

def teardown_module():
    utils.teardown_test_environment()


class ContactFormTestCase(TestCase):

    def test_send_email(self):
        "Send an email"
        form = contact.ContactForm()
        form.cleaned_data = {}
        with patch.object(letter.Letter, 'send') as psend:
            with patch.object(contact.Site.objects, 'get_current') as psite:
                psite.domain = 'example.com'
                form.send_email('bill@example.com')
                psend.assert_called_once_with()



if __name__ == '__main__':
    unittest.main()
