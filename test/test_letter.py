"""
Unittests for the letter packate
"""
import sys
import unittest

from django.core import mail
from django.test import utils, TestCase
import ffs
import mailtools
from mock import MagicMock, patch

if sys.version_info <  (2, 7): import unittest2 as unittest

import letter


def setup_module():
    utils.setup_test_environment()

def teardown_module():
    utils.teardown_test_environment()


class BaseMailerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tolist(self):
        "Should be list of unicodes"
        cases = [
            ('hai',          u'hai'),
            (['hai', 'bai'], u'hai, bai')
            ]
        mailer = letter.BaseMailer()
        for case, expected in cases:
            self.assertEqual(expected, mailer.tolist(case))

    def test_sanity_check_plain(self):
        "Should raise if"
        mailer = letter.BaseMailer()
        resp = mailer.sanity_check(None, None, None, plain='this')
        self.assertEqual(None, resp)

    def test_sanity_check_html(self):
        "Should raise if"
        mailer = letter.BaseMailer()
        resp = mailer.sanity_check(None, None, None, html='this')
        self.assertEqual(None, resp)

    def test_sanity_check_plain_and_html(self):
        "Should raise if"
        mailer = letter.BaseMailer()
        resp = mailer.sanity_check(None, None, None, plain='this', html='that')
        self.assertEqual(None, resp)

    def test_sanity_check_none(self):
        "should raise"
        mailer = letter.BaseMailer()
        with self.assertRaises(letter.NoContentError):
            mailer.sanity_check(None, None, None)


class BaseSMTPMailerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_send_no_content(self):
        "Should raise"
        mailer = letter.BaseSMTPMailer()
        with self.assertRaises(letter.NoContentError):
            mailer.send(None, None, None)




class PostmanTestCase(unittest.TestCase):

    def setUp(self):
        self.p = letter.Postman('foo', 'localhost')

    def test_find_tpl(self):
        "Find a template"
        mockpath = MagicMock(name='MockPath')
        mockpath.ls.return_value = ['that.jinja2']
        self.p.tpls = [mockpath]
        tpl = self.p._find_tpl('that')
        self.assertEqual('that.jinja2', tpl)

    def test_find_tpl_no_dir(self):
        "A dir in our path doesn't exist"
        self.p.tpls = [ffs.Path('does/not/exist/at/this/point')]
        tpl = self.p._find_tpl('that')
        self.assertEqual(None, tpl)


class DjangoPostmanTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        mail.outbox = []

    def test_send_multipart(self):
        "Should send"

        class Message(letter.Letter):
            Postie = letter.DjangoPostman()

            To      = 'larry@example.com'
            From    = 'bill@example.com'
            Subject = 'My Cool mail'

            Template = 'emails/cool_email'
            Context = {
                'href': 'http://example.com',
                'link': 'Examples!',
                }

        Message.send()

        # self.assertEqual(1, len(mail.outbox))
        # self.assertEqual('bill@example.com', mail.outbox[0].from_email)




if __name__ == '__main__':
    unittest.main()
