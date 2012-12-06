import logging
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand

from mailer.engine import send_all

# allow a sysadmin to pause the sending of mail temporarily.
PAUSE_SEND = getattr(settings, "MAILER_PAUSE_SEND", False)

class Command(NoArgsCommand):
    help = 'Do one pass through the mail queue, attempting to send all mail.'

    option_list = NoArgsCommand.option_list + (
        make_option('--limit', '-l', dest='limit', action='store', help='The maximum number of mails to send.'),
    )

    def handle_noargs(self, **options):
        # if PAUSE_SEND is turned on don't do anything.
        if not PAUSE_SEND:
            send_all(limit=options['limit'])
        else:
            logging.info("sending is paused, quitting.")
