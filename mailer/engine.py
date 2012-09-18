import time
import smtplib
import logging
from lockfile import FileLock, AlreadyLocked, LockTimeout
from socket import error as socket_error

from mailer.models import Message, DontSendEntry, MessageLog

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

# when queue is empty, how long to wait (in seconds) before checking again
EMPTY_QUEUE_SLEEP = getattr(settings, "MAILER_EMPTY_QUEUE_SLEEP", 30)

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "MAILER_LOCK_WAIT_TIMEOUT", -1)


# Only send emails to these addresses. Should be an iterable of compiled regexes.
# Allow all if None.
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


def send_all():
    """
    Send all eligible messages in the queue.
    """

    lock = FileLock("send_mail")

    logging.debug("acquiring lock...")
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logging.debug("lock already in place. quitting.")
        return
    except LockTimeout:
        logging.debug("waiting for the lock timed out. quitting.")
        return
    logging.debug("acquired.")

    start_time = time.time()

    dont_send = 0
    deferred = 0
    sent = 0

    try:
        for message in prioritize():
            if DontSendEntry.objects.has_address(message.to_address) or not in_whitelist(message.to_address):
                logging.info("skipping email to %s as on don't send list " % message.to_address)
                MessageLog.objects.log(message, 2) # @@@ avoid using literal result code
                message.delete()
                dont_send += 1
            else:
                try:
                    logging.info("sending message '%s' to %s" % (message.subject.encode("utf-8"), message.to_address.encode("utf-8")))

                    # prepare email
                    if message.html_body:
                        logging.info("sending message as HTML message")
                        msg = EmailMultiAlternatives(message.subject, message.message_body, message.from_address, [message.to_address])
                        msg.attach_alternative(message.html_body, 'text/html')
                    else:
                        msg = EmailMessage(message.subject, message.message_body, message.from_address, [message.to_address])

                    # attach attachments
                    for attachment in message.attachment_set.all():
                        mimetype = attachment.mimetype or 'application/octet-stream'
                        msg.attach(attachment.filename, attachment.attachment_file.read(), mimetype)

                    msg.send()
                except (socket_error,
                        UnicodeEncodeError,
                        smtplib.SMTPSenderRefused,
                        smtplib.SMTPRecipientsRefused,
                        smtplib.SMTPAuthenticationError,
                        smtplib.SMTPDataError), err:
                    message.defer()
                    logging.info("message deferred due to failure: %s" % err)
                    MessageLog.objects.log(message, 3, log_message=str(err)) # @@@ avoid using literal result code
                    deferred += 1
                else:
                    MessageLog.objects.log(message, 1) # @@@ avoid using literal result code
                    message.delete()
                    sent += 1
    finally:
        logging.debug("releasing lock...")
        lock.release()
        logging.debug("released.")

    logging.info("")
    logging.info("%s sent; %s deferred; %s don't send" % (sent, deferred, dont_send))
    logging.info("done in %.2f seconds" % (time.time() - start_time))

def send_loop():
    """
    Loop indefinitely, checking queue at intervals of EMPTY_QUEUE_SLEEP and
    sending messages if any are on queue.
    """

    while True:
        while not Message.objects.all():
            logging.debug("sleeping for %s seconds before checking queue again" % EMPTY_QUEUE_SLEEP)
            time.sleep(EMPTY_QUEUE_SLEEP)
        send_all()
