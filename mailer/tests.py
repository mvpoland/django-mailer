# coding: utf-8
import smtplib
import mock

from django.core import mail
from django.core.mail.backends.locmem import EmailBackend as LocMemEmailBackend
from django.test import TestCase, override_settings
from django.utils import timezone

import mailer
from mailer import lockfile
from mailer import engine, send_mail
from mailer.enums import (
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_DEFERRED,
)
from mailer.engine import send_all
from mailer.models import DontSendEntry, Message, MessageLog


class FailingMailerEmailBackend(LocMemEmailBackend):
    def send_messages(self, email_messages):
        raise smtplib.SMTPSenderRefused(1, "foo", "foo@foo.com")


class BasicTestCase(TestCase):
    def test_save_to_db(self):
        """
        Test that using send_mail creates a Message object in DB instead, when EMAIL_BACKEND is set.
        """
        self.assertEqual(Message.objects.count(), 0)
        send_mail("Subject ☺", "Body", "sender@example.com", ["recipient@example.com"])
        self.assertEqual(Message.objects.count(), 1)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendingTest(TestCase):
    def setUp(self):
        pass

    def test_mailer_email_backend(self):
        send_mail("Subject ☺", "Body", "sender1@example.com", ["recipient@example.com"])
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

        send_all()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(MessageLog.objects.count(), 1)

    def test_retry_deferred(self):
        with self.settings(EMAIL_BACKEND="mailer.tests.FailingMailerEmailBackend"):
            send_mail(
                "Subject", "Body", "sender2@example.com", ["recipient@example.com"]
            )
            send_all()

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.deferred().count(), 1)
        self.assertEqual(MessageLog.objects.count(), 1)

        # Send emails once again
        engine.send_all()
        self.assertEqual(len(mail.outbox), 0)
        # Should not have sent the deferred ones
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.deferred().count(), 1)

        # Now mark them for retrying
        Message.objects.retry_deferred()
        engine.send_all()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Message.objects.count(), 0)

    def test_mail_admins(self):
        with self.settings(ADMINS=(("Test", "testadmin@example.com"),)):  # noqa
            mailer.mail_admins("Subject", "Admin Body")

            self.assertEqual(Message.objects.count(), 1)
            self.assertEqual(Message.objects.deferred().count(), 0)

            engine.send_all()

            self.assertEqual(Message.objects.count(), 0)
            self.assertEqual(Message.objects.deferred().count(), 0)

            self.assertEqual(len(mail.outbox), 1)
            sent = mail.outbox[0]

            # Default "plain text"
            self.assertEqual(sent.body, "Admin Body")
            self.assertEqual(sent.to, ["testadmin@example.com"])

    def test_mail_managers(self):
        with self.settings(MANAGERS=(("Test", "testmanager@example.com"),)):  # noqa
            mailer.mail_managers("Subject", "Manager Body")

            self.assertEqual(Message.objects.count(), 1)
            self.assertEqual(Message.objects.deferred().count(), 0)

            engine.send_all()

            self.assertEqual(Message.objects.count(), 0)
            self.assertEqual(Message.objects.deferred().count(), 0)

            self.assertEqual(len(mail.outbox), 1)
            sent = mail.outbox[0]

            # Default "plain text"
            self.assertEqual(sent.body, "Manager Body")
            self.assertEqual(sent.to, ["testmanager@example.com"])

    def test_blacklisted_emails(self):
        with self.settings(
            MAILER_EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            obj = DontSendEntry.objects.create(
                to_address="nogo@example.com", when_added=timezone.now()
            )
            self.assertTrue(obj.to_address, "nogo@example.com")

            send_mail("Subject", "GoBody", "send1@example.com", ["go@example.com"])
            send_mail("Subject", "NoGoBody", "send2@example.com", ["nogo@example.com"])

            self.assertEqual(Message.objects.count(), 2)
            self.assertEqual(Message.objects.deferred().count(), 0)

            engine.send_all()

            # All messages are processed
            self.assertEqual(Message.objects.count(), 0)
            self.assertEqual(Message.objects.deferred().count(), 0)

            # but only one should get sent
            self.assertEqual(len(mail.outbox), 1)
            sent = mail.outbox[0]

            # Default "plain text"
            self.assertEqual(sent.body, "GoBody")
            self.assertEqual(sent.to, ["go@example.com"])


class LockLockedTest(TestCase):
    def setUp(self):
        self.patcher_lock = mock.patch.object(
            mailer.lockfile.FileLock, "acquire", side_effect=lockfile.AlreadyLocked
        )
        self.patcher_prio = mock.patch(
            "mailer.engine.prioritize", side_effect=Exception
        )

        self.lock = self.patcher_lock.start()
        self.prio = self.patcher_prio.start()

        self.addCleanup(self.clean_up)

    def clean_up(self):
        self.patcher_lock.stop()
        self.patcher_prio.stop()

    def test(self):
        send_all()
        self.assertTrue(self.lock.called)
        self.lock.assert_called_once_with()
        self.prio.assert_not_called()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PrioritizeTest(TestCase):
    def test_prioritize(self):
        mailer.send_mail(
            "Subject",
            "Body",
            "prio1@example.com",
            ["r@example.com"],
            priority=PRIORITY_HIGH,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio2@example.com",
            ["r@example.com"],
            priority=PRIORITY_MEDIUM,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio3@example.com",
            ["r@example.com"],
            priority=PRIORITY_LOW,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio4@example.com",
            ["r@example.com"],
            priority=PRIORITY_HIGH,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio5@example.com",
            ["r@example.com"],
            priority=PRIORITY_HIGH,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio6@example.com",
            ["r@example.com"],
            priority=PRIORITY_LOW,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio7@example.com",
            ["r@example.com"],
            priority=PRIORITY_LOW,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio8@example.com",
            ["r@example.com"],
            priority=PRIORITY_MEDIUM,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio9@example.com",
            ["r@example.com"],
            priority=PRIORITY_MEDIUM,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio10@example.com",
            ["r@example.com"],
            priority=PRIORITY_LOW,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio11@example.com",
            ["r@example.com"],
            priority=PRIORITY_MEDIUM,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio12@example.com",
            ["r@example.com"],
            priority=PRIORITY_HIGH,
        )
        mailer.send_mail(
            "Subject",
            "Body",
            "prio13@example.com",
            ["r@example.com"],
            priority=PRIORITY_DEFERRED,
        )
        self.assertEqual(Message.objects.count(), 13)
        self.assertEqual(Message.objects.deferred().count(), 1)
        self.assertEqual(Message.objects.non_deferred().count(), 12)

        messages = engine.prioritize()

        # High priority
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio1@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio4@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio5@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio12@example.com")
        msg.delete()

        # Medium priority
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio2@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio8@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio9@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio11@example.com")
        msg.delete()

        # Low priority
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio3@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio6@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio7@example.com")
        msg.delete()
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio10@example.com")
        msg.delete()

        # Add one more mail that should still get delivered
        mailer.send_mail(
            "Subject",
            "Body",
            "prio14@example.com",
            ["r@example.com"],
            priority=PRIORITY_HIGH,
        )
        msg = next(messages)
        self.assertEqual(msg.from_address, "prio14@example.com")
        msg.delete()

        # Ensure nothing else comes up
        self.assertRaises(StopIteration, lambda: next(messages))

        # Ensure deferred was not deleted
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.deferred().count(), 1)
