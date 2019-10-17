from __future__ import absolute_import

from mailer.enums import PRIORITY_MAPPING

VERSION = (0, 7, 2)  # following PEP 386


__version__ = '0.7.2'


def get_priority(priority):
    from mailer.enums import PRIORITY_MAPPING, PRIORITY_MEDIUM

    if priority is None:
        priority = PRIORITY_MEDIUM

    if priority in PRIORITY_MAPPING:
        priority = PRIORITY_MAPPING[priority]

    if priority not in PRIORITY_MAPPING.values():
        raise ValueError("Invalid priority {0}".format(repr(priority)))
    return priority


def _add_attachments(msg, attachments=None):
    from mailer.models import Attachment

    if attachments:
        for attachment in attachments:
            filename, content, mimetype = attachment
            Attachment.objects.from_content(msg, filename, content, mimetype)

    msg.ready_to_send = True
    msg.save()


def send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    priority="medium",
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    html_body="",
    attachments=None
):
    """
    Puts a new email on the queue.
    See the documentation for django.core.mail.send_mail for more information
    on the basic options.

    You can add attachments by passing a list of tuples to the attachments
    keyword argument. The tuples must have the following structure:
    (filename, bytes, mimetype or None)
    e.g.
    ('filename.txt', 'raw bytestring', 'application/octet-stream')
    """
    from django.conf import settings
    from django.utils.encoding import force_text
    from mailer.models import Message

    # need to do this in case subject used lazy version of ugettext
    subject = force_text(subject)
    message = force_text(message)
    priority = get_priority(priority)

    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    for to_address in recipient_list:
        msg = Message(
            to_address=to_address,
            from_address=from_email,
            subject=subject,
            message_body=message,
            html_body=html_body,
            priority=priority,
            ready_to_send=False
        )
        msg.save()
        _add_attachments(msg, attachments)


def mail_admins(
    subject,
    message,
    fail_silently=False,
    priority="medium",
    attachments=None
):
    from django.utils.encoding import force_text
    from django.conf import settings
    from mailer.models import Message

    priority = get_priority(priority)
    for name, to_address in settings.ADMINS:
        msg = Message(
            to_address=to_address,
            from_address=settings.SERVER_EMAIL,
            subject=settings.EMAIL_SUBJECT_PREFIX + force_text(subject),
            message_body=force_text(message),
            priority=priority,
            ready_to_send=False
        )
        msg.save()
        _add_attachments(msg, attachments)


def mail_managers(
    subject,
    message,
    fail_silently=False,
    priority="medium",
    attachments=None
):
    from django.utils.encoding import force_text
    from django.conf import settings
    from mailer.models import Message

    priority = get_priority(priority)
    for name, to_address in settings.MANAGERS:
        msg = Message(
            to_address=to_address,
            from_address=settings.SERVER_EMAIL,
            subject=settings.EMAIL_SUBJECT_PREFIX + force_text(subject),
            message_body=force_text(message),
            priority=priority,
            ready_to_send=False
        )
        msg.save()
        _add_attachments(msg, attachments)
