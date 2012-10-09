"""
Unittests for the letter packate
"""
import sys
import unittest

import mailtools
from mock import MagicMock, patch

if sys.version_info <  (2, 7): import unittest2 as unittest

import letter

class PostmanTestCase(unittest.TestCase):

    def setUp(self):
        self.p = letter.Postman('foo', 'localhost')

    def test_init(self):
        "Set up state please"
        postie = letter.Postman(['foo'], 'localhost')
        self.assertIsInstance(postie.mailer, mailtools.ThreadedMailer)
        self.assertEqual(['foo'], postie.tpls)

    def test_blocking(self):
        "Set up blocking mailer"
        postie = letter.Postman('foo', 'localhost', blocking = True)
        self.assertIsInstance(postie.mailer, mailtools.SMTPMailer)
        self.assertEqual(['foo'], postie.tpls)

    def test_send(self):
        "Send the mail already!"
        with patch.object(self.p.mailer, 'send_plain') as psend:
            self.p.send(u'from@example.com',
                        u'to@example.com',
                        u'This is a mail',
                        u'Hai, kthxbai')
            psend.assert_called_once_with(u'from@example.com',
                                          [u'to@example.com'],
                                          u'This is a mail',
                                          u'Hai, kthxbai')

    def test_send_list(self):
        "Send the mail already!"
        with patch.object(self.p.mailer, 'send_plain') as psend:
            self.p.send(u'from@example.com',
                        [u'to@example.com'],
                        u'This is a mail',
                        u'Hai, kthxbai')
            psend.assert_called_once_with(u'from@example.com',
                                          [u'to@example.com'],
                                          u'This is a mail',
                                          u'Hai, kthxbai')


    def test_send_str(self):
        "Send the mail already!"
        with patch.object(self.p.mailer, 'send_plain') as psend:
            self.p.send('from@example.com',
                        'to@example.com',
                        'This is a mail',
                        'Hai, kthxbai')
            psend.assert_called_once_with(u'from@example.com',
                                          [u'to@example.com'],
                                          u'This is a mail',
                                          u'Hai, kthxbai')
            for arg in psend.call_args[0]:
                if isinstance(arg, list):
                    self.assertTrue(all([isinstance(x, unicode) for x in arg]))
                else:
                    self.assertIsInstance(arg, unicode)

    def test_find_tpl(self):
        "Find a template"
        mockpath = MagicMock(name='MockPath')
        mockpath.ls.return_value = ['that.jinja2']
        self.p.tpls = [mockpath]
        tpl = self.p._find_tpl('that')
        self.assertEqual('that.jinja2', tpl)

    def test_find_no_tpl(self):
        "Find a template"
        mockpath = MagicMock(name='MockPath')
        mockpath.ls.return_value = []
        self.p.tpls = [mockpath]
        tpl = self.p._find_tpl('that')
        self.assertEqual(None, tpl)


    def test_send_tpl(self):
        "Send with a template"
        tplcontents = '{{greeting}}, {{farewell}}'
        mockpath = MagicMock(name='MockPath')
        mockpath.ls.return_value = ['that.jinja2']
        self.p.tpls = [mockpath]
        with patch.object(self.p.mailer, 'send_plain') as psend:
            with self.p.template('that'):
                self.assertEqual(self.p._activetpl, 'that.jinja2')

                self.p._activetpl = MagicMock(name='mocktemplatepath')
                self.p._activetpl.contents = tplcontents

                self.p.send(u'from@example.com',
                            [u'to@example.com'],
                            u'This is a mail',
                            greeting='Hai', farewell = 'kthxbai')

            psend.assert_called_once_with(u'from@example.com',
                                          [u'to@example.com'],
                                          u'This is a mail',
                                          u'Hai, kthxbai')

    def test_send_tpl_raises(self):
        "No template"
        with patch.object(self.p, '_find_tpl') as pfind:
            pfind.return_value = None
            with self.assertRaises(letter.NoTemplateError):
                with self.p.template('sometpl'):
                    pass #Should never get here.


if __name__ == '__main__':
    unittest.main()

