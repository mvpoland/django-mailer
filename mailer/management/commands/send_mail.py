from optparse import make_option

from django.core.management.base import NoArgsCommand

from mailer.engine import send_all


class Command(NoArgsCommand):
    help = 'Do one pass through the mail queue, attempting to send all mail.'

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--limit', '-l',
            dest='limit',
            action='store',
            help='The maximum number of mails to send.'
        ),
        make_option(
            '--no-lock', '-n',
            dest='use_locking',
            action='store_false',
            default=True,
            help='Do not use local mailer lock.'
        ),
    )

    def handle_noargs(self, **options):
        send_all(limit=options['limit'], use_locking=options['use_locking'])
