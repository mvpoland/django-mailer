from optparse import make_option

from django.core.management.base import BaseCommand

from mailer.engine import send_all


class Command(BaseCommand):
    help = "Do one pass through the mail queue, attempting to send all mail."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            "-l",
            dest="limit",
            action="store",
            help="The maximum number of mails to send.",
        )
        parser.add_argument(
            "--no-lock",
            "-n",
            dest="use_locking",
            action="store_false",
            default=True,
            help="Do not use local mailer lock.",
        )

    def handle(self, **options):
        send_all(limit=options["limit"], use_locking=options["use_locking"])
