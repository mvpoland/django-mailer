"""
This patch is intended to be used with django-mailer, which can
be found at http://github.com/jtauber/django-mailer/tree/master
"""
from django.core import mail


def patch_send_mail():
    from mailer import send_mail

    mail.orig_send_mail = mail.send_mail
    mail.send_mail = send_mail
