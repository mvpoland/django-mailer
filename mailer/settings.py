from django.conf import settings


""" Add here dictionary of extra headers pushed forward to django's EmailMultiAlternatives and EmailMessage.

Example:
    to activate click and open action for e-mails sent by Mandrillapp you'll need to define this as follows:

    MAIL_EXTRA_HEADERS = {'X-MC-Track': 'opens,clicks'}

"""
MAILER_EXTRA_HEADERS = getattr(settings, 'MAILER_EXTRA_HEADERS', None)
