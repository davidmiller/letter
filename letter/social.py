"""
Sending messages on Social media services with letter.
"""
import collections

import tweepy

from letter import Error

__all__ = [
    'AccountNotFoundError',
    'TweetTooLongError',
    'TwitterAccount',
    'TwitterPostie',
    'Tweet'
    ]

class AccountNotFoundError(Error): pass
class TweetTooLongError(Error): pass
TwitterAccount = collections.namedtuple('TwitterAccount',
                                        'access_token access_token_secret')

class TwitterPostie(object):
    """
    Deliver messages via twitter
    """
    def __init__(self, consumer_key='', consumer_secret='', accounts={}):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.accounts = accounts

    def send(self, to, from_, body, dm=False):
        """
        Send BODY as an @message from FROM to TO

        If we don't have the access tokens for FROM, raise AccountNotFoundError.
        If the tweet resulting from '@{0} {1}'.format(TO, BODY) is > 140 chars
        raise TweetTooLongError.

        If we want to send this message as a DM, do so.

        Arguments:
        - `to`: str
        - `from_`: str
        - `body`: str
        - `dm`: [optional] bool

        Return: None
        Exceptions: AccountNotFoundError
                    TweetTooLongError
        """
        tweet = '@{0} {1}'.format(to, body)

        if from_ not in self.accounts:
            raise AccountNotFoundError()
        if len(tweet) > 140:
            raise TweetTooLongError()

        self.auth.set_access_token(*self.accounts.get(from_))
        api = tweepy.API(self.auth)
        if dm:
            api.send_direct_message(screen_name=to, text=body)
        else:
            api.update_status(tweet)
        return


class Tweet(object):
    """
    The top level API for sending tweets
    """
    @classmethod
    def send(klass):
        dm = getattr(klass, 'DM', False)
        klass.Postie.send(klass.To, klass.From, klass.Body, dm=dm)


