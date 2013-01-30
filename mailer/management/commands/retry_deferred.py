from django.core.management.base import NoArgsCommand
from mailer.models import Message

from logging import getLogger

logger = getLogger(__name__)

class Command(NoArgsCommand):
    help = 'Attempt to resend any deferred mail.'

    def handle_noargs(self, **options):
        count = Message.objects.retry_deferred()
        logger.info("%s message(s) retried" % count)
