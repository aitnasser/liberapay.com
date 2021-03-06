from __future__ import print_function, unicode_literals

from dependency_injection import resolve_dependencies
from pando import Response

from .constants import DONATION_LIMITS, PASSWORD_MIN_SIZE, PASSWORD_MAX_SIZE


class Redirect(Exception):
    def __init__(self, url):
        self.url = url


class LazyResponse(Response):

    def __init__(self, code, lazy_body, **kw):
        Response.__init__(self, code, '', **kw)
        self.lazy_body = lazy_body

    def render_body(self, state):
        f = self.lazy_body
        self.body = f(*resolve_dependencies(f, state).as_args)


class AuthRequired(LazyResponse):

    def __init__(self):
        Response.__init__(self, 403, '')
        self.html_template = 'templates/auth-required.html'

    def lazy_body(self, _):
        return _("You need to sign in first")


class LoginRequired(LazyResponse):

    def __init__(self):
        Response.__init__(self, 403, '')
        self.html_template = 'templates/log-in-required.html'

    def lazy_body(self, _):
        return _("You need to log in")


class NeedDatabase(LazyResponse):

    def __init__(self):
        Response.__init__(self, 503, '')
        self.html_template = 'templates/no-db.html'

    def lazy_body(self, _):
        return _("We're unable to process your request right now, sorry.")


class LazyResponseXXX(LazyResponse):

    def __init__(self, *args, **kw):
        Response.__init__(self, self.code, '', **kw)
        self.lazy_body = self.msg
        self.args = args

    # https://github.com/liberapay/liberapay.com/issues/365
    # __str__ = Exception.__str__


class LazyResponse400(LazyResponseXXX):
    code = 400


class ProblemChangingUsername(LazyResponse400): pass

class UsernameIsEmpty(ProblemChangingUsername):
    def msg(self, _):
        return _("You need to provide a username!")

class UsernameTooLong(ProblemChangingUsername):
    def msg(self, _):
        return _("The username '{0}' is too long.", *self.args)

class UsernameContainsInvalidCharacters(ProblemChangingUsername):
    def msg(self, _):
        return _("The username '{0}' contains invalid characters.", *self.args)

class UsernameIsRestricted(ProblemChangingUsername):
    def msg(self, _):
        return _("The username '{0}' is restricted.", *self.args)

class UsernameAlreadyTaken(ProblemChangingUsername):
    def msg(self, _):
        return _("The username '{0}' is already taken.", *self.args)


class ProblemChangingEmail(LazyResponse400): pass

class EmailAlreadyTaken(ProblemChangingEmail):
    def msg(self, _):
        return _("{0} is already connected to a different Liberapay account.", *self.args)

class CannotRemovePrimaryEmail(ProblemChangingEmail):
    def msg(self, _):
        return _("You cannot remove your primary email address.")

class EmailNotVerified(ProblemChangingEmail):
    def msg(self, _):
        return _("The email address '{0}' is not verified.", *self.args)

class TooManyEmailAddresses(ProblemChangingEmail):
    def msg(self, _):
        return _("You've reached the maximum number of email addresses we allow.")

class BadEmailAddress(ProblemChangingEmail):
    def msg(self, _):
        return _("'{0}' is not a valid email address.", *self.args)


class BadPasswordSize(LazyResponse400):
    def msg(self, _):
        return _("The password must be at least {0} and at most {1} characters long.",
                 PASSWORD_MIN_SIZE, PASSWORD_MAX_SIZE)


class NoSelfTipping(LazyResponse400):
    def msg(self, _):
        return _("You can't donate to yourself.")

class NoTippee(LazyResponse400):
    def msg(self, _):
        return _("There is no user named {0}.", *self.args)

_ = lambda a: a
BAD_AMOUNT_MESSAGES = {
    'weekly': _("'{0}' is not a valid weekly donation amount (min={1}, max={2})"),
    'monthly': _("'{0}' is not a valid monthly donation amount (min={1}, max={2})"),
    'yearly': _("'{0}' is not a valid yearly donation amount (min={1}, max={2})"),
}
del _

class BadAmount(LazyResponse400):
    def msg(self, _):
        period = self.args[1]
        return _(BAD_AMOUNT_MESSAGES[period], self.args[0], *DONATION_LIMITS[period])

class UserDoesntAcceptTips(LazyResponse400):
    def msg(self, _):
        return _("The user {0} doesn't accept donations.", *self.args)


class NonexistingElsewhere(LazyResponse400):
    def msg(self, _):
        return _("It seems you're trying to delete something that doesn't exist.")


class NegativeBalance(LazyResponse400):
    def msg(self, _):
        return _("There isn't enough money in your wallet.")


class NotEnoughWithdrawableMoney(LazyResponse400):
    def msg(self, _):
        return _("You can't withdraw more than {0} at this time.", *self.args)


class FeeExceedsAmount(LazyResponse400):
    def msg(self, _):
        return _("The transaction's fee would exceed its amount.")


class TransactionFeeTooHigh(Exception): pass


class PaydayIsRunning(LazyResponseXXX):
    code = 503

    def msg(self, _):
        return _(
            "Sorry, we're running payday right now, and we're not set up to do "
            "payouts while payday is running. Please check back in a few hours."
        )


class InvalidNumber(LazyResponse400):
    def msg(self, _):
        return _('"{0}" is not a valid number.', *self.args)


class CommunityAlreadyExists(LazyResponse400):
    def msg(self, _):
        return _('The "{0}" community already exists.', *self.args)


class InvalidCommunityName(LazyResponse400):
    def msg(self, _):
        return _('"{0}" is not a valid community name.', *self.args)


class TransferError(LazyResponseXXX):
    code = 500
    def msg(self, _):
        return _(
            "Transferring the money failed, sorry. Please contact support@liberapay.com "
            "if the problem persists. Error message: {0}", *self.args
        )


class AccountSuspended(LazyResponseXXX):
    code = 403
    def msg(self, _):
        return _(
            "You are not allowed to do this because your account is currently "
            "suspended."
        )
