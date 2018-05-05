__version__ = '0.6.2'

import importlib
import logging

from mailer.enums import PRIORITY_MAPPING

logger = logging.getLogger(__name__)


def _add_attachments(msg, attachments=None):
    from mailer.models import Attachment

    if attachments:
        for attachment in attachments:
            filename, content, mimetype = attachment
            Attachment.objects.from_content(msg, filename, content, mimetype)

    msg.ready_to_send = True
    msg.save()


def send_mail(subject, message, from_email, recipient_list, priority="medium",
              fail_silently=False, auth_user=None, auth_password=None, html_body="",
              attachments=None):
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
    from django.conf import settings as dj_settings
    from django.utils.encoding import force_unicode
    from mailer.models import Message
    from mailer.settings import MAILER_SCHEDULER
    # need to do this in case subject used lazy version of ugettext
    subject = force_unicode(subject)
    priority = PRIORITY_MAPPING[priority]
    if from_email is None:
        from_email = dj_settings.DEFAULT_FROM_EMAIL
    scheduler = None
    if MAILER_SCHEDULER:
        scheduler = load_scheduler(MAILER_SCHEDULER)
    for to_address in recipient_list:
        msg = Message(to_address=to_address,
                      from_address=from_email,
                      subject=subject,
                      message_body=message,
                      html_body=html_body,
                      priority=priority,
                      ready_to_send=False)
        msg.save()
        _add_attachments(msg, attachments)
        if scheduler:
            scheduler.schedule(msg)


def mail_admins(subject, message, fail_silently=False, priority="medium",
                attachments=None):
    from django.utils.encoding import force_unicode
    from django.conf import settings
    from mailer.models import Message
    priority = PRIORITY_MAPPING[priority]
    for name, to_address in settings.ADMINS:
        msg = Message(to_address=to_address,
                      from_address=settings.SERVER_EMAIL,
                      subject=settings.EMAIL_SUBJECT_PREFIX + force_unicode(subject),
                      message_body=message,
                      priority=priority,
                      ready_to_send=False)
        msg.save()
        _add_attachments(msg, attachments)


def mail_managers(subject, message, fail_silently=False, priority="medium",
                  attachments=None):
    from django.utils.encoding import force_unicode
    from django.conf import settings
    from mailer.models import Message
    priority = PRIORITY_MAPPING[priority]
    for name, to_address in settings.MANAGERS:
        msg = Message(to_address=to_address,
                      from_address=settings.SERVER_EMAIL,
                      subject=settings.EMAIL_SUBJECT_PREFIX + force_unicode(subject),
                      message_body=message,
                      priority=priority,
                      ready_to_send=False)
        msg.save()
        _add_attachments(msg, attachments)


def load_scheduler(path):
    """ Import scheduler class from provided path visible within PYTHONPATH.

    Example usage:

        `load_scheduler('my_project.module.BasicCeleryScheduler')`

    """
    try:
        scheduler_path = path.split('.')
        module, classname = '.'.join(scheduler_path[:-1]), scheduler_path[-1]
        module = importlib.import_module(module)
        return getattr(module, classname)()
    except:
        logger.error("Bad scheduler path provided {}".format(path))
