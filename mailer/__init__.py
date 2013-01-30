import datetime
import os
import subprocess

def get_git_version():
    git_dir = os.path.abspath(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            '.git'
        )
    )
    try:
        # Python 2.7 has subprocess.check_output
        # 2.6 needs this longer version
        git_info = subprocess.Popen(['git', '--git-dir=%s' % git_dir, 'log', '--pretty=%ct %h', '-1'], stdout=subprocess.PIPE).communicate()[0].split()
        git_time = datetime.datetime.fromtimestamp(float(git_info[0]))
    except Exception:
        git_time = datetime.datetime.now()
        git_info = ('', '0000000')
    return git_time.strftime('%Y.%m.%d') + '.' + git_info[1]

__version__ = get_git_version()
VERSION = __version__

from mailer.enums import PRIORITY_MAPPING

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
    from django.conf import settings
    from django.utils.encoding import force_unicode
    from mailer.models import Message
    # need to do this in case subject used lazy version of ugettext
    subject = force_unicode(subject)
    priority = PRIORITY_MAPPING[priority]
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
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
