"""
Commandline module interface.
"""
import argparse
import getpass
import sys

import letter

def main():
    """
    Do the things!


    Return: 0
    Exceptions:
    """
    description = 'Letter - a commandline interface'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--gmail', action='store_true', help='Send via Gmail', )
    args = parser.parse_args()

    to       = raw_input('To address > ')
    subject  = raw_input('Subject > ')
    body     = raw_input('Your Message > ')


    if args.gmail:
        user = fromaddr = raw_input('Gmail Address > ')
        pw   = getpass.getpass()
        postie = letter.GmailPostman(user=user, pw=pw)
    else:
        postie = letter.Postman() # Unauthorized SMTP, localhost:25
        fromaddr = raw_input('From address > ')

    class Message(letter.Letter):
        Postie     = postie

        From       = fromaddr
        To         = to
        Subject    = subject
        Body       = body

    return 0


if __name__ == '__main__':
    sys.exit(main())
