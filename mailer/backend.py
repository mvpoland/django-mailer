from django.core.mail.backends.base import BaseEmailBackend

from mailer.models import Message


class DbBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        # allow for a custom batch size
        messages = Message.objects.bulk_create(
            [Message(email=email) for email in email_messages]
        )

        return len(messages)
