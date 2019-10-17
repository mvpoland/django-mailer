from django.core.management.base import BaseCommand
from mailer.models import Message

from logging import getLogger

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Attempt to resend any deferred mail.'

    def handle(self, **options):
        count = Message.objects.retry_deferred()
        logger.info("%s message(s) retried" % count)
