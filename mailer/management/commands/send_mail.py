from optparse import make_option
from smtplib import SMTPException

from django.core.management.base import NoArgsCommand

from mailer.engine import send_all
from mailer.exceptions import TimeoutError

class Command(NoArgsCommand):
    help = 'Do one pass through the mail queue, attempting to send all mail.'

    option_list = NoArgsCommand.option_list + (
        make_option('--limit', '-l', dest='limit', action='store', help='The maximum number of mails to send.'),
        make_option('--timeout', '-t', dest='timeout', type='int', action='store', help='A timeout in seconds for the send function. An error will be raised if it takes longer.'),
    )

    def handle_noargs(self, **options):
        try:
            send_all(limit=options['limit'], timeout=options['timeout'])
        except (TimeoutError, SMTPException):
            pass
