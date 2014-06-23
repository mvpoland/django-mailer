import time
import smtplib
from lockfile import FileLock, AlreadyLocked, LockTimeout
from socket import error as socket_error

from django_statsd.clients import statsd

from mailer.enums import RESULT_MAPPING
from mailer.models import Message, DontSendEntry, MessageLog

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

from logging import getLogger

logger = getLogger(__name__)

EMPTY_QUEUE_SLEEP = getattr(settings, "MAILER_EMPTY_QUEUE_SLEEP", 30)

LOCK_WAIT_TIMEOUT = getattr(settings, "MAILER_LOCK_WAIT_TIMEOUT", -1)

WHITELIST = getattr(settings, 'MAILER_WHITELIST', None)

def prioritize():
    """
    Yield the messages in the queue in the order they should be sent.
    """
    while True:
        while Message.objects.high_priority().count():
            for message in Message.objects.high_priority().order_by('when_added'):
                yield message
        while Message.objects.high_priority().count() == 0 and Message.objects.medium_priority().count():
            yield Message.objects.medium_priority().order_by('when_added')[0]
        while Message.objects.high_priority().count() == 0 and Message.objects.medium_priority().count() == 0 and Message.objects.low_priority().count():
            yield Message.objects.low_priority().order_by('when_added')[0]
        if Message.objects.non_deferred().count() == 0:
            break


def in_whitelist(address):
    """
    Test if the given email address is contained in the list of allowed addressees.
    """
    if WHITELIST is None:
        return True
    else:
        return any(regex.search(address) for regex in WHITELIST)


def send_all(limit=None):
    """
    Send all eligible messages in the queue.
    """
    # Get lock so only one process sends at the same time
    lock = FileLock('send_mail')
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logger.info('Already locked.')
        return
    except LockTimeout:
        logger.info('Lock timed out.')
        return

    # Check for multiple mail hosts
    hosts = getattr(settings, 'EMAIL_HOSTS', None)
    if hosts is not None:
        from gargoyle import gargoyle
        for host, config in hosts.items():
            if gargoyle.is_active('mailer-%s' % host):
                settings.EMAIL_HOST = config['host']
                settings.EMAIL_USE_TLS = config['use_tls']
                settings.EMAIL_PORT = config['port']
                settings.EMAIL_HOST_USER = config['user']
                settings.EMAIL_HOST_PASSWORD = config['password']
                break


    # Start sending mails
    total, successes, failures = 0, 0, 0
    try:
        for message in prioritize():
            # Check limit
            if limit is not None and total >= int(limit):
                logger.info('Limit (%s) reached, stopping.' % limit)
                break

            # Check whitelist and don't send list
            if DontSendEntry.objects.has_address(message.to_address) or not in_whitelist(message.to_address):
                logger.info('Skipping mail to %s - on don\'t send list.' % message.to_address)
                MessageLog.objects.log(message, RESULT_MAPPING['don\'t send'])
                message.delete()
            else:
                try:
                    logger.info('Sending message to %s' % message.to_address.encode("utf-8"))
                    # Prepare body
                    if message.html_body:
                        msg = EmailMultiAlternatives(message.subject, message.message_body, message.from_address, [message.to_address])
                        msg.attach_alternative(message.html_body, 'text/html')
                    else:
                        msg = EmailMessage(message.subject, message.message_body, message.from_address, [message.to_address])

                    # Prepare attachments
                    for attachment in message.attachment_set.all():
                        mimetype = attachment.mimetype or 'application/octet-stream'
                        msg.attach(attachment.filename, attachment.attachment_file.read(), mimetype)

                    # Do actual send
                    msg.send()
                except (socket_error,
                        UnicodeEncodeError,
                        smtplib.SMTPSenderRefused,
                        smtplib.SMTPRecipientsRefused,
                        smtplib.SMTPAuthenticationError,
                        smtplib.SMTPDataError), err:
                    # Sending failed, defer message
                    message.defer()
                    logger.info('Message deferred due to failure: %s' % err)
                    MessageLog.objects.log(message, RESULT_MAPPING['failure'], log_message=str(err))
                    failures += 1
                else:
                    # Sending succeeded
                    MessageLog.objects.log(message, RESULT_MAPPING['success'])
                    message.delete()
                    successes += 1
            total += 1
    finally:
        lock.release()
        if successes and failures:
            statsd.gauge('mailer.success_rate', successes / failures)
        else:
            statsd.gauge('mailer.success_rate', 1)


def send_loop():
    """
    Loop indefinitely, checking queue at intervals of EMPTY_QUEUE_SLEEP and
    sending messages if any are on queue.
    """

    while True:
        while Message.objects.count() == 0:
            time.sleep(EMPTY_QUEUE_SLEEP)
        send_all()
